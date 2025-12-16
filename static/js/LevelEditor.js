class LevelEditor {
  constructor(projectData, canvas) {
    this.projectData = projectData;
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.sceneManager = new window.SceneManager();
    this.currentLevel = this.initializeLevel();
    this.setupEventListeners();
    this.loadAssets();
    this.initUI();
    
    this.selectedTool = 'tile';
    this.selectedTile = null;
    this.selectedEntity = null;
    this.isDragging = false;
    this.dragStart = { x: 0, y: 0 };
    this.gridSize = 32;
    this.zoom = 1;
    this.offset = { x: 0, y: 0 };
    this.spawnPoints = [];
    this.entityTemplates = {};
    this.tilePalettes = {};
    this.undoStack = [];
    this.redoStack = [];
  }

  initializeLevel() {
    return {
      id: `level_${Date.now()}`,
      name: 'New Level',
      width: 100,
      height: 100,
      gridSize: this.gridSize,
      backgroundColor: '#1a1a1a',
      layers: [
        {
          id: 'background',
          name: 'Background',
          type: 'tilemap',
          visible: true,
          tiles: Array(this.gridSize * this.gridSize).fill(null)
        },
        {
          id: 'foreground',
          name: 'Foreground',
          type: 'tilemap',
          visible: true,
          tiles: Array(this.gridSize * this.gridSize).fill(null)
        }
      ],
      entities: [],
      spawnPoints: [],
      physics: {
        gravity: 9.8,
        friction: 0.8
      }
    };
  }

  loadAssets() {
    const AssetManager = window.AssetManager || {};
    
    this.tilePalettes = {
      'ground': (AssetManager.getAssetsByType?.('tiles') || []).filter(tile => tile.tags?.includes('ground')),
      'decor': (AssetManager.getAssetsByType?.('tiles') || []).filter(tile => tile.tags?.includes('decor')),
      'walls': (AssetManager.getAssetsByType?.('tiles') || []).filter(tile => tile.tags?.includes('wall'))
    };

    const entityAssets = AssetManager.getAssetsByType?.('sprites') || [];
    entityAssets.forEach(asset => {
      if (asset.tags?.includes('entity')) {
        this.entityTemplates[asset.id] = new window.Entity({
          id: asset.id,
          name: asset.name,
          sprite: asset.data,
          width: 32,
          height: 32,
          tags: asset.tags.filter(t => t !== 'entity')
        });
      }
    });

    const spawnPointTemplate = AssetManager.getAssetById?.('spawn_point_template');
    if (spawnPointTemplate) {
      this.spawnPoints = [];
    }
  }

  initUI() {
    const toolbar = document.createElement('div');
    toolbar.className = 'level-editor-toolbar';
    toolbar.innerHTML = `
      <div class="tool-selector">
        <button data-tool="tile" class="active">🟩 Tile</button>
        <button data-tool="entity">👾 Entity</button>
        <button data-tool="spawn">⭐ Spawn</button>
        <button data-tool="eraser">🗑️ Eraser</button>
      </div>
      <div class="tool-options">
        <div class="tile-palette-selector">
          <select id="tilePalette">
            <option value="ground">Ground Tiles</option>
            <option value="walls">Wall Tiles</option>
            <option value="decor">Decoration</option>
          </select>
        </div>
        <div class="entity-selector">
          <select id="entitySelector">
            <option value="">Select Entity</option>
            ${Object.values(this.entityTemplates).map(entity => 
              `<option value="${entity.id}">${entity.name}</option>`
            ).join('')}
          </select>
        </div>
      </div>
      <div class="level-controls">
        <button id="saveLevel">💾 Save Level</button>
        <button id="loadLevel">📂 Load Level</button>
        <button id="newLevel">🆕 New Level</button>
        <button id="undo">↶ Undo</button>
        <button id="redo">↷ Redo</button>
      </div>
      <div class="view-controls">
        <input type="range" id="zoomSlider" min="0.25" max="4" step="0.25" value="1">
        <span id="zoomDisplay">100%</span>
      </div>
    `;
    document.querySelector('#editor-container')?.prepend(toolbar);

    toolbar.querySelectorAll('.tool-selector button').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tool = e.target.dataset.tool;
        if (tool) this.selectTool(tool);
      });
    });

    toolbar.querySelector('#tilePalette')?.addEventListener('change', (e) => {
      const palette = e.target.value;
      this.renderTilePalette(palette);
    });

    toolbar.querySelector('#entitySelector')?.addEventListener('change', (e) => {
      const entityId = e.target.value;
      this.selectedEntity = entityId || null;
    });

    toolbar.querySelector('#saveLevel')?.addEventListener('click', () => this.saveLevel());
    toolbar.querySelector('#loadLevel')?.addEventListener('click', () => this.loadLevel());
    toolbar.querySelector('#newLevel')?.addEventListener('click', () => this.newLevel());
    toolbar.querySelector('#undo')?.addEventListener('click', () => this.undo());
    toolbar.querySelector('#redo')?.addEventListener('click', () => this.redo());

    toolbar.querySelector('#zoomSlider')?.addEventListener('input', (e) => {
      this.zoom = parseFloat(e.target.value);
      document.getElementById('zoomDisplay').textContent = `${Math.round(this.zoom * 100)}%`;
      this.render();
    });

    const paletteContainer = document.createElement('div');
    paletteContainer.className = 'tile-palette';
    paletteContainer.style.width = '200px';
    paletteContainer.style.position = 'absolute';
    paletteContainer.style.right = '10px';
    paletteContainer.style.top = '60px';
    document.body.appendChild(paletteContainer);
    this.renderTilePalette('ground');

    this.setupCanvas();
  }

  setupCanvas() {
    this.canvas.width = window.innerWidth * 0.7;
    this.canvas.height = window.innerHeight * 0.8;
    
    this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
    
    this.render();
  }

  selectTool(tool) {
    this.selectedTool = tool;
    document.querySelectorAll('.tool-selector button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tool === tool);
    });
    
    document.querySelector('.tile-palette-selector').style.display = 
      tool === 'tile' ? 'block' : 'none';
    document.querySelector('.entity-selector').style.display = 
      tool === 'entity' ? 'block' : 'none';
  }

  renderTilePalette(paletteName) {
    const paletteContainer = document.querySelector('.tile-palette');
    const tiles = this.tilePalettes[paletteName] || [];
    
    paletteContainer.innerHTML = `
      <h3>${paletteName.charAt(0).toUpperCase() + paletteName.slice(1)} Tiles</h3>
      <div class="palette-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px;">
        ${tiles.map(tile => `
          <div class="palette-tile" data-tile-id="${tile.id}" style="
            width: 48px; 
            height: 48px; 
            background-image: url('${tile.data}'); 
            background-size: contain; 
            background-repeat: no-repeat; 
            background-position: center;
            border: 2px solid ${this.selectedTile?.id === tile.id ? '#3498db' : 'transparent'};
            cursor: pointer;
          "></div>
        `).join('')}
      </div>
    `;
    
    paletteContainer.querySelectorAll('.palette-tile').forEach(tileEl => {
      tileEl.addEventListener('click', () => {
        const tileId = tileEl.getAttribute('data-tile-id');
        this.selectedTile = this.tilePalettes[paletteName].find(t => t.id === tileId) || null;
        this.renderTilePalette(paletteName);
      });
    });
  }

  handleMouseDown(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - this.offset.x) / (this.gridSize * this.zoom);
    const y = (e.clientY - rect.top - this.offset.y) / (this.gridSize * this.zoom);
    
    this.isDragging = true;
    this.dragStart = { x, y };
    
    if (this.selectedTool === 'tile' && this.selectedTile) {
      this.placeTile(Math.floor(x), Math.floor(y));
    } else if (this.selectedTool === 'entity' && this.selectedEntity) {
      this.placeEntity(Math.floor(x), Math.floor(y));
    } else if (this.selectedTool === 'spawn') {
      this.placeSpawnPoint(Math.floor(x), Math.floor(y));
    } else if (this.selectedTool === 'eraser') {
      this.eraseAt(Math.floor(x), Math.floor(y));
    }
    
    this.saveUndoState();
  }

  handleMouseMove(e) {
    if (!this.isDragging) return;
    
    const rect = this.canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - this.offset.x) / (this.gridSize * this.zoom);
    const y = (e.clientY - rect.top - this.offset.y) / (this.gridSize * this.zoom);
    
    if (this.selectedTool === 'tile' && this.selectedTile) {
      this.placeTile(Math.floor(x), Math.floor(y));
    } else if (this.selectedTool === 'entity' && this.selectedEntity) {
      this.placeEntity(Math.floor(x), Math.floor(y));
    } else if (this.selectedTool === 'eraser') {
      this.eraseAt(Math.floor(x), Math.floor(y));
    }
    
    this.render();
  }

  handleMouseUp() {
    this.isDragging = false;
  }

  handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    this.zoom = Math.max(0.25, Math.min(4, this.zoom + delta));
    document.getElementById('zoomSlider').value = this.zoom.toString();
    document.getElementById('zoomDisplay').textContent = `${Math.round(this.zoom * 100)}%`;
    this.render();
  }

  placeTile(x, y) {
    const layer = this.currentLevel.layers.find(l => l.id === 'foreground');
    if (!layer || !this.selectedTile) return;
    
    const index = y * this.currentLevel.width + x;
    if (index >= 0 && index < layer.tiles.length) {
      layer.tiles[index] = { id: this.selectedTile.id, x, y };
      this.render();
    }
  }

  placeEntity(x, y) {
    if (!this.selectedEntity) return;
    
    const entity = this.entityTemplates[this.selectedEntity];
    if (!entity) return;
    
    this.currentLevel.entities.push({
      id: `entity_${Date.now()}`,
      entityType: entity.id,
      x: x * this.gridSize + this.gridSize / 2,
      y: y * this.gridSize + this.gridSize / 2,
      width: entity.width,
      height: entity.height
    });
    
    this.render();
  }

  placeSpawnPoint(x, y) {
    this.currentLevel.spawnPoints.push({
      id: `spawn_${Date.now()}`,
      x: x * this.gridSize + this.gridSize / 2,
      y: y * this.gridSize + this.gridSize / 2,
      type: 'player',
      properties: {}
    });
    
    this.render();
  }

  eraseAt(x, y) {
    this.currentLevel.layers.forEach(layer => {
      const index = y * this.currentLevel.width + x;
      if (index >= 0 && index < layer.tiles.length) {
        layer.tiles[index] = null;
      }
    });
    
    this.currentLevel.entities = this.currentLevel.entities.filter(entity => {
      const entityX = Math.floor(entity.x / this.gridSize);
      const entityY = Math.floor(entity.y / this.gridSize);
      return !(entityX === x && entityY === y);
    });
    
    this.currentLevel.spawnPoints = this.currentLevel.spawnPoints.filter(spawn => {
      const spawnX = Math.floor(spawn.x / this.gridSize);
      const spawnY = Math.floor(spawn.y / this.gridSize);
      return !(spawnX === x && spawnY === y);
    });
    
    this.render();
  }

  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.ctx.save();
    this.ctx.translate(this.offset.x, this.offset.y);
    this.ctx.scale(this.zoom, this.zoom);
    
    this.drawGrid();
    this.ctx.fillStyle = this.currentLevel.backgroundColor;
    this.ctx.fillRect(0, 0, this.currentLevel.width * this.gridSize, this.currentLevel.height * this.gridSize);
    
    this.currentLevel.layers.forEach(layer => {
      if (layer.visible && layer.type === 'tilemap') {
        this.drawTileLayer(layer);
      }
    });
    
    this.drawEntities();
    this.drawSpawnPoints();
    this.drawSelectionGrid();
    
    this.ctx.restore();
    this.drawUIOverlay();
  }

  drawGrid() {
    this.ctx.strokeStyle = '#34495e';
    this.ctx.lineWidth = 0.5;
    
    for (let x = 0; x <= this.currentLevel.width; x++) {
      this.ctx.beginPath();
      this.ctx.moveTo(x * this.gridSize, 0);
      this.ctx.lineTo(x * this.gridSize, this.currentLevel.height * this.gridSize);
      this.ctx.stroke();
    }
    
    for (let y = 0; y <= this.currentLevel.height; y++) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y * this.gridSize);
      this.ctx.lineTo(this.currentLevel.width * this.gridSize, y * this.gridSize);
      this.ctx.stroke();
    }
  }

  drawTileLayer(layer) {
    layer.tiles.forEach((tile, index) => {
      if (!tile) return;
      
      const x = index % this.currentLevel.width;
      const y = Math.floor(index / this.currentLevel.width);
      
      const tileDefinition = Object.values(this.tilePalettes).flat().find(t => t.id === tile.id);
      if (tileDefinition) {
        const img = new Image();
        img.src = tileDefinition.data;
        this.ctx.drawImage(img, x * this.gridSize, y * this.gridSize, this.gridSize, this.gridSize);
      }
    });
  }

  drawEntities() {
    this.currentLevel.entities.forEach(entity => {
      const template = this.entityTemplates[entity.entityType];
      if (!template) return;
      
      this.ctx.fillStyle = '#3498db';
      this.ctx.fillRect(entity.x - entity.width / 2, entity.y - entity.height / 2, entity.width, entity.height);
      
      this.ctx.strokeStyle = '#2980b9';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(entity.x - entity.width / 2, entity.y - entity.height / 2, entity.width, entity.height);
      
      this.ctx.fillStyle = '#ecf0f1';
      this.ctx.font = '12px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(template.name, entity.x, entity.y - entity.height / 2 - 5);
    });
  }

  drawSpawnPoints() {
    this.currentLevel.spawnPoints.forEach(spawn => {
      this.ctx.fillStyle = '#27ae60';
      this.ctx.beginPath();
      this.ctx.arc(spawn.x, spawn.y, 15, 0, Math.PI * 2);
      this.ctx.fill();
      
      this.ctx.strokeStyle = '#229954';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
      
      this.ctx.fillStyle = '#ecf0f1';
      this.ctx.font = '10px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('SPAWN', spawn.x, spawn.y + 4);
    });
  }

  drawSelectionGrid() {
    if (this.selectedTool === 'tile' && this.selectedTile) {
      this.ctx.fillStyle = 'rgba(52, 152, 219, 0.3)';
      this.ctx.fillRect(Math.floor(this.dragStart.x) * this.gridSize, Math.floor(this.dragStart.y) * this.gridSize, this.gridSize, this.gridSize);
    }
  }

  drawUIOverlay() {
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    this.ctx.fillStyle = '#ecf0f1';
    this.ctx.font = '14px Arial';
    this.ctx.fillText(`Level: ${this.currentLevel.name} | Grid: ${this.currentLevel.width}x${this.currentLevel.height}`, 10, 25);
    this.ctx.fillText(`Tool: ${this.selectedTool.toUpperCase()}${this.selectedTile ? ` - ${this.selectedTile.name}` : ''}`, 10, 50);
    
    this.ctx.restore();
  }

  saveUndoState() {
    const state = JSON.parse(JSON.stringify(this.currentLevel));
    this.undoStack.push(state);
    
    if (this.undoStack.length > 50) {
      this.undoStack.shift();
    }
    
    this.redoStack = [];
  }

  undo() {
    if (this.undoStack.length === 0) return;
    
    this.redoStack.push(JSON.parse(JSON.stringify(this.currentLevel)));
    this.currentLevel = JSON.parse(JSON.stringify(this.undoStack.pop()));
    this.render();
  }

  redo() {
    if (this.redoStack.length === 0) return;
    
    this.undoStack.push(JSON.parse(JSON.stringify(this.currentLevel)));
    this.currentLevel = JSON.parse(JSON.stringify(this.redoStack.pop()));
    this.render();
  }

  saveLevel() {
    if (this.currentLevel.spawnPoints.length === 0) {
      alert('Level must have at least one spawn point!');
      return;
    }
    
    const levelIndex = this.projectData.levels.findIndex(l => l.id === this.currentLevel.id);
    if (levelIndex !== -1) {
      this.projectData.levels[levelIndex] = this.currentLevel;
    } else {
      this.projectData.levels.push(this.currentLevel);
    }
    
    localStorage.setItem(`lupiforge_level_${this.currentLevel.id}`, JSON.stringify(this.currentLevel));
    this.showToast('✅ Level saved successfully');
  }

  loadLevel() {
    const levelSelect = document.createElement('div');
    levelSelect.className = 'level-selector-modal';
    levelSelect.innerHTML = `
      <div class="modal-content">
        <h2>Select Level to Load</h2>
        <div class="level-list">
          ${this.projectData.levels.map(level => `
            <div class="level-item" data-level-id="${level.id}">
              <h3>${level.name}</h3>
              <p>Grid: ${level.width}x${level.height}</p>
            </div>
          `).join('')}
        </div>
        <button id="cancelLoad">Cancel</button>
      </div>
    `;
    
    document.body.appendChild(levelSelect);
    
    levelSelect.querySelectorAll('.level-item').forEach(item => {
      item.addEventListener('click', () => {
        const levelId = item.getAttribute('data-level-id');
        if (levelId) {
          this.loadLevelById(levelId);
          document.body.removeChild(levelSelect);
        }
      });
    });
    
    levelSelect.querySelector('#cancelLoad')?.addEventListener('click', () => {
      document.body.removeChild(levelSelect);
    });
  }

  loadLevelById(levelId) {
    const level = this.projectData.levels.find(l => l.id === levelId);
    if (level) {
      this.undoStack.push(JSON.parse(JSON.stringify(this.currentLevel)));
      this.currentLevel = JSON.parse(JSON.stringify(level));
      this.render();
      this.showToast(`🎯 Level "${level.name}" loaded`);
    }
  }

  newLevel() {
    if (confirm('Create new level? Current changes will be lost if not saved.')) {
      this.undoStack.push(JSON.parse(JSON.stringify(this.currentLevel)));
      this.currentLevel = this.initializeLevel();
      this.render();
      this.showToast('🆕 New level created');
    }
  }

  showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'level-editor-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  }

  exportLevel() {
    return JSON.parse(JSON.stringify(this.currentLevel));
  }

  importLevel(levelData) {
    this.undoStack.push(JSON.parse(JSON.stringify(this.currentLevel)));
    this.currentLevel = JSON.parse(JSON.stringify(levelData));
    this.render();
  }

  getSpawnPoints() {
    return [...this.currentLevel.spawnPoints];
  }

  getCurrentLevel() {
    return this.currentLevel;
  }

  setupEventListeners() {
    window.addEventListener('resize', () => {
      this.canvas.width = window.innerWidth * 0.7;
      this.canvas.height = window.innerHeight * 0.8;
      this.render();
    });
  }
}

