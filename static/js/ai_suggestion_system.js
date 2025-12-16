// FIXED AI SUGGESTION SYSTEM
class AISuggestionSystem {
  constructor(workspace) {
    this.workspace = workspace;
    this.suggestions = [];
    this.lastAnalysisTime = 0;
    this.analysisInterval = 2000; // 2 seconds
    this.suggestionPanel = null;
    this.enabled = true;
    this.suggestionHistory = [];
    this.maxSuggestions = 5;
    this.lastSuggestionTime = 0;
    this.suggestionCooldown = 3000; // 3 seconds between suggestions
    this.suggestionContainer = null;
    this.init();
  }

  init() {
    this.createSuggestionPanel();
    this.setupEventListeners();
    this.scheduleAnalysis();
  }

  setupEventListeners() {
    if (!this.workspace) return;
    
    if (this.workspace.addChangeListener) {
      this.workspace.addChangeListener((event) => {
        if (event.type === Blockly.Events.BLOCK_CREATE || 
            event.type === Blockly.Events.BLOCK_DELETE) {
          this.scheduleAnalysis();
        }
      });
    }
  }

  createSuggestionPanel() {
    this.suggestionPanel = document.createElement('div');
    this.suggestionPanel.id = 'ai-suggestion-panel';
    this.suggestionPanel.className = 'ai-suggestion-panel';
    this.suggestionPanel.style.cssText = `
      position: fixed;
      bottom: 80px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 10px;
      box-shadow: 0 5px 25px rgba(0,0,0,0.4);
      padding: 15px;
      width: 300px;
      max-height: 400px;
      overflow-y: auto;
      z-index: 1000;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.3s ease;
      font-family: Arial, sans-serif;
    `;
    
    const header = document.createElement('div');
    header.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(255,255,255,0.2);
    `;
    
    const title = document.createElement('h3');
    title.style.cssText = 'margin: 0; font-size: 16px; color: white; display: flex; align-items: center; gap: 8px;';
    title.innerHTML = '<span>🤖</span> AI Suggestions';
    
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '×';
    closeButton.style.cssText = `
      background: rgba(255,255,255,0.2);
      border: none;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      color: white;
      cursor: pointer;
      font-size: 16px;
      font-weight: bold;
      transition: all 0.2s ease;
    `;
    closeButton.addEventListener('click', () => this.hidePanel());
    
    header.appendChild(title);
    header.appendChild(closeButton);
    this.suggestionPanel.appendChild(header);
    
    const content = document.createElement('div');
    content.id = 'suggestion-content';
    content.style.cssText = 'min-height: 60px;';
    this.suggestionPanel.appendChild(content);
    
    document.body.appendChild(this.suggestionPanel);
  }

  scheduleAnalysis() {
    if (!this.enabled) return;
    const now = Date.now();
    if (now - this.lastAnalysisTime < this.analysisInterval) return;
    this.lastAnalysisTime = now;
    setTimeout(() => this.analyzeWorkspace(), 500);
  }

  analyzeWorkspace() {
    if (!this.enabled) return;
    const now = Date.now();
    if (now - this.lastSuggestionTime < this.suggestionCooldown) return;
    this.lastSuggestionTime = now;
    this.suggestions = [];
    const blocks = this.workspace.getAllBlocks ? this.workspace.getAllBlocks() : [];
    this.analyzeGameStructure(blocks);
    this.showSuggestions();
  }

  analyzeGameStructure(blocks) {
    const hasGameStart = blocks.some(block => block.type === 'on_game_start');
    if (!hasGameStart) {
      this.addSuggestion({
        id: 'missing_game_start',
        category: 'structure',
        title: 'Add Game Start Event',
        description: 'Every game needs an entry point. Add an "On Game Start" block to initialize your game.',
        priority: 'high',
        action: () => this.insertBlock('on_game_start', 50, 50)
      });
    }
  }

  addSuggestion(suggestion) {
    if (this.suggestionHistory.some(s => s.id === suggestion.id)) return;
    this.suggestions.push(suggestion);
    this.suggestionHistory.push({...suggestion, timestamp: Date.now()});
    if (this.suggestionHistory.length > 50) {
      this.suggestionHistory.shift();
    }
  }

  showSuggestions() {
    if (!this.suggestionPanel || this.suggestions.length === 0) return;
    const content = this.suggestionPanel.querySelector('#suggestion-content');
    if (!content) return;
    const priorityWeights = { high: 0, medium: 1, low: 2 };
    this.suggestions.sort((a, b) => priorityWeights[a.priority] - priorityWeights[b.priority]);
    const displaySuggestions = this.suggestions.slice(0, this.maxSuggestions);
    content.innerHTML = displaySuggestions.map(suggestion => `
      <div class="suggestion-item" style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 10px; margin-bottom: 8px; border-left: 3px solid ${this.getPriorityColor(suggestion.priority)};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
          <strong style="color: white; font-size: 14px;">${suggestion.title}</strong>
          <span style="background: ${this.getPriorityColor(suggestion.priority)}; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px;">${suggestion.priority}</span>
        </div>
        <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 8px; line-height: 1.4;">${suggestion.description}</p>
        <button class="apply-suggestion" data-id="${suggestion.id}" style="background: white; color: #667eea; border: none; border-radius: 15px; padding: 3px 12px; font-size: 11px; cursor: pointer; font-weight: bold; transition: all 0.2s ease;">
          Apply Suggestion
        </button>
      </div>
    `).join('');
    this.setupSuggestionButtons();
    this.suggestionPanel.style.opacity = '1';
    this.suggestionPanel.style.transform = 'translateY(0)';
  }

  setupSuggestionButtons() {
    const content = this.suggestionPanel.querySelector('#suggestion-content');
    content.querySelectorAll('.apply-suggestion').forEach(button => {
      button.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = button.dataset.id;
        const suggestion = this.suggestions.find(s => s.id === id);
        if (suggestion && suggestion.action) {
          suggestion.action();
          this.hideSuggestion(id);
        }
      });
    });
  }

  insertBlock(type, x, y) {
    if (this.workspace.newBlock) {
      const block = this.workspace.newBlock(type);
      block.initSvg?.();
      block.render?.();
      block.moveBy(x, y);
      this.workspace.centerOnBlock?.(block.id);
      block.select?.();
    }
  }

  hideSuggestion(id) {
    this.suggestions = this.suggestions.filter(s => s.id !== id);
    this.suggestionHistory.push({ id, dismissed: true, timestamp: Date.now() });
    if (this.suggestions.length === 0) {
      this.hidePanel();
    } else {
      this.showSuggestions();
    }
  }

  hidePanel() {
    if (this.suggestionPanel) {
      this.suggestionPanel.style.opacity = '0';
      this.suggestionPanel.style.transform = 'translateY(20px)';
      this.suggestions = [];
    }
  }

  getPriorityColor(priority) {
    const colors = { high: '#ff6b6b', medium: '#ffa502', low: '#4ecdc4' };
    return colors[priority] || '#533483';
  }

  dispose() {
    if (this.suggestionPanel && this.suggestionPanel.parentNode) {
      this.suggestionPanel.parentNode.removeChild(this.suggestionPanel);
    }
  }
}

// Initialize on page load
if (typeof workspace !== 'undefined') {
  window.aiSuggestionSystem = new AISuggestionSystem(workspace);
}
