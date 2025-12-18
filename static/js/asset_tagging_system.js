(function() {
  if (typeof AssetTaggingSystem !== 'undefined') {
    console.log('⚠️ AssetTaggingSystem already defined, skipping redeclaration');
    return;
  }

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
      if (this.assetManager.on) {
        this.assetManager.on('assetUploaded', (asset) => {
          this.showTaggingDialog(asset);
        });
      }
      
      if (this.workspace.addChangeListener) {
        this.workspace.addChangeListener(() => {
          this.updateAllBlockDropdowns();
        });
      }
    }

    registerTagBlocks() {
      if (typeof Blockly === 'undefined') return;
      
      Blockly.Blocks['asset_tag'] = {
        init: function() {
          this.appendValueInput('ASSET')
            .setCheck('asset')
            .appendField('Asset');
          this.appendValueInput('TAG')
            .setCheck('string')
            .appendField('Tag as');
          this.setPreviousStatement(true, null);
          this.setNextStatement(true, null);
          this.setColour(65);
          this.setTooltip('Tag an asset for quick reference');
        }
      };

      Blockly.JavaScript.forBlock['asset_tag'] = function(block) {
        const asset = Blockly.JavaScript.valueToCode(block, 'ASSET', Blockly.JavaScript.ORDER_ATOMIC);
        const tag = Blockly.JavaScript.valueToCode(block, 'TAG', Blockly.JavaScript.ORDER_ATOMIC);
        return `assetTaggingSystem.tagAsset(${asset}, ${tag});\n`;
      };
    }

    tagAsset(assetId, tag) {
      if (!this.tagMap[assetId]) {
        this.tagMap[assetId] = [];
      }
      if (!this.tagMap[assetId].includes(tag)) {
        this.tagMap[assetId].push(tag);
        this.saveTags();
      }
    }

    untagAsset(assetId, tag) {
      if (this.tagMap[assetId]) {
        this.tagMap[assetId] = this.tagMap[assetId].filter(t => t !== tag);
        if (this.tagMap[assetId].length === 0) {
          delete this.tagMap[assetId];
        }
        this.saveTags();
      }
    }

    getAssetTags(assetId) {
      return this.tagMap[assetId] || [];
    }

    saveTags() {
      localStorage.setItem('lupiforge_asset_tags', JSON.stringify(this.tagMap));
    }

    showTaggingDialog(asset) {
      const dialog = document.createElement('div');
      dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 5px 25px rgba(0,0,0,0.3);
        z-index: 10000;
        min-width: 300px;
      `;

      dialog.innerHTML = `
        <h3>${asset.name}</h3>
        <p>Select tags for this asset:</p>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;">
          ${this.tagSuggestions.map(tag => `
            <label style="display: flex; align-items: center; gap: 5px;">
              <input type="checkbox" value="${tag}" class="tag-checkbox">
              <span style="background: ${this.tagColorMap[tag]}; color: white; padding: 3px 10px; border-radius: 3px;">${tag}</span>
            </label>
          `).join('')}
        </div>
        <div style="display: flex; gap: 10px; margin-top: 20px;">
          <button onclick="this.parentElement.parentElement.remove()" style="flex: 1; padding: 10px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">Done</button>
        </div>
      `;

      document.body.appendChild(dialog);

      dialog.querySelectorAll('.tag-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
          if (checkbox.checked) {
            this.tagAsset(asset.id, checkbox.value);
          } else {
            this.untagAsset(asset.id, checkbox.value);
          }
        });
      });
    }

    updateAllBlockDropdowns() {
      if (typeof Blockly === 'undefined') return;
      
      const blocks = this.workspace.getAllBlocks(false);
      blocks.forEach(block => {
        if (block.type === 'asset_tag') {
          const field = block.getField('TAG');
          if (field && field.menuGenerator_) {
            const options = this.tagSuggestions.map(tag => [tag, tag]);
            field.menuGenerator_ = () => options;
          }
        }
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

  window.AssetTaggingSystem = AssetTaggingSystem;
  console.log('✅ AssetTaggingSystem loaded');
})();

// Initialize if possible
if (typeof Blockly !== 'undefined' && typeof workspace !== 'undefined' && typeof assetManager !== 'undefined') {
  window.assetTaggingSystem = new AssetTaggingSystem(workspace, assetManager);
}
