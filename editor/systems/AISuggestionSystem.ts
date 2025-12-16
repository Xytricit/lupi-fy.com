class AISuggestionSystem {
  private workspace: any;
  private suggestions: any[] = [];
  private lastAnalysisTime: number = 0;
  private analysisInterval: number = 2000;
  private suggestionPanel: HTMLElement | null = null;
  private enabled: boolean = true;
  private suggestionHistory: any[] = [];
  private maxSuggestions: number = 5;
  private lastSuggestionTime: number = 0;
  private suggestionCooldown: number = 3000;
  private suggestionContainer: HTMLElement | null = null;

  constructor(workspace: any) {
    this.workspace = workspace;
    this.init();
  }

  private init() {
    this.createSuggestionPanel();
    this.setupEventListeners();
    this.scheduleAnalysis();
  }

  private createSuggestionPanel() {
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
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s;
    `;
    closeButton.addEventListener('click', () => this.hideSuggestions());
    closeButton.addEventListener('mouseover', () => {
      closeButton.style.transform = 'scale(1.2)';
    });
    closeButton.addEventListener('mouseout', () => {
      closeButton.style.transform = 'scale(1)';
    });

    header.appendChild(title);
    header.appendChild(closeButton);

    this.suggestionContainer = document.createElement('div');
    this.suggestionContainer.id = 'ai-suggestion-container';
    this.suggestionContainer.style.cssText = `
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;

    this.suggestionPanel.appendChild(header);
    this.suggestionPanel.appendChild(this.suggestionContainer);
    document.body.appendChild(this.suggestionPanel);
  }

  private setupEventListeners() {
    if (!this.workspace) return;

    document.addEventListener('blockAdded', (e: any) => {
      this.analyzeSuggestions();
    });

    document.addEventListener('blockRemoved', (e: any) => {
      this.analyzeSuggestions();
    });

    document.addEventListener('blockModified', (e: any) => {
      this.analyzeSuggestions();
    });
  }

  private scheduleAnalysis() {
    setInterval(() => {
      if (this.enabled) {
        this.analyzeSuggestions();
      }
    }, this.analysisInterval);
  }

  analyzeSuggestions() {
    const now = Date.now();
    if (now - this.lastAnalysisTime < this.analysisInterval) return;
    this.lastAnalysisTime = now;

    this.suggestions = [];

    if (this.workspace && this.workspace.blocks) {
      this.checkForCommonPatterns();
      this.checkForOptimizations();
      this.checkForBestPractices();
    }

    if (this.suggestions.length > 0 && now - this.lastSuggestionTime > this.suggestionCooldown) {
      this.displaySuggestions();
      this.lastSuggestionTime = now;
    }
  }

  private checkForCommonPatterns() {
    const blocks = this.workspace.blocks || [];
    
    if (blocks.length > 0) {
      const blockTypes = blocks.map((b: any) => b.type);
      
      if (blockTypes.includes('movement') && blockTypes.includes('collision')) {
        this.suggestions.push({
          type: 'pattern',
          title: 'Collision Detection Pattern',
          description: 'Consider adding collision handling after movement blocks',
          severity: 'info',
          action: 'Learn more'
        });
      }

      if (blockTypes.filter((t: any) => t === 'event').length > 3) {
        this.suggestions.push({
          type: 'pattern',
          title: 'Multiple Events Detected',
          description: 'You have many event handlers. Consider consolidating related events',
          severity: 'warning',
          action: 'Optimize'
        });
      }
    }
  }

  private checkForOptimizations() {
    const blocks = this.workspace.blocks || [];
    
    if (blocks.length > 10) {
      this.suggestions.push({
        type: 'optimization',
        title: 'Performance Tip',
        description: 'Consider breaking complex logic into functions or scenes',
        severity: 'info',
        action: 'Refactor'
      });
    }

    const updateBlocks = blocks.filter((b: any) => b.type === 'update').length;
    if (updateBlocks > 5) {
      this.suggestions.push({
        type: 'optimization',
        title: 'Update Loop Heavy',
        description: 'Too many update blocks may impact performance. Consider batching operations',
        severity: 'warning',
        action: 'Optimize'
      });
    }
  }

  private checkForBestPractices() {
    const blocks = this.workspace.blocks || [];
    
    const hasErrorHandling = blocks.some((b: any) => b.type === 'error' || b.type === 'try');
    if (!hasErrorHandling && blocks.length > 5) {
      this.suggestions.push({
        type: 'bestPractice',
        title: 'Error Handling',
        description: 'Add error handling blocks to improve game stability',
        severity: 'info',
        action: 'Add Now'
      });
    }

    const hasComments = blocks.some((b: any) => b.type === 'comment');
    if (!hasComments && blocks.length > 8) {
      this.suggestions.push({
        type: 'bestPractice',
        title: 'Code Documentation',
        description: 'Add comments to explain complex logic for future reference',
        severity: 'info',
        action: 'Document'
      });
    }
  }

  private displaySuggestions() {
    if (!this.suggestionContainer) return;

    this.suggestionContainer.innerHTML = '';

    this.suggestions.slice(0, this.maxSuggestions).forEach((suggestion) => {
      const suggestionEl = document.createElement('div');
      suggestionEl.className = `ai-suggestion-item ai-suggestion-${suggestion.severity}`;
      suggestionEl.style.cssText = `
        padding: 12px;
        background: rgba(255,255,255,0.1);
        border-radius: 6px;
        border-left: 3px solid ${this.getSeverityColor(suggestion.severity)};
        cursor: pointer;
        transition: all 0.2s;
      `;

      const titleEl = document.createElement('div');
      titleEl.style.cssText = 'font-weight: bold; margin-bottom: 5px; font-size: 13px;';
      titleEl.textContent = suggestion.title;

      const descEl = document.createElement('div');
      descEl.style.cssText = 'font-size: 12px; opacity: 0.9; margin-bottom: 8px;';
      descEl.textContent = suggestion.description;

      const actionBtn = document.createElement('button');
      actionBtn.textContent = suggestion.action;
      actionBtn.style.cssText = `
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 11px;
        transition: all 0.2s;
      `;
      actionBtn.addEventListener('mouseover', () => {
        actionBtn.style.background = 'rgba(255,255,255,0.3)';
      });
      actionBtn.addEventListener('mouseout', () => {
        actionBtn.style.background = 'rgba(255,255,255,0.2)';
      });
      actionBtn.addEventListener('click', () => {
        this.handleSuggestionAction(suggestion);
      });

      suggestionEl.appendChild(titleEl);
      suggestionEl.appendChild(descEl);
      suggestionEl.appendChild(actionBtn);

      this.suggestionContainer!.appendChild(suggestionEl);
    });

    this.showSuggestions();
    this.suggestionHistory.push({
      suggestions: this.suggestions,
      timestamp: Date.now()
    });
  }

  private getSeverityColor(severity: string): string {
    const colors: { [key: string]: string } = {
      error: '#ff6b6b',
      warning: '#ffd93d',
      info: '#6bcf7f'
    };
    return colors[severity] || '#6bcf7f';
  }

  private handleSuggestionAction(suggestion: any) {
    console.log('Suggestion action:', suggestion);
    const event = new CustomEvent('aiSuggestionAction', { detail: suggestion });
    document.dispatchEvent(event);
  }

  showSuggestions() {
    if (this.suggestionPanel) {
      this.suggestionPanel.style.opacity = '1';
      this.suggestionPanel.style.transform = 'translateY(0)';
    }
  }

  hideSuggestions() {
    if (this.suggestionPanel) {
      this.suggestionPanel.style.opacity = '0';
      this.suggestionPanel.style.transform = 'translateY(20px)';
    }
  }

  toggleSuggestions() {
    if (this.suggestionPanel) {
      const isVisible = this.suggestionPanel.style.opacity === '1';
      isVisible ? this.hideSuggestions() : this.showSuggestions();
    }
  }

  enable() {
    this.enabled = true;
    console.log('AI Suggestion System enabled');
  }

  disable() {
    this.enabled = false;
    this.hideSuggestions();
    console.log('AI Suggestion System disabled');
  }

  getSuggestions() {
    return [...this.suggestions];
  }

  getSuggestionHistory() {
    return [...this.suggestionHistory];
  }

  clearHistory() {
    this.suggestionHistory = [];
  }
}

export default AISuggestionSystem;