// Register visual blocks
if (typeof registerBlock !== 'undefined') {
  registerBlock({
    id: "level_spawn_point",
    category: "Level",
    label: "Spawn Point [TYPE] at x:[X] y:[Y]",
    inputs: {
      TYPE: { type: "dropdown", options: ["player", "enemy", "item", "npc", "checkpoint"], default: "player" },
      X: { type: "number", default: 100 },
      Y: { type: "number", default: 100 },
      PROPERTIES: { type: "object", default: "{}" }
    },
    output: null,
    compile(node) {
      return { 
        type: "SpawnPoint", 
        properties: {
          type: node.inputs.TYPE,
          x: parseFloat(node.inputs.X),
          y: parseFloat(node.inputs.Y),
          properties: JSON.parse(node.inputs.PROPERTIES || "{}")
        }
      };
    }
  });

  registerBlock({
    id: "get_spawn_point",
    category: "Level",
    label: "Get Spawn Point [TYPE]",
    inputs: {
      TYPE: { type: "dropdown", options: ["player", "enemy", "item", "npc", "checkpoint", "random"], default: "player" }
    },
    output: "vector",
    compile(node) {
      return { 
        type: "GetSpawnPoint", 
        properties: { type: node.inputs.TYPE }
      };
    }
  });

  registerBlock({
    id: "level_boundary",
    category: "Level",
    label: "Set Level Boundary x1:[X1] y1:[Y1] x2:[X2] y2:[Y2]",
    inputs: {
      X1: { type: "number", default: 0 },
      Y1: { type: "number", default: 0 },
      X2: { type: "number", default: 800 },
      Y2: { type: "number", default: 600 }
    },
    output: null,
    compile(node) {
      return { 
        type: "LevelBoundary", 
        properties: {
          x1: parseFloat(node.inputs.X1),
          y1: parseFloat(node.inputs.Y1),
          x2: parseFloat(node.inputs.X2),
          y2: parseFloat(node.inputs.Y2)
        }
      };
    }
  });
}

export default LevelEditor;
