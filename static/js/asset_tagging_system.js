// FIXED ASSET TAGGING SYSTEM
class AssetTaggingSystem {
  constructor(workspace, assetManager) {
    this.workspace = workspace;
    this.assetManager = assetManager;
    this.tagMap = JSON.parse(localStorage.getItem('lupiforge_asset_tags') || '{}');
    this.tagSuggestions = ['player', 'enemy', 'obstacle', 'collectible', 'projectile', 'npc', 'boss', 'interactive', 'background'];
    this.tagColorMap = {
      player: '#3498db',
      enemy: '#e74c3c',
      obstacle: '#95a5a6',
      collectible: '#2ecc71',
      projectile: '#f39c12',
      npc: '#9b59b6',
      boss: '#8e44ad',
      interactive: '#1abc9c',
      background: '#34495e'
    };
    this.setupEventListeners();
    this.registerTagBlocks();
    this.updateAllBlockDropdowns();
  }

  setupEventListeners() {
    // Listen for asset uploads
    if (this.assetManager.on) {
      this.assetManager.on('assetUploaded', (asset) => {
        this.showTaggingDialog(asset);
      });
    }
    
    // Listen for workspace changes to update dropdowns
    if (this.workspace.addChangeListener) {
      this.workspace.addChangeListener((event) => {
        if (event.type === Blockly.Events.CREATE || event.type === Blockly.Events.DELETE) {
          this.updateAllBlockDropdowns();
        }
      });
    }
  }

  registerTagBlocks() {
    // Register tag-related blocks
    Blockly.Blocks['tag_asset'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("Tag Asset")
            .appendField(new Blockly.FieldDropdown(() => this.getAssetOptions()), "ASSET")
            .appendField("with")
            .appendField(new Blockly.FieldTextInput(""), "TAG");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour("#e67e22");
        this.setTooltip("Add a tag to an asset for easier reference");
      },
      getAssetOptions: () => {
        const options = [["-- Select Asset --", ""]];
        const assets = this.assetManager.getAllAssets ? this.assetManager.getAllAssets() : [];
        assets.forEach(asset => {
          options.push([asset.name, asset.id]);
        });
        return options;
      }
    };

