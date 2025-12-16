declare const Blockly: any;
declare const registerBlock: any;
declare function showToast(message: string): void;

interface AssetTaggingOptions {
  workspace: any;
  assetManager: any;
}

interface TagEvent {
  assetId: string;
  tag: string;
}

class AssetTaggingSystem {
  private workspace: any;
  private assetManager: any;
  private tagMap: Record<string, string[]> = {};
  private tagSuggestions: string[] = ['player', 'enemy', 'obstacle', 'collectible', 'projectile', 'npc', 'boss', 'interactive', 'background'];
  private tagColorMap: Record<string, string> = {
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
  private eventListeners: Record<string, ((data: any) => void)[]> = {};

  constructor(workspace: any, assetManager: any) {
    this.workspace = workspace;
    this.assetManager = assetManager;
    this.loadTagData();
    this.setupEventListeners();
    this.registerTagBlocks();
    this.updateAllBlockDropdowns();
  }

  private loadTagData(): void {
    try {
      const savedTags = localStorage.getItem('lupiforge_asset_tags');
      if (savedTags) {
        this.tagMap = JSON.parse(savedTags);
      }
    } catch (error) {
      console.warn('Failed to load asset tags:', error);
      this.tagMap = {};
    }
  }

  private saveTagData(): void {
    try {
      localStorage.setItem('lupiforge_asset_tags', JSON.stringify(this.tagMap));
    } catch (error) {
      console.error('Failed to save asset tags:', error);
    }
  }

  private setupEventListeners(): void {
    if (this.assetManager && typeof this.assetManager.on === 'function') {
      this.assetManager.on('assetUploaded', (asset: any) => {
        this.showTaggingDialog(asset);
      });
    }
    
    if (this.workspace && typeof this.workspace.addChangeListener === 'function') {
      this.workspace.addChangeListener((event: any) => {
        if (event && (event.type === Blockly.Events.CREATE || event.type === Blockly.Events.DELETE)) {
          this.updateAllBlockDropdowns();
        }
      });
    }
  }

  private registerTagBlocks(): void {
    if (typeof registerBlock === 'undefined') {
      console.warn('registerBlock not available');
      return;
    }

    registerBlock({
      id: "tag_asset",
      category: "Assets",
      label: "Tag Asset [ASSET] with [TAG]",
      inputs: {
        ASSET: { type: "asset", options: this.getAssetOptions() },
        TAG: { type: "string", suggestions: this.tagSuggestions }
      },
      output: null,
      compile: (node: any) => {
        return { 
          type: "TagAsset", 
          properties: {
            assetId: node.inputs.ASSET,
            tag: node.inputs.TAG
          }
        };
      }
    });

    registerBlock({
      id: "get_assets_by_tag",
      category: "Assets",
      label: "Get Assets with Tag [TAG]",
      inputs: {
        TAG: { type: "string", suggestions: this.tagSuggestions }
      },
      output: "array",
      compile: (node: any) => {
        return { 
          type: "GetAssetsByTag", 
          properties: {
            tag: node.inputs.TAG
          }
        };
      }
    });

    registerBlock({
      id: "asset_has_tag",
      category: "Assets",
      label: "Asset [ASSET] has Tag [TAG]?",
      inputs: {
        ASSET: { type: "asset", options: this.getAssetOptions() },
        TAG: { type: "string", suggestions: this.tagSuggestions }
      },
      output: "boolean",
      compile: (node: any) => {
        return { 
          type: "AssetHasTag", 
          properties: {
            assetId: node.inputs.ASSET,
            tag: node.inputs.TAG
          }
        };
      }
    });
  }

  tagAsset(assetId: string, tag: string): void {
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
      this.emitTagEvent('assetTagged', { assetId, tag });
    }
  }

  untagAsset(assetId: string, tag: string): void {
    if (this.tagMap[assetId]) {
      this.tagMap[assetId] = this.tagMap[assetId].filter(t => t !== tag);
      this.saveTagData();
      this.updateAllBlockDropdowns();
      this.emitTagEvent('assetUntagged', { assetId, tag });
    }
  }

  getAssetsByTag(tag: string): any[] {
    return Object.entries(this.tagMap)
      .filter(([_, tags]) => (tags as string[]).includes(tag))
      .map(([assetId]) => this.assetManager.getAssetById(assetId))
      .filter(asset => asset !== null);
  }

  getAssetTags(assetId: string): string[] {
    return this.tagMap[assetId] || [];
  }

  getAllTags(): string[] {
    const allTags = new Set<string>();
    Object.values(this.tagMap).forEach(tags => {
      tags.forEach(tag => allTags.add(tag));
    });
    return Array.from(allTags);
  }

  private getAssetOptions(): any[] {
    const tags = this.getAllTags();
    const options: any[] = [["-- Select Asset --", ""]];
    
    if (tags.length > 0) {
      options.push(["----- BY TAG -----", "HEADER"]);
      tags.forEach(tag => {
        options.push([`🏷️ ${tag}`, `tag:${tag}`]);
      });
    }
    
    return options;
  }

