class RenderSystem {
  camera = {
    x: 0,
    y: 0,
    targetX: 0,
    targetY: 0,
    width: 800,
    height: 600,
    zoom: 1.0,
    minZoom: 0.5,
    maxZoom: 3.0,
    smooth: 0.1,
    bounds: {
      minX: -Infinity,
      maxX: Infinity,
      minY: -Infinity,
      maxY: Infinity
    },
    shake: {
      intensity: 0,
      duration: 0,
      startTime: 0
    },
    transitions: [],
    followTarget: null,
    followOffset: { x: 0, y: 0 },
    isShaking: false
  };
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  entities: any[];
  background: any;
  layers: any[];

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.entities = [];
    this.layers = [];
    this.resize();
    this.initEventListeners();
  }

  initEventListeners() {
    window.addEventListener('resize', this.resize.bind(this));
    
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      this.setZoom(this.camera.zoom + delta);
    });
  }

  resize() {
    this.camera.width = this.canvas.width;
    this.camera.height = this.canvas.height;
  }

  setCameraPosition(x: number, y: number) {
    this.camera.targetX = x;
    this.camera.targetY = y;
    this.applyCameraBounds();
  }

  setZoom(zoom: number) {
    this.camera.zoom = Math.max(this.camera.minZoom, Math.min(this.camera.maxZoom, zoom));
  }

  setCameraBounds(minX: number, maxX: number, minY: number, maxY: number) {
    this.camera.bounds.minX = minX;
    this.camera.bounds.maxX = maxX;
    this.camera.bounds.minY = minY;
    this.camera.bounds.maxY = maxY;
    this.applyCameraBounds();
  }

  setCameraFollow(target: any, offsetX: number = 0, offsetY: number = 0, smooth: number = 0.1) {
    this.camera.followTarget = target;
    this.camera.followOffset.x = offsetX;
    this.camera.followOffset.y = offsetY;
    this.camera.smooth = smooth;
  }

  stopCameraFollow() {
    this.camera.followTarget = null;
  }

  applyCameraBounds() {
    if (isFinite(this.camera.bounds.minX)) {
      this.camera.targetX = Math.max(this.camera.bounds.minX, this.camera.targetX);
    }
    if (isFinite(this.camera.bounds.maxX)) {
      this.camera.targetX = Math.min(this.camera.bounds.maxX, this.camera.targetX);
    }
    if (isFinite(this.camera.bounds.minY)) {
      this.camera.targetY = Math.max(this.camera.bounds.minY, this.camera.targetY);
    }
    if (isFinite(this.camera.bounds.maxY)) {
      this.camera.targetY = Math.min(this.camera.bounds.maxY, this.camera.targetY);
    }
  }

  cameraShake(intensity: number, duration: number) {
    this.camera.shake.intensity = intensity;
    this.camera.shake.duration = duration * 1000;
    this.camera.shake.startTime = Date.now();
    this.camera.isShaking = true;
  }

  startCameraTransition(toX: number, toY: number, duration: number, easing: string = 'linear') {
    const transition = {
      fromX: this.camera.x,
      fromY: this.camera.y,
      toX,
      toY,
      duration,
      elapsed: 0,
      easing,
      startTime: Date.now()
    };
    this.camera.transitions.push(transition);
  }

  update(deltaTime: number) {
    if (this.camera.followTarget && this.camera.followTarget.x !== undefined) {
      this.camera.targetX = this.camera.followTarget.x + this.camera.followOffset.x - (this.camera.width / (2 * this.camera.zoom));
      this.camera.targetY = this.camera.followTarget.y + this.camera.followOffset.y - (this.camera.height / (2 * this.camera.zoom));
      this.applyCameraBounds();
    }

    this.camera.x += (this.camera.targetX - this.camera.x) * this.camera.smooth;
    this.camera.y += (this.camera.targetY - this.camera.y) * this.camera.smooth;

    if (this.camera.isShaking) {
      const elapsed = Date.now() - this.camera.shake.startTime;
      if (elapsed < this.camera.shake.duration) {
        const progress = elapsed / this.camera.shake.duration;
        const intensity = this.camera.shake.intensity * (1 - progress);
        
        this.camera.x += (Math.random() - 0.5) * intensity;
        this.camera.y += (Math.random() - 0.5) * intensity;
      } else {
        this.camera.isShaking = false;
      }
    }

    for (let i = this.camera.transitions.length - 1; i >= 0; i--) {
      const transition = this.camera.transitions[i];
      transition.elapsed = Date.now() - transition.startTime;
      
      if (transition.elapsed >= transition.duration) {
        this.camera.x = transition.toX;
        this.camera.y = transition.toY;
        this.camera.transitions.splice(i, 1);
        continue;
      }
      
      const progress = transition.elapsed / transition.duration;
      const easedProgress = this.getEasedProgress(progress, transition.easing);
      
      this.camera.x = transition.fromX + (transition.toX - transition.fromX) * easedProgress;
      this.camera.y = transition.fromY + (transition.toY - transition.fromY) * easedProgress;
    }
  }

  getEasedProgress(progress: number, easing: string): number {
    switch (easing) {
      case 'easeIn':
        return progress * progress;
      case 'easeOut':
        return 1 - Math.pow(1 - progress, 2);
      case 'easeInOut':
        return progress < 0.5 
          ? 2 * progress * progress 
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
      case 'elastic':
        return Math.pow(2, -10 * progress) * Math.sin((progress * 10 - 0.75) * (2 * Math.PI) / 3) + 1;
      case 'bounce':
        const n1 = 7.5625;
        const d1 = 2.75;
        if (progress < 1 / d1) {
          return n1 * progress * progress;
        } else if (progress < 2 / d1) {
          progress -= 1.5 / d1;
          return n1 * progress * progress + 0.75;
        } else if (progress < 2.5 / d1) {
          progress -= 2.25 / d1;
          return n1 * progress * progress + 0.9375;
        } else {
          progress -= 2.625 / d1;
          return n1 * progress * progress + 0.984375;
        }
      default:
        return progress;
    }
  }

  render() {
    this.ctx.save();
    
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
    this.ctx.scale(this.camera.zoom, this.camera.zoom);
    this.ctx.translate(-this.canvas.width / 2, -this.canvas.height / 2);
    
    this.ctx.translate(-this.camera.x, -this.camera.y);
    
    if (this.background) {
      this.renderBackground();
    }
    
    this.renderLayers();
    this.renderEntities();
    
    this.ctx.restore();
  }

  renderBackground() {
    if (!this.background) return;
    
    if (typeof this.background === 'string') {
      const img = new Image();
      img.src = this.background;
      this.ctx.drawImage(img, this.camera.x, this.camera.y, this.camera.width, this.camera.height);
    } else if (this.background.color) {
      this.ctx.fillStyle = this.background.color;
      this.ctx.fillRect(this.camera.x, this.camera.y, this.camera.width, this.camera.height);
    }
  }

  renderLayers() {
    this.layers.forEach(layer => {
      if (layer.visible !== false) {
        if (layer.type === 'tilemap') {
          this.renderTilemap(layer);
        } else if (layer.type === 'particles') {
          this.renderParticles(layer);
        }
      }
    });
  }

  renderEntities() {
    const sortedEntities = [...this.entities].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
    
    sortedEntities.forEach(entity => {
      if (entity.visible !== false) {
        this.renderEntity(entity);
      }
    });
  }

  renderEntity(entity: any) {
    if (!this.isEntityInView(entity)) return;
    
    this.ctx.save();
    
    this.ctx.translate(entity.x, entity.y);
    
    if (entity.rotation) {
      this.ctx.rotate(entity.rotation);
    }
    
    if (entity.scaleX || entity.scaleY) {
      this.ctx.scale(entity.scaleX || 1, entity.scaleY || 1);
    }
    
    if (entity.flipX) {
      this.ctx.scale(-1, 1);
      this.ctx.translate(-entity.width, 0);
    }
    
    if (entity.flipY) {
      this.ctx.scale(1, -1);
      this.ctx.translate(0, -entity.height);
    }
    
    if (entity.opacity !== undefined && entity.opacity < 1) {
      this.ctx.globalAlpha = entity.opacity;
    }
    
    if (entity.sprite) {
      this.renderSprite(entity);
    } else if (entity.text) {
      this.renderText(entity);
    } else if (entity.shape) {
      this.renderShape(entity);
    } else {
      this.renderDefault(entity);
    }
    
    this.ctx.restore();
  }
  
  isEntityInView(entity: any): boolean {
    const cameraRight = this.camera.x + this.camera.width / this.camera.zoom;
    const cameraBottom = this.camera.y + this.camera.height / this.camera.zoom;
    
    return !(
      entity.x + (entity.width || 0) < this.camera.x ||
      entity.x > cameraRight ||
      entity.y + (entity.height || 0) < this.camera.y ||
      entity.y > cameraBottom
    );
  }

  renderSprite(entity: any) {
    if (entity.sprite.complete) {
      const width = entity.width || entity.sprite.width;
      const height = entity.height || entity.sprite.height;
      
      const offsetX = entity.offsetX || 0;
      const offsetY = entity.offsetY || 0;
      
      this.ctx.drawImage(
        entity.sprite,
        0, 0, entity.sprite.width, entity.sprite.height,
        -width / 2 - offsetX, -height / 2 - offsetY, width, height
      );
    }
  }

  renderText(entity: any) {
    this.ctx.font = entity.fontSize ? `${entity.fontSize}px ${entity.fontFamily || 'Arial'}` : '16px Arial';
    this.ctx.fillStyle = entity.color || '#ffffff';
    this.ctx.textAlign = entity.textAlign || 'center';
    this.ctx.textBaseline = entity.textBaseline || 'middle';
    
    const lines = entity.text.split('\n');
    const lineHeight = entity.lineHeight || 1.5;
    
    lines.forEach((line: string, i: number) => {
      const y = (i - (lines.length - 1) / 2) * (entity.fontSize || 16) * lineHeight;
      this.ctx.fillText(line, 0, y);
    });
  }

  renderShape(entity: any) {
    switch (entity.shape) {
      case 'circle':
        this.ctx.beginPath();
        this.ctx.arc(0, 0, entity.radius || 20, 0, Math.PI * 2);
        if (entity.fillColor) {
          this.ctx.fillStyle = entity.fillColor;
          this.ctx.fill();
        }
        if (entity.strokeColor) {
          this.ctx.strokeStyle = entity.strokeColor;
          this.ctx.lineWidth = entity.strokeWidth || 2;
          this.ctx.stroke();
        }
        break;
      case 'rectangle':
        const width = entity.width || 50;
        const height = entity.height || 50;
        this.ctx.beginPath();
        this.ctx.rect(-width / 2, -height / 2, width, height);
        if (entity.fillColor) {
          this.ctx.fillStyle = entity.fillColor;
          this.ctx.fill();
        }
        if (entity.strokeColor) {
          this.ctx.strokeStyle = entity.strokeColor;
          this.ctx.lineWidth = entity.strokeWidth || 2;
          this.ctx.stroke();
        }
        break;
      case 'polygon':
        if (entity.points && entity.points.length > 0) {
          this.ctx.beginPath();
          this.ctx.moveTo(entity.points[0].x, entity.points[0].y);
          for (let i = 1; i < entity.points.length; i++) {
            this.ctx.lineTo(entity.points[i].x, entity.points[i].y);
          }
          this.ctx.closePath();
          
          if (entity.fillColor) {
            this.ctx.fillStyle = entity.fillColor;
            this.ctx.fill();
          }
          if (entity.strokeColor) {
            this.ctx.strokeStyle = entity.strokeColor;
            this.ctx.lineWidth = entity.strokeWidth || 2;
            this.ctx.stroke();
          }
        }
        break;
    }
  }

  renderDefault(entity: any) {
    this.ctx.fillStyle = entity.color || '#2196F3';
    this.ctx.fillRect(-25, -25, 50, 50);
    
    if (entity.debug) {
      this.ctx.strokeStyle = '#FF5252';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(-25, -25, 50, 50);
    }
  }

  renderTilemap(layer: any) {
    if (!layer.data || !layer.tileWidth || !layer.tileHeight) return;
    
    const startX = Math.floor(this.camera.x / layer.tileWidth);
    const startY = Math.floor(this.camera.y / layer.tileHeight);
    const endX = Math.ceil((this.camera.x + this.camera.width / this.camera.zoom) / layer.tileWidth);
    const endY = Math.ceil((this.camera.y + this.camera.height / this.camera.zoom) / layer.tileHeight);
    
    for (let y = startY; y <= endY; y++) {
      for (let x = startX; x <= endX; x++) {
        const index = y * layer.width + x;
        const tileId = layer.data[index];
        
        if (tileId > 0 && layer.tileset && layer.tileset[tileId]) {
          const tile = layer.tileset[tileId];
          
          const srcX = (tileId % layer.tilesPerRow) * layer.tileWidth;
          const srcY = Math.floor(tileId / layer.tilesPerRow) * layer.tileHeight;
          
          const destX = x * layer.tileWidth;
          const destY = y * layer.tileHeight;
          
          this.ctx.drawImage(
            tile.image,
            srcX, srcY, layer.tileWidth, layer.tileHeight,
            destX, destY, layer.tileWidth, layer.tileHeight
          );
        }
      }
    }
  }

  renderDebugOverlay() {
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    this.ctx.font = '12px Arial';
    this.ctx.fillStyle = '#fff';
    this.ctx.fillText(`Camera: (${Math.round(this.camera.x)}, ${Math.round(this.camera.y)})`, 10, 20);
    this.ctx.fillText(`Zoom: ${this.camera.zoom.toFixed(2)}`, 10, 40);
    
    this.ctx.fillText(`Entities: ${this.entities.length}`, 10, 60);
    
    if (isFinite(this.camera.bounds.minX)) {
      this.ctx.strokeStyle = '#FF5252';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(
        this.camera.bounds.minX - this.camera.x,
        this.camera.bounds.minY - this.camera.y,
        this.camera.bounds.maxX - this.camera.bounds.minX,
        this.camera.bounds.maxY - this.camera.bounds.minY
      );
    }
    
    this.ctx.restore();
  }

  getCameraPosition() {
    return { x: this.camera.x, y: this.camera.y };
  }

  getCameraZoom() {
    return this.camera.zoom;
  }

  isPointInView(x: number, y: number): boolean {
    return (
      x >= this.camera.x && 
      x <= this.camera.x + this.camera.width / this.camera.zoom &&
      y >= this.camera.y && 
      y <= this.camera.y + this.camera.height / this.camera.zoom
    );
  }

  screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    const rect = this.canvas.getBoundingClientRect();
    const adjustedX = screenX - rect.left;
    const adjustedY = screenY - rect.top;
    
    const worldX = (adjustedX / this.camera.zoom) + this.camera.x - (this.canvas.width / (2 * this.camera.zoom));
    const worldY = (adjustedY / this.camera.zoom) + this.camera.y - (this.canvas.height / (2 * this.camera.zoom));
    
    return { x: worldX, y: worldY };
  }

  worldToScreen(worldX: number, worldY: number): { x: number; y: number } {
    const screenX = (worldX - this.camera.x) * this.camera.zoom + (this.canvas.width / 2);
    const screenY = (worldY - this.camera.y) * this.camera.zoom + (this.canvas.height / 2);
    return { x: screenX, y: screenY };
  }
}

export function setCameraPosition(x: number, y: number) {
  renderSystem.setCameraPosition(x, y);
}

export function setCameraZoom(zoom: number) {
  renderSystem.setZoom(zoom);
}

export function setCameraBounds(minX: number, maxX: number, minY: number, maxY: number) {
  renderSystem.setCameraBounds(minX, maxX, minY, maxY);
}

export function followCamera(target: any, offsetX: number = 0, offsetY: number = 0, smooth: number = 0.1) {
  renderSystem.setCameraFollow(target, offsetX, offsetY, smooth);
}

export function stopCameraFollow() {
  renderSystem.stopCameraFollow();
}

export function shakeCamera(intensity: number = 10, duration: number = 0.5) {
  renderSystem.cameraShake(intensity, duration);
}

export function transitionCamera(toX: number, toY: number, duration: number = 1, easing: string = 'linear') {
  renderSystem.startCameraTransition(toX, toY, duration, easing);
}

export function screenToWorld(x: number, y: number) {
  return renderSystem.screenToWorld(x, y);
}

export function worldToScreen(x: number, y: number) {
  return renderSystem.worldToScreen(x, y);
}

const renderSystem = new RenderSystem(document.getElementById('gameCanvas') as HTMLCanvasElement);
export default renderSystem;
