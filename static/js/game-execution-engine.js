/**
 * LupiForge Game Execution Engine
 * 
 * Converts game logic JSON to Phaser runtime behavior.
 * No magic. No scaffolding. Just execution.
 */

class GameExecutionEngine {
  constructor(phaserScene) {
    this.scene = phaserScene;
    this.objects = {}; // Track spawned objects
    this.objectCounter = 0; // Auto-increment for unique names
    this.timers = []; // Track active timers for cleanup
    this.state = {
      score: 0,
      gameRunning: false
    };
  }

  /**
   * Execute game logic
   * @param {Object} logicJson - { events: [...] }
   */
  run(logicJson) {
    if (!logicJson || !logicJson.events) return;

    const events = logicJson.events;

    // Setup game state
    this.state.gameRunning = true;

    // Register and execute all event handlers
    events.forEach(event => {
      this.registerEvent(event);
    });

    // Fire on_game_start if it exists
    const startEvent = events.find(e => e.type === 'on_game_start');
    if (startEvent) {
      this.executeActions(startEvent.actions || []);
    }
  }

  /**
   * Register event handlers with Phaser
   */
  registerEvent(event) {
    switch (event.type) {
      case 'on_game_start':
        // Already handled in run()
        break;

      case 'on_key_press':
        const key = event.key || 'ArrowRight';
        const keyMap = {
          'left': 'LEFT',
          'right': 'RIGHT',
          'up': 'UP',
          'down': 'DOWN',
          'ArrowLeft': 'LEFT',
          'ArrowRight': 'RIGHT',
          'ArrowUp': 'UP',
          'ArrowDown': 'DOWN',
          'w': 'W',
          'a': 'A',
          's': 'S',
          'd': 'D'
        };
        
        const keyCode = keyMap[key] || key;
        const keyObj = this.scene.input.keyboard.addKey(keyCode);
        
        keyObj.on('down', () => {
          this.executeActions(event.actions || []);
        });
        break;

      case 'on_collision':
        const targetName = event.target || 'collectible';
        // Defer collision setup to first update cycle when objects exist
        if (this.scene.player) {
          this.scene.events.once('update', () => {
            if (this.scene[targetName]) {
              this.scene.physics.add.overlap(
                this.scene.player,
                this.scene[targetName],
                () => {
                  this.executeActions(event.actions || []);
                }
              );
            }
          });
        }
        break;

      case 'on_timer':
        const interval = event.interval || 1000;
        const timer = this.scene.time.addTimer({
          delay: interval,
          loop: true,
          callback: () => {
            this.executeActions(event.actions || []);
          }
        });
        this.timers.push(timer);
        break;
    }
  }

  /**
   * Execute a list of actions
   */
  executeActions(actions) {
    if (!Array.isArray(actions)) return;

    actions.forEach(action => {
      this.executeAction(action);
    });
  }

  /**
   * Execute a single action
   */
  executeAction(action) {
    if (!action || !action.type) return;

    switch (action.type) {
      case 'move_player':
        this.actionMovePlayer(action);
        break;

      case 'spawn_object':
        this.actionSpawnObject(action);
        break;

      case 'destroy_object':
        this.actionDestroyObject(action);
        break;

      case 'add_score':
        this.actionAddScore(action);
        break;

      case 'set_velocity':
        this.actionSetVelocity(action);
        break;
    }
  }

  /**
   * Move player to absolute position
   */
  actionMovePlayer(action) {
    if (!this.scene.player) return;
    
    const x = action.x !== undefined ? action.x : this.scene.player.x;
    const y = action.y !== undefined ? action.y : this.scene.player.y;
    
    this.scene.player.x = x;
    this.scene.player.y = y;
  }

  /**
   * Spawn a new object
   */
  actionSpawnObject(action) {
    const x = action.x || 300;
    const y = action.y || 200;
    const width = action.width || 20;
    const height = action.height || 20;
    const color = action.color || 0xff0000;
    // Auto-generate unique name if not provided
    const name = action.name || `item${++this.objectCounter}`;

    const obj = this.scene.add.rectangle(x, y, width, height, color);
    if (this.scene.physics) {
      this.scene.physics.add.existing(obj);
    }

    this.objects[name] = obj;
    this.scene[name] = obj;
  }

  /**
   * Destroy an object
   */
  actionDestroyObject(action) {
    const name = action.name || 'collectible';
    const obj = this.objects[name] || this.scene[name];
    
    if (obj) {
      obj.destroy();
      delete this.objects[name];
      delete this.scene[name];
    }
  }

  /**
   * Add to score
   */
  actionAddScore(action) {
    const amount = action.amount || 1;
    this.state.score += amount;
  }

  /**
   * Set velocity on player
   */
  actionSetVelocity(action) {
    if (!this.scene.player || !this.scene.player.body) return;
    
    const vx = action.vx || 0;
    const vy = action.vy || 0;
    
    this.scene.player.body.setVelocity(vx, vy);
  }

  /**
   * Get current score
   */
  getScore() {
    return this.state.score;
  }

  /**
   * Reset engine
   */
  reset() {
    this.state = { score: 0, gameRunning: false };
    // Clean up all timers
    this.timers.forEach(timer => {
      if (timer && !timer.paused) {
        this.scene.time.removeTimer(timer);
      }
    });
    this.timers = [];
    // Destroy all spawned objects
    Object.keys(this.objects).forEach(key => {
      if (this.objects[key]) {
        this.objects[key].destroy();
      }
    });
    this.objects = {};
    this.objectCounter = 0;
  }
}

// Export for use in templates
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GameExecutionEngine;
}
