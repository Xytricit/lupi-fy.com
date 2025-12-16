// Prevent duplicate declarations
if (typeof StateStore !== 'undefined') {
  console.log('⚠️ StateStore already defined, skipping redeclaration');
  return;
}

(function() {

  class StateStore {
    constructor() {
      this.gameState = {
        // Core game state
        score: 0,
        health: 100,
        lives: 3,
        level: 1,
        
        // Camera state
        camera: {
          x: 0,
          y: 0,
          targetX: 0,
          targetY: 0,
          zoom: 1,
          smooth: 0.1
        },
        
        // Inventory system
        inventory: {
          slots: Array(20).fill(null),  // Fixed-size inventory
          maxWeight: 100,               // Max weight the player can carry
          gold: 0                      // In-game currency
        },
        
        // Buffs/debuffs
        buffs: {
          // Example: { 'speed_boost': { power: 1.5, expires: 1234567890 } }
        },
      
      // Cooldowns
      cooldowns: {
        // Example: { 'fireball': 1234567890 }
      },
      
      // Game zones/levels
      zones: [
        // { id: 'forest', discovered: true, completed: false, bestTime: 0 }
      ],
      
      // Game entities (enemies, NPCs, etc.)
      entities: [
        // { id: 'enemy1', type: 'goblin', health: 30, x: 100, y: 200 }
      ],
      
      // Game variables (custom variables for game logic)
      variables: {
        // playerName: 'Hero',
        // hasMetWizard: false,
        // quests: { rescuePrincess: 'in_progress' }
      },
      
      // Save slots
      saveSlots: {
        // slot1: { name: 'Save 1', timestamp: 1234567890 },
        // slot2: null,
        // slot3: null
      },
      
      // Game settings
      settings: {
        audio: {
          master: 1.0,  // 0.0 to 1.0
          music: 0.7,
          sfx: 0.9,
          mute: false
        },
        controls: {
          keybinds: {
            up: 'ArrowUp',
            down: 'ArrowDown',
            left: 'ArrowLeft',
            right: 'ArrowRight',
            jump: 'Space',
            interact: 'KeyE'
          },
          invertY: false,
          sensitivity: 1.0
        },
        graphics: {
          quality: 'medium', // 'low', 'medium', 'high'
          vsync: true,
          resolution: { width: 1920, height: 1080 }
        },
        accessibility: {
          colorBlindMode: 'none', // 'protanopia', 'deuteranopia', 'tritanopia'
          textSize: 'medium',     // 'small', 'medium', 'large'
          subtitles: true
        }
      },
      
      // Metadata
      meta: {
        version: '1.0.0',
        lastSaved: null,
        playTime: 0,  // in seconds
        achievements: []
      }
    };
    
    // Versioning for save compatibility
    this.saveVersion = '1.2';
    this.lastSaveTime = 0;
    this.autoSaveInterval = null;
    
    // Event system
    this.listeners = {};
    
    // Load state from localStorage if available
    this.loadState();
    
    // Setup auto-save
    this.setupAutoSave();
    
    // Setup event listeners
    this.setupEventListeners();
  }
  
  // ===== CORE GAME STATE METHODS =====
  
  // Get the entire game state
  getState() {
    return JSON.parse(JSON.stringify(this.gameState));
  }
  
  // Reset the game state to initial values
  resetState() {
    const initialState = new StateStore().gameState;
    this.gameState = JSON.parse(JSON.stringify(initialState));
    this.saveState();
    this.emit('stateReset');
  }
  
  // ===== VARIABLE MANAGEMENT =====
  
  // Set a game variable
  setVariable(key, value) {
    this.gameState.variables[key] = value;
    this.emit('variableChanged', { key, value });
    return this;
  }
  
  // Get a game variable
  getVariable(key, defaultValue = null) {
    return key in this.gameState.variables 
      ? this.gameState.variables[key] 
      : defaultValue;
  }
  
  // Remove a game variable
  removeVariable(key) {
    if (key in this.gameState.variables) {
      delete this.gameState.variables[key];
      this.emit('variableRemoved', { key });
      return true;
    }
    return false;
  }
  
  // ===== SCORE & STATS =====
  
  // Add to score
  addScore(points) {
    if (typeof points !== 'number') return this;
    this.gameState.score = Math.max(0, this.gameState.score + points);
    this.emit('scoreChanged', { score: this.gameState.score, delta: points });
    return this;
  }
  
  // Set score directly
  setScore(value) {
    if (typeof value !== 'number') return this;
    const oldScore = this.gameState.score;
    this.gameState.score = Math.max(0, value);
    this.emit('scoreChanged', { 
      score: this.gameState.score, 
      delta: this.gameState.score - oldScore 
    });
    return this;
  }
  
  // Health management
  setHealth(value) {
    if (typeof value !== 'number') return this;
    const oldHealth = this.gameState.health;
    this.gameState.health = Math.max(0, Math.min(100, value));
    this.emit('healthChanged', { 
      health: this.gameState.health, 
      delta: this.gameState.health - oldHealth 
    });
    return this;
  }
  
  addHealth(amount) {
    return this.setHealth(this.gameState.health + amount);
  }
  
  // Lives management
  setLives(value) {
    if (typeof value !== 'number') return this;
    const oldLives = this.gameState.lives;
    this.gameState.lives = Math.max(0, value);
    this.emit('livesChanged', { 
      lives: this.gameState.lives, 
      delta: this.gameState.lives - oldLives 
    });
    return this;
  }
  
  addLives(amount) {
    return this.setLives(this.gameState.lives + amount);
  }
  
  // ===== INVENTORY SYSTEM =====
  
  // Add item to inventory
  inventoryAdd(item) {
    if (!item || !item.id) return false;
    
    // Check if item is stackable and already in inventory
    if (item.stackable) {
      const existingItem = this.gameState.inventory.slots.find(slot => 
        slot && slot.id === item.id && slot.quantity < (item.maxStack || 99)
      );
      
      if (existingItem) {
        existingItem.quantity += (item.quantity || 1);
        this.emit('inventoryUpdated', { action: 'stacked', item: { ...existingItem } });
        return true;
      }
    }
    
    // Find first empty slot
    const emptySlot = this.gameState.inventory.slots.findIndex(slot => slot === null);
    if (emptySlot === -1) {
      this.emit('inventoryFull', { item });
      return false; // Inventory full
    }
    
    // Add to inventory
    this.gameState.inventory.slots[emptySlot] = { 
      ...item, 
      quantity: item.quantity || 1,
      slot: emptySlot 
    };
    
    this.emit('inventoryUpdated', { 
      action: 'added', 
      item: { ...this.gameState.inventory.slots[emptySlot] } 
    });
    
    return true;
  }
  
  // Remove item from inventory
  inventoryRemove(slotIndex, quantity = 1) {
    if (!this.gameState.inventory.slots[slotIndex]) return false;
    
    const item = this.gameState.inventory.slots[slotIndex];
    
    if (item.quantity <= quantity) {
      // Remove the entire stack
      this.gameState.inventory.slots[slotIndex] = null;
      this.emit('inventoryUpdated', { 
        action: 'removed', 
        item: { ...item, quantity: 0 } 
      });
    } else {
      // Reduce quantity
      item.quantity -= quantity;
      this.emit('inventoryUpdated', { 
        action: 'removed', 
        item: { ...item, quantity: quantity } 
      });
    }
    
    return true;
  }
  
  // Check if inventory has an item
  inventoryHas(itemId, quantity = 1) {
    let total = 0;
    this.gameState.inventory.slots.forEach(slot => {
      if (slot && slot.id === itemId) {
        total += slot.quantity;
      }
    });
    return total >= quantity;
  }
  
  // Get count of a specific item in inventory
  inventoryGetCount(itemId) {
    return this.gameState.inventory.slots.reduce((total, slot) => {
      return slot && slot.id === itemId ? total + slot.quantity : total;
    }, 0);
  }
  
  // Move item between slots
  inventoryMove(fromSlot, toSlot) {
    if (fromSlot === toSlot) return true;
    
    const slots = this.gameState.inventory.slots;
    const fromItem = slots[fromSlot];
    const toItem = slots[toSlot];
    
    // If items are the same and stackable, try to combine
    if (fromItem && toItem && 
        fromItem.id === toItem.id && 
        fromItem.stackable && 
        toItem.stackable) {
      
      const maxStack = fromItem.maxStack || 99;
      const spaceLeft = maxStack - toItem.quantity;
      
      if (spaceLeft > 0) {
        const transferAmount = Math.min(spaceLeft, fromItem.quantity);
        toItem.quantity += transferAmount;
        fromItem.quantity -= transferAmount;
        
        if (fromItem.quantity <= 0) {
          slots[fromSlot] = null;
        }
        
        this.emit('inventoryUpdated', { 
          action: 'moved', 
          fromSlot, 
          toSlot, 
          item: { ...(slots[toSlot] || {}) } 
        });
        
        return true;
      }
    }
    
    // Otherwise, swap the items
    [slots[fromSlot], slots[toSlot]] = [slots[toSlot], slots[fromSlot]];
    
    if (slots[fromSlot]) slots[fromSlot].slot = fromSlot;
    if (slots[toSlot]) slots[toSlot].slot = toSlot;
    
    this.emit('inventoryUpdated', { 
      action: 'swapped', 
      fromSlot, 
      toSlot, 
      fromItem: slots[fromSlot] ? { ...slots[fromSlot] } : null,
      toItem: slots[toSlot] ? { ...slots[toSlot] } : null
    });
    
    return true;
  }
  
  // ===== SAVE/LOAD SYSTEM =====
  
  // Save current state to a slot
  saveGame(slot = 'autosave', name = 'Autosave') {
    const saveData = {
      gameState: this.gameState,
      meta: {
        saveVersion: this.saveVersion,
        timestamp: Date.now(),
        name: name || `Save ${slot}`
      }
    };
    
    // If not autosave, update save slots
    if (slot !== 'autosave') {
      this.gameState.saveSlots[slot] = {
        name: name || `Save ${slot}`,
        timestamp: Date.now(),
        level: this.gameState.level,
        score: this.gameState.score
      };
    }
    
    // Update last saved time
    this.gameState.meta.lastSaved = new Date().toISOString();
    
    // Save to localStorage
    try {
      localStorage.setItem(`lupiforge_save_${slot}`, JSON.stringify(saveData));
      this.lastSaveTime = Date.now();
      this.emit('gameSaved', { slot, name });
      return true;
    } catch (e) {
      console.error('Failed to save game:', e);
      this.emit('saveError', { error: e, slot, name });
      return false;
    }
  }
  
  // Load game from a slot
  loadGame(slot = 'autosave') {
    try {
      const saveData = JSON.parse(localStorage.getItem(`lupiforge_save_${slot}`));
      
      if (!saveData) {
        this.emit('loadError', { error: 'No save data found', slot });
        return false;
      }
      
      // Basic version checking
      if (saveData.meta.saveVersion !== this.saveVersion) {
        console.warn(`Save version mismatch: ${saveData.meta.saveVersion} (current: ${this.saveVersion})`);
        // Could add migration logic here
      }
      
      // Merge the saved state with current state to preserve any new properties
      this.gameState = {
        ...this.gameState, // Current defaults
        ...saveData.gameState, // Saved values
        meta: {
          ...this.gameState.meta, // Current meta defaults
          ...(saveData.gameState?.meta || {}) // Saved meta values
        }
      };
      
      this.emit('gameLoaded', { slot, saveData });
      return true;
      
    } catch (e) {
      console.error('Failed to load game:', e);
      this.emit('loadError', { error: e, slot });
      return false;
    }
  }
  
  // Delete a save slot
  deleteSave(slot) {
    if (slot === 'autosave') return false; // Prevent deleting autosave
    
    try {
      localStorage.removeItem(`lupiforge_save_${slot}`);
      delete this.gameState.saveSlots[slot];
      this.emit('saveDeleted', { slot });
      return true;
    } catch (e) {
      console.error('Failed to delete save:', e);
      return false;
    }
  }
  
  // ===== EVENT SYSTEM =====
  
  // Subscribe to an event
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
    return () => this.off(event, callback);
  }
  
  // Unsubscribe from an event
  off(event, callback) {
    if (!this.listeners[event]) return;
    
    if (callback) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    } else {
      delete this.listeners[event];
    }
  }
  
  // Emit an event
  emit(event, data = {}) {
    if (!this.listeners[event]) return;
    
    // Add timestamp to all events
    const eventData = {
      ...data,
      timestamp: Date.now(),
      event
    };
    
    this.listeners[event].forEach(callback => {
      try {
        callback(eventData);
      } catch (e) {
        console.error(`Error in ${event} handler:`, e);
      }
    });
  }
  
  // ===== PERSISTENCE =====
  
  // Load state from localStorage
  loadState() {
    try {
      const savedState = localStorage.getItem('lupiforge_game_state');
      if (savedState) {
        const parsed = JSON.parse(savedState);
        
        // Basic migration/version checking could go here
        if (parsed.meta && parsed.meta.version === this.saveVersion) {
          this.gameState = {
            ...this.gameState, // Defaults
            ...parsed,         // Saved values
            meta: {
              ...this.gameState.meta,
              ...(parsed.meta || {})
            }
          };
          
          this.emit('stateLoaded');
          return true;
        }
      }
    } catch (e) {
      console.error('Failed to load state:', e);
    }
    return false;
  }
  
  // Save state to localStorage
  saveState() {
    try {
      // Update metadata before saving
      this.gameState.meta.lastSaved = new Date().toISOString();
      
      localStorage.setItem('lupiforge_game_state', JSON.stringify(this.gameState));
      this.lastSaveTime = Date.now();
      this.emit('stateSaved');
      return true;
    } catch (e) {
      console.error('Failed to save state:', e);
      this.emit('saveError', { error: e });
      return false;
    }
  }
  
  // ===== UTILITY METHODS =====
  
  // Setup auto-save
  setupAutoSave(interval = 30000) {
    // Clear existing interval if any
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    
    // Set up new interval
    if (interval > 0) {
      this.autoSaveInterval = setInterval(() => {
        this.saveState();
        this.saveGame('autosave');
      }, interval);
    }
  }
  
  // Setup event listeners
  setupEventListeners() {
    // Auto-save when page is about to unload
    window.addEventListener('beforeunload', () => {
      this.saveState();
      this.saveGame('autosave');
    });
    
    // Example of listening to game events
    this.on('healthChanged', ({ health, delta }) => {
      if (health <= 0) {
        this.emit('playerDeath');
      }
    });
    
    this.on('playerDeath', () => {
      // Handle player death (e.g., show game over screen)
      console.log('Player died!');
    });
  }
  
  // Cleanup
  destroy() {
    // Clear intervals
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    
    // Remove event listeners
    window.removeEventListener('beforeunload', this.saveState);
    
    // Clear all event listeners
    this.listeners = {};
  }
}

  window.StateStore = StateStore;
  console.log('✅ StateStore loaded');
  
  // Create a singleton instance
  if (typeof window.stateStore === 'undefined') {
    window.stateStore = new StateStore();
  }
})();

// Expose for CommonJS/Node.js
if (typeof module !== 'undefined' && module.exports && typeof StateStore !== 'undefined') {
  module.exports = StateStore;
}