    Blockly.JavaScript['tag_asset'] = function(block) {
      const assetId = block.getFieldValue('ASSET');
      const tag = block.getFieldValue('TAG');
      return `tagAsset("${assetId}", "${tag}");\n`;
    };
  }

  tagAsset(assetId, tag) {
    if (!this.tagMap[assetId]) {
      this.tagMap[assetId] = [];
    }
    
    if (!this.tagMap[assetId].includes(tag)) {
      this.tagMap[assetId].push(tag);
      this.saveTagData();
      
      if (!this.tagSuggestions.includes(tag)) {
        this.tagSuggestions.push(tag);
      }
      
      this.updateAllBlockDropdowns();
    }
  }

  saveTagData() {
    localStorage.setItem('lupiforge_asset_tags', JSON.stringify(this.tagMap));
  }

  updateAllBlockDropdowns() {
    if (!this.workspace || !this.workspace.getAllBlocks) return;
    
    const allBlocks = this.workspace.getAllBlocks(false);
    allBlocks.forEach(block => {
      if (block.type.includes('tag') || block.type.includes('asset')) {
        this.updateBlockTagDropdowns(block);
      }
    });
  }

  updateBlockTagDropdowns(block) {
    // Update dropdowns for tags
    const tagField = block.getField('TAG') || block.getField('tag');
    if (tagField && typeof tagField.setOptions === 'function') {
      const options = this.getAllTags().map(tag => [tag, tag]);
      if (options.length > 0) {
        tagField.setOptions(options);
      }
    }
    
    // Update dropdowns for assets
    const assetField = block.getField('ASSET') || block.getField('SPRITE');
    if (assetField && typeof assetField.setOptions === 'function') {
      const assetOptions = this.getAssetOptions();
      if (assetOptions.length > 0) {
        assetField.setOptions(assetOptions);
      }
    }
  }

  getAssetOptions() {
    const options = [["-- Select Asset --", ""]];
    const assets = this.assetManager.getAllAssets ? this.assetManager.getAllAssets() : [];
    assets.forEach(asset => {
      const tags = this.getAssetTags(asset.id);
      const tagDisplay = tags.length > 0 ? ` (${tags.join(', ')})` : '';
      options.push([`${asset.name}${tagDisplay}`, asset.id]);
    });
    return options;
  }

  getAssetTags(assetId) {
    return this.tagMap[assetId] || [];
  }

  getAllTags() {
    const allTags = new Set();
    Object.values(this.tagMap).forEach(tags => {
      tags.forEach(tag => allTags.add(tag));
    });
    return Array.from(allTags);
  }

  showTaggingDialog(asset) {
    // Create modal dialog
    const modal = document.createElement('div');
    modal.className = 'asset-tagging-modal';
    modal.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #16213e;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 5px 30px rgba(0,0,0,0.5);
      z-index: 1000;
      min-width: 400px;
    `;
    
    modal.innerHTML = `
      <h3 style="color: white; margin-bottom: 20px;">🏷️ Tag Asset: ${asset.name}</h3>
      <div style="margin-bottom: 15px;">
        <label style="color: #95a5a6; font-size: 14px; display: block; margin-bottom: 5px;">Select Tags:</label>
        <div id="tag-suggestions" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;"></div>
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
          <input type="text" id="new-tag-input" placeholder="Add custom tag..." 
            style="flex: 1; padding: 8px; border: 1px solid #533483; border-radius: 5px; background: #0f3460; color: white;">
          <button id="add-tag-btn" style="padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">Add</button>
        </div>
        <div id="selected-tags" style="display: flex; flex-wrap: wrap; gap: 8px; min-height: 40px; padding: 10px; background: #0f3460; border-radius: 5px;"></div>
      </div>
      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button id="skip-tagging" style="padding: 10px 20px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer;">Skip</button>
        <button id="confirm-tagging" style="padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer;">Confirm Tags</button>
      </div>
    `;
    
    document.body.appendChild(modal);
    this.renderTagSuggestions(modal, asset);
    this.setupTaggingDialogEvents(modal, asset);
  }

  renderTagSuggestions(modal, asset) {
    const suggestionsContainer = modal.querySelector('#tag-suggestions');
    const selectedTagsContainer = modal.querySelector('#selected-tags');
    
    // Add existing tags first
    const existingTags = this.getAssetTags(asset.id);
    existingTags.forEach(tag => {
      this.toggleTagSelection(tag, selectedTagsContainer, true);
    });
    
    // Add all available tag suggestions
    this.tagSuggestions.forEach(tag => {
      const tagElement = document.createElement('button');
      tagElement.textContent = tag;
      tagElement.style.cssText = `
        background: ${this.getTagColor(tag)};
        color: white;
        border: none;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s;
      `;
      
      tagElement.addEventListener('click', () => {
        this.toggleTagSelection(tag, selectedTagsContainer);
        tagElement.style.background = this.getTagColor(tag, 0.7);
      });
      
      suggestionsContainer.appendChild(tagElement);
    });
  }

  toggleTagSelection(tag, container, forceAdd = false) {
    const existingTags = Array.from(container.children)
      .map(el => el.dataset.tag)
      .filter(Boolean);
      
    if (forceAdd || !existingTags.includes(tag)) {
      const tagElement = document.createElement('span');
      tagElement.textContent = `🏷️ ${tag}`;
      tagElement.dataset.tag = tag;
      tagElement.style.cssText = `
        background: ${this.getTagColor(tag)};
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 5px;
      `;
      
      const removeBtn = document.createElement('button');
      removeBtn.innerHTML = '×';
      removeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        margin-left: 5px;
        font-weight: bold;
      `;
      
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        container.removeChild(tagElement);
      });
      
      tagElement.appendChild(removeBtn);
      container.appendChild(tagElement);
    } else {
      const tagElement = container.querySelector(`[data-tag="${tag}"]`);
      if (tagElement) {
        container.removeChild(tagElement);
      }
    }
  }

  setupTaggingDialogEvents(modal, asset) {
    const newTagInput = modal.querySelector('#new-tag-input');
    const addTagBtn = modal.querySelector('#add-tag-btn');
    const skipBtn = modal.querySelector('#skip-tagging');
    const confirmBtn = modal.querySelector('#confirm-tagging');
    const selectedTagsContainer = modal.querySelector('#selected-tags');
    
    addTagBtn.addEventListener('click', () => {
      const tag = newTagInput.value.trim().toLowerCase();
      if (tag && !this.tagSuggestions.includes(tag)) {
        this.tagSuggestions.push(tag);
      }
      
      if (tag) {
        this.toggleTagSelection(tag, selectedTagsContainer, true);
        newTagInput.value = '';
        
        // Update suggestions
        const suggestionsContainer = modal.querySelector('#tag-suggestions');
        suggestionsContainer.innerHTML = '';
        this.renderTagSuggestions(modal, asset);
      }
    });
    
    // Allow pressing Enter to add a tag
    newTagInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        addTagBtn.click();
      }
    });
    
    skipBtn.addEventListener('click', () => {
      document.body.removeChild(modal);
    });
    
    confirmBtn.addEventListener('click', () => {
      const selectedTags = Array.from(selectedTagsContainer.children)
        .map(el => el.dataset.tag)
        .filter(Boolean);
        
      // Update tags for this asset
      this.tagMap[asset.id] = [...new Set(selectedTags)]; // Remove duplicates
      this.saveTagData();
      
      // Update any blocks that might be using these tags
      this.updateAllBlockDropdowns();
      
      document.body.removeChild(modal);
    });
  }

  getTagColor(tag, opacity = 1) {
    const baseColor = this.tagColorMap[tag] || '#533483';
    if (opacity < 1) {
      const r = parseInt(baseColor.slice(1, 3), 16);
      const g = parseInt(baseColor.slice(3, 5), 16);
      const b = parseInt(baseColor.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    return baseColor;
  }
}

// Initialize if possible
if (typeof Blockly !== 'undefined' && typeof workspace !== 'undefined' && typeof assetManager !== 'undefined') {
  window.assetTaggingSystem = new AssetTaggingSystem(workspace, assetManager);
}