  showTaggingDialog(asset: any): void {
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

  private renderTagSuggestions(modal: HTMLElement, asset: any): void {
    const suggestionsContainer = modal.querySelector('#tag-suggestions') as HTMLElement;
    const selectedTagsContainer = modal.querySelector('#selected-tags') as HTMLElement;
    
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
    
    const assetName = asset.name.toLowerCase();
    const autoTags = this.suggestTagsFromName(assetName);
    autoTags.forEach(tag => {
      const tagElements = suggestionsContainer.querySelectorAll('button');
      tagElements.forEach(el => {
        if (el.textContent === tag) {
          el.style.background = this.getTagColor(tag, 0.7);
          this.toggleTagSelection(tag, selectedTagsContainer, true);
        }
      });
    });
  }

  private suggestTagsFromName(assetName: string): string[] {
    const suggestions: string[] = [];
    
    if (assetName.includes('player') || assetName.includes('hero') || assetName.includes('character')) {
      suggestions.push('player');
    }
    
    if (assetName.includes('enemy') || assetName.includes('monster') || assetName.includes('bad') || assetName.includes('villain')) {
      suggestions.push('enemy');
    }
    
    if (assetName.includes('coin') || assetName.includes('gem') || assetName.includes('star') || assetName.includes('collect')) {
      suggestions.push('collectible');
    }
    
    if (assetName.includes('wall') || assetName.includes('block') || assetName.includes('platform') || assetName.includes('ground')) {
      suggestions.push('obstacle');
    }
    
    if (assetName.includes('bullet') || assetName.includes('laser') || assetName.includes('fireball') || assetName.includes('projectile')) {
      suggestions.push('projectile');
    }
    
    return suggestions;
  }

  private toggleTagSelection(tag: string, container: HTMLElement, forceAdd: boolean = false): void {
    const existingTags = Array.from(container.children)
      .map(el => (el as HTMLElement).dataset.tag)
      .filter(Boolean) as string[];
      
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

  private setupTaggingDialogEvents(modal: HTMLElement, asset: any): void {
    const newTagInput = modal.querySelector('#new-tag-input') as HTMLInputElement;
    const addTagBtn = modal.querySelector('#add-tag-btn') as HTMLButtonElement;
    const skipBtn = modal.querySelector('#skip-tagging') as HTMLButtonElement;
    const confirmBtn = modal.querySelector('#confirm-tagging') as HTMLButtonElement;
    const selectedTagsContainer = modal.querySelector('#selected-tags') as HTMLElement;
    
    addTagBtn.addEventListener('click', () => {
      const tag = newTagInput.value.trim().toLowerCase();
      if (tag && !this.tagSuggestions.includes(tag)) {
        this.tagSuggestions.push(tag);
      }
      
      if (tag) {
        this.toggleTagSelection(tag, selectedTagsContainer, true);
        newTagInput.value = '';
        
        const suggestionsContainer = modal.querySelector('#tag-suggestions') as HTMLElement;
        suggestionsContainer.innerHTML = '';
        this.renderTagSuggestions(modal, asset);
      }
    });
    
    skipBtn.addEventListener('click', () => {
      document.body.removeChild(modal);
    });
    
    confirmBtn.addEventListener('click', () => {
      const selectedTags = Array.from(selectedTagsContainer.children)
        .map(el => (el as HTMLElement).dataset.tag)
        .filter(Boolean) as string[];
        
      selectedTags.forEach(tag => {
        this.tagAsset(asset.id, tag);
      });
      
      document.body.removeChild(modal);
      showToast(`✅ ${selectedTags.length} tags added to ${asset.name}`);
    });
  }

  private getTagColor(tag: string, opacity: number = 1): string {
    const baseColor = this.tagColorMap[tag] || '#533483';
    if (opacity < 1) {
      const r = parseInt(baseColor.slice(1, 3), 16);
      const g = parseInt(baseColor.slice(3, 5), 16);
      const b = parseInt(baseColor.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    return baseColor;
  }

  updateAllBlockDropdowns(): void {
    if (!this.workspace) return;
    const allBlocks = this.workspace.getAllBlocks(false);
    
    allBlocks.forEach(block => {
      if (block.type.includes('tag') || block.type.includes('asset') || block.type.includes('spawn')) {
        this.updateBlockTagDropdowns(block);
      }
    });
  }

  private updateBlockTagDropdowns(block: any): void {
    const options = this.getAssetOptions();
    const field = block.getField('ASSET') || block.getField('TAG') || block.getField('SPRITE');
    
    if (field && typeof field.setOptions === 'function') {
      field.setOptions(options);
    }
  }

  private emitTagEvent(eventName: string, data: TagEvent): void {
    if (this.eventListeners[eventName]) {
      this.eventListeners[eventName].forEach(callback => {
        callback(data);
      });
    }
  }

  on(eventName: string, callback: (data: TagEvent) => void): void {
    if (!this.eventListeners[eventName]) {
      this.eventListeners[eventName] = [];
    }
    this.eventListeners[eventName].push(callback);
  }
}

export default AssetTaggingSystem;
