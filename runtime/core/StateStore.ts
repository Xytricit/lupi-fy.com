class StateStore {
  private state: Record<string, any> = {};
  private settings: Record<string, any> = {};
  private saveSlots: Record<number, any> = {};
  private autosaveInterval: number | null = null;
  private lastSaveTime: number = 0;
  private readonly SAVE_VERSION = '1.2';
  private readonly MAX_SAVE_SLOTS = 5;
  private readonly AUTOSAVE_INTERVAL = 60000;

  constructor() {
    this.loadState();
    this.loadSettings();
    this.initAutosave();
    this.setupEventListeners();
  }

  setState(key: string, value: any) {
    this.state[key] = value;

    if (key === 'achievements') {
      this.handleAchievementUnlock(value);
    }

    this.emitStateChange(key, value);
  }

  getState(key: string, defaultValue: any = null): any {
    return this.state[key] !== undefined ? this.state[key] : defaultValue;
  }

  getStateSnapshot(): Record<string, any> {
    return { ...this.state };
  }

  clearState() {
    this.state = {};
    this.emitStateChange('all', null);
  }

  setSetting(key: string, value: any) {
    this.settings[key] = value;

    if (key === 'volume') {
      this.handleVolumeChange(value);
    } else if (key === 'theme') {
      this.handleThemeChange(value);
    } else if (key === 'language') {
      this.handleLanguageChange(value);
    }

    this.saveSettings();
    this.emitSettingChange(key, value);
  }

  getSetting(key: string, defaultValue: any = null): any {
    return this.settings[key] !== undefined ? this.settings[key] : defaultValue;
  }

  getSettingsSnapshot(): Record<string, any> {
    return { ...this.settings };
  }

  resetSettings() {
    this.settings = {
      volume: 0.8,
      musicVolume: 0.7,
      effectsVolume: 0.9,
      fullscreen: false,
      theme: 'dark',
      language: 'en',
      accessibility: {
        colorBlindMode: false,
        highContrast: false,
        textToSpeech: false
      },
      controls: {
        invertY: false,
        sensitivity: 1.0,
        vibration: true,
        touchControls: true
      },
      notifications: {
        achievements: true,
        messages: true,
        gameUpdates: true
      },
      performance: {
        quality: 'auto',
        vsync: true,
        frameRateLimit: 60
      },
      privacy: {
        shareData: true,
        allowAnalytics: true
      }
    };
    this.saveSettings();
    this.emitSettingChange('all', this.settings);
  }

  saveGame(slot: number = 1, metadata: Record<string, any> = {}): boolean {
    if (slot < 1 || slot > this.MAX_SAVE_SLOTS) {
      console.error(`Invalid save slot: ${slot}. Must be between 1 and ${this.MAX_SAVE_SLOTS}`);
      return false;
    }

    try {
      const saveData = {
        version: this.SAVE_VERSION,
        timestamp: Date.now(),
        state: this.getStateSnapshot(),
        metadata: {
          ...metadata,
          playTime: (metadata.playTime || 0) + this.getPlayTimeSinceLastSave()
        }
      };

      this.saveSlots[slot] = saveData;
      this.lastSaveTime = Date.now();

      this.saveToStorage();
      this.emitSaveEvent(slot, 'saved');

      return true;
    } catch (error) {
      console.error('Failed to save game:', error);
      this.emitSaveEvent(slot, 'error', (error as Error).message);
      return false;
    }
  }

  loadGame(slot: number = 1): boolean {
    if (slot < 1 || slot > this.MAX_SAVE_SLOTS) {
      console.error(`Invalid load slot: ${slot}. Must be between 1 and ${this.MAX_SAVE_SLOTS}`);
      return false;
    }

    if (!this.saveSlots[slot]) {
      console.warn(`No save data found in slot ${slot}`);
      return false;
    }

    try {
      const saveData = this.saveSlots[slot];

      if (saveData.version !== this.SAVE_VERSION) {
        console.warn(`Save version mismatch: ${saveData.version} vs ${this.SAVE_VERSION}`);
      }

      this.state = { ...saveData.state };
      this.emitSaveEvent(slot, 'loaded');
      this.emitStateChange('all', this.state);

      return true;
    } catch (error) {
      console.error('Failed to load game:', error);
      this.emitSaveEvent(slot, 'error', (error as Error).message);
      return false;
    }
  }

  deleteSave(slot: number): boolean {
    if (slot < 1 || slot > this.MAX_SAVE_SLOTS) {
      console.error(`Invalid delete slot: ${slot}. Must be between 1 and ${this.MAX_SAVE_SLOTS}`);
      return false;
    }

    if (this.saveSlots[slot]) {
      delete this.saveSlots[slot];
      this.saveToStorage();
      this.emitSaveEvent(slot, 'deleted');
      return true;
    }

    console.warn(`No save data to delete in slot ${slot}`);
    return false;
  }

  getSaveInfo(slot: number): any {
    if (slot < 1 || slot > this.MAX_SAVE_SLOTS) return null;
    return this.saveSlots[slot] ? {
      timestamp: this.saveSlots[slot].timestamp,
      metadata: this.saveSlots[slot].metadata
    } : null;
  }

  saveSettings() {
    try {
      const serialized = JSON.stringify({
        version: this.SAVE_VERSION,
        timestamp: Date.now(),
        settings: this.settings
      });

      localStorage.setItem('lupiforge_settings', serialized);
      this.emitSettingChange('saved', this.settings);

      return true;
    } catch (error) {
      console.error('Failed to save settings:', error);
      return false;
    }
  }

  loadSettings() {
    try {
      const saved = localStorage.getItem('lupiforge_settings');
      if (saved) {
        const parsed = JSON.parse(saved);

        if (parsed.version === this.SAVE_VERSION) {
          this.settings = parsed.settings;
          this.emitSettingChange('loaded', this.settings);
        } else {
          console.warn('Settings version mismatch, resetting to defaults');
          this.resetSettings();
        }
      } else {
        this.resetSettings();
      }

      return true;
    } catch (error) {
      console.error('Failed to load settings:', error);
      this.resetSettings();
      return false;
    }
  }

  saveState() {
    try {
      const serialized = JSON.stringify({
        version: this.SAVE_VERSION,
        timestamp: Date.now(),
        state: this.state,
        saveSlots: this.saveSlots
      });

      localStorage.setItem('lupiforge_state', serialized);
      this.emitStateChange('saved', this.state);

      return true;
    } catch (error) {
      console.error('Failed to save state:', error);
      return false;
    }
  }

  loadState() {
    try {
      const saved = localStorage.getItem('lupiforge_state');
      if (saved) {
        const parsed = JSON.parse(saved);

        if (parsed.version === this.SAVE_VERSION) {
          this.state = parsed.state || {};
          this.saveSlots = parsed.saveSlots || {};
          this.emitStateChange('loaded', this.state);
        } else {
          console.warn('State version mismatch, starting fresh');
          this.state = {};
          this.saveSlots = {};
        }
      } else {
        this.state = {};
        this.saveSlots = {};
      }

      return true;
    } catch (error) {
      console.error('Failed to load state:', error);
      this.state = {};
      this.saveSlots = {};
      return false;
    }
  }

  initAutosave() {
    if (this.autosaveInterval) {
      clearInterval(this.autosaveInterval);
    }

    this.autosaveInterval = window.setInterval(() => {
      this.autosave();
    }, this.AUTOSAVE_INTERVAL);
  }

  autosave() {
    if (Date.now() - this.lastSaveTime > 5000) {
      this.saveGame(1, {
        autosave: true,
        playTime: this.getPlayTimeSinceLastSave()
      });
    }
  }

  disableAutosave() {
    if (this.autosaveInterval) {
      clearInterval(this.autosaveInterval);
      this.autosaveInterval = null;
    }
  }

  enableAutosave() {
    this.initAutosave();
  }

  getPlayTimeSinceLastSave(): number {
    return (Date.now() - this.lastSaveTime) / 1000;
  }

  private eventListeners: Record<string, Function[]> = {
    stateChange: [],
    settingChange: [],
    saveEvent: [],
    achievement: []
  };

  on(eventType: string, callback: Function) {
    if (!this.eventListeners[eventType]) {
      this.eventListeners[eventType] = [];
    }
    this.eventListeners[eventType].push(callback);
  }

  off(eventType: string, callback: Function) {
    if (this.eventListeners[eventType]) {
      this.eventListeners[eventType] = this.eventListeners[eventType].filter(cb => cb !== callback);
    }
  }

  private emitStateChange(key: string, value: any) {
    this.eventListeners.stateChange.forEach(callback => {
      callback({ key, value, state: this.state });
    });
  }

  private emitSettingChange(key: string, value: any) {
    this.eventListeners.settingChange.forEach(callback => {
      callback({ key, value, settings: this.settings });
    });
  }

  private emitSaveEvent(slot: number, type: string, error?: string) {
    this.eventListeners.saveEvent.forEach(callback => {
      callback({ slot, type, error, saveSlots: this.saveSlots });
    });
  }

  private emitAchievementUnlock(achievement: any) {
    this.eventListeners.achievement.forEach(callback => {
      callback(achievement);
    });
  }

  private handleAchievementUnlock(achievementData: any) {
    console.log('Achievement unlocked:', achievementData);
  }

  private handleVolumeChange(volume: number) {
    console.log('Volume changed to:', volume);
  }

  private handleThemeChange(theme: string) {
    document.body.setAttribute('data-theme', theme);
    console.log('Theme changed to:', theme);
  }

  private handleLanguageChange(language: string) {
    console.log('Language changed to:', language);
  }

  private setupEventListeners() {
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.saveState();
        this.saveSettings();
      });
    }
  }

  private saveToStorage() {
    try {
      const serialized = JSON.stringify({
        version: this.SAVE_VERSION,
        timestamp: Date.now(),
        saveSlots: this.saveSlots
      });

      localStorage.setItem('lupiforge_saves', serialized);
      return true;
    } catch (error) {
      console.error('Failed to save to storage:', error);
      return false;
    }
  }

  getSaveSlots(): Record<number, any> {
    return { ...this.saveSlots };
  }

  exportSaveData(slot: number): string | null {
    if (slot < 1 || slot > this.MAX_SAVE_SLOTS) return null;
    const save = this.saveSlots[slot];
    if (!save) return null;

    return JSON.stringify(save, null, 2);
  }

  importSaveData(slot: number, data: string): boolean {
    if (slot < 1 || slot > this.MAX_SAVE_SLOTS) return false;

    try {
      const parsed = JSON.parse(data);
      if (!parsed.version || !parsed.state) return false;

      this.saveSlots[slot] = parsed;
      this.saveToStorage();
      this.emitSaveEvent(slot, 'imported');

      return true;
    } catch (error) {
      console.error('Failed to import save data:', error);
      return false;
    }
  }

  getAllSaves(): Array<{ slot: number; data: any }> {
    return Object.entries(this.saveSlots).map(([slot, data]) => ({
      slot: parseInt(slot),
      data
    }));
  }

  clearAllSaves(): boolean {
    this.saveSlots = {};
    this.saveToStorage();
    this.emitSaveEvent(0, 'cleared');
    return true;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = StateStore;
}
