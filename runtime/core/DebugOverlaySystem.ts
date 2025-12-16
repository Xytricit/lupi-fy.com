class DebugOverlaySystem {
  private enabled: boolean = false;
  private showHitboxes: boolean = true;
  private showPerformance: boolean = true;
  private showEntityInfo: boolean = true;
  private renderSystem: any;
  private entityManager: any;
  private lastFrameTime: number = 0;
  private frameCount: number = 0;
  private fps: number = 60;
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;

  constructor(renderSystem: any, entityManager: any, canvas: HTMLCanvasElement) {
    this.renderSystem = renderSystem;
    this.entityManager = entityManager;
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.setupEventListeners();
  }

  private setupEventListeners() {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'F3') {
        this.toggle();
      } else if (e.key === 'F4') {
        this.toggleHitboxes();
      } else if (e.key === 'F5') {
        this.togglePerformance();
      } else if (e.key === 'F6') {
        this.toggleEntityInfo();
      }
    });
  }

  toggle() {
    this.enabled = !this.enabled;
    console.log(`Debug overlay ${this.enabled ? 'enabled' : 'disabled'}`);
    return this.enabled;
  }

  toggleHitboxes() {
    this.showHitboxes = !this.showHitboxes;
    console.log(`Hitboxes ${this.showHitboxes ? 'enabled' : 'disabled'}`);
    return this.showHitboxes;
  }

  togglePerformance() {
    this.showPerformance = !this.showPerformance;
    console.log(`Performance metrics ${this.showPerformance ? 'enabled' : 'disabled'}`);
    return this.showPerformance;
  }

  toggleEntityInfo() {
    this.showEntityInfo = !this.showEntityInfo;
    console.log(`Entity info ${this.showEntityInfo ? 'enabled' : 'disabled'}`);
    return this.showEntityInfo;
  }

  update(deltaTime: number) {
    if (!this.enabled) return;
    
    this.frameCount++;
    const now = performance.now();
    if (now - this.lastFrameTime >= 1000) {
      this.fps = this.frameCount;
      this.frameCount = 0;
      this.lastFrameTime = now;
    }
  }

  render() {
    if (!this.enabled) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    if (this.showHitboxes) {
      this.renderHitboxes();
    }
    
    if (this.showPerformance) {
      this.renderPerformanceMetrics();
    }
    
    if (this.showEntityInfo) {
      this.renderEntityInfo();
    }
    
    this.ctx.restore();
  }

  private renderHitboxes() {
    const entities = this.entityManager.getAllEntities();
    const camera = this.renderSystem.getCameraPosition();
    const zoom = this.renderSystem.getCameraZoom();
    
    entities.forEach(entity => {
      if (!entity.width || !entity.height) return;
      
      const screenPos = this.renderSystem.worldToScreen(entity.x, entity.y);
      
      this.ctx.save();
      this.ctx.setTransform(1, 0, 0, 1, 0, 0);
      
      this.ctx.strokeStyle = entity.tags?.includes('player') ? '#3498db' : 
                             entity.tags?.includes('enemy') ? '#e74c3c' : 
                             entity.tags?.includes('collectible') ? '#2ecc71' : '#f1c40f';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(
        screenPos.x - (entity.width / 2) * zoom,
        screenPos.y - (entity.height / 2) * zoom,
        entity.width * zoom,
        entity.height * zoom
      );
      
      this.ctx.font = '10px Arial';
      this.ctx.fillStyle = this.ctx.strokeStyle;
      this.ctx.textAlign = 'center';
      this.ctx.fillText(
        entity.id ? `ID: ${entity.id}` : entity.type || 'Entity',
        screenPos.x,
        screenPos.y - (entity.height / 2) * zoom - 5
      );
      
      if (entity.tags && entity.tags.length > 0) {
        this.ctx.font = '8px Arial';
        this.ctx.fillStyle = '#ecf0f1';
        entity.tags.forEach((tag: string, index: number) => {
          this.ctx.fillText(
            tag,
            screenPos.x,
            screenPos.y - (entity.height / 2) * zoom + (index * 10) + 10
          );
        });
      }
      
      this.ctx.restore();
    });
  }

  private renderPerformanceMetrics() {
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    const metrics = [
      `FPS: ${Math.round(this.fps)}`,
      `Entities: ${this.entityManager.getEntityCount()}`,
      `Camera: (${Math.round(this.renderSystem.getCameraPosition().x)}, ${Math.round(this.renderSystem.getCameraPosition().y)})`,
      `Zoom: ${this.renderSystem.getCameraZoom().toFixed(2)}`
    ];
    
    this.ctx.font = '12px Arial';
    this.ctx.fillStyle = '#27ae60';
    this.ctx.textAlign = 'left';
    
    metrics.forEach((metric, index) => {
      this.ctx.fillText(metric, 10, 30 + (index * 20));
    });
    
    if ((performance as any).memory) {
      const usedMB = Math.round((performance as any).memory.usedJSHeapSize / 1048576);
      const totalMB = Math.round((performance as any).memory.totalJSHeapSize / 1048576);
      this.ctx.fillText(`Memory: ${usedMB}/${totalMB} MB`, 10, 30 + (metrics.length * 20));
    }
    
    this.ctx.restore();
  }

  private renderEntityInfo() {
    const mousePos = this.getMousePosition();
    if (!mousePos) return;
    
    const worldMouse = this.renderSystem.screenToWorld(mousePos.x, mousePos.y);
    const nearbyEntities = this.entityManager.getEntitiesNear(worldMouse.x, worldMouse.y, 100);
    
    if (nearbyEntities.length === 0) return;
    
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    const panelX = mousePos.x + 20;
    const panelY = mousePos.y + 20;
    const panelWidth = 200;
    const lineHeight = 18;
    
    this.ctx.fillStyle = 'rgba(22, 33, 62, 0.85)';
    this.ctx.fillRect(panelX, panelY, panelWidth, (nearbyEntities.length * 80) + 20);
    this.ctx.strokeStyle = '#533483';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(panelX, panelY, panelWidth, (nearbyEntities.length * 80) + 20);
    
    this.ctx.font = '14px Arial';
    this.ctx.fillStyle = '#ecf0f1';
    this.ctx.textAlign = 'left';
    this.ctx.fillText('Entity Inspector', panelX + 10, panelY + 20);
    
    nearbyEntities.forEach((entity, index) => {
      const startY = panelY + 40 + (index * 80);
      
      this.ctx.font = '12px Arial';
      this.ctx.fillStyle = '#3498db';
      this.ctx.fillText(`Type: ${entity.type || 'Unknown'}`, panelX + 10, startY);
      this.ctx.fillStyle = '#95a5a6';
      this.ctx.fillText(`ID: ${entity.id || 'N/A'}`, panelX + 10, startY + 15);
      
      this.ctx.fillStyle = '#2ecc71';
      this.ctx.fillText(`Pos: (${Math.round(entity.x)}, ${Math.round(entity.y)})`, panelX + 10, startY + 30);
      
      if (entity.health !== undefined) {
        this.ctx.fillStyle = '#e74c3c';
        this.ctx.fillText(`Health: ${Math.round(entity.health)}`, panelX + 10, startY + 45);
      }
      
      if (entity.velocityX !== undefined || entity.velocityY !== undefined) {
        this.ctx.fillStyle = '#9b59b6';
        const velX = entity.velocityX ? Math.round(entity.velocityX) : 0;
        const velY = entity.velocityY ? Math.round(entity.velocityY) : 0;
        this.ctx.fillText(`Velocity: (${velX}, ${velY})`, panelX + 10, startY + 60);
      }
    });
    
    this.ctx.restore();
  }

  private getMousePosition(): { x: number, y: number } | null {
    if (typeof (window as any).inputSystem !== 'undefined') {
      return {
        x: (window as any).inputSystem.getMouseX(),
        y: (window as any).inputSystem.getMouseY()
      };
    }
    return null;
  }

  drawDebugText(text: string, x: number, y: number, color: string = '#ecf0f1', size: number = 12) {
    if (!this.enabled) return;
    
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.font = `${size}px Arial`;
    this.ctx.fillStyle = color;
    this.ctx.textAlign = 'left';
    this.ctx.fillText(text, x, y);
    this.ctx.restore();
  }

  drawDebugRect(x: number, y: number, width: number, height: number, color: string = '#f1c40f', lineWidth: number = 2) {
    if (!this.enabled) return;
    
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = lineWidth;
    this.ctx.strokeRect(x, y, width, height);
    this.ctx.restore();
  }

  drawDebugCircle(x: number, y: number, radius: number, color: string = '#3498db', lineWidth: number = 2) {
    if (!this.enabled) return;
    
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, Math.PI * 2);
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = lineWidth;
    this.ctx.stroke();
    this.ctx.restore();
  }

  drawDebugLine(x1: number, y1: number, x2: number, y2: number, color: string = '#e74c3c', lineWidth: number = 2) {
    if (!this.enabled) return;
    
    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = lineWidth;
    this.ctx.stroke();
    this.ctx.restore();
  }

  log(message: string, category: string = 'info') {
    if (!this.enabled) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const color = category === 'error' ? '#e74c3c' : 
                 category === 'warning' ? '#f39c12' : 
                 category === 'success' ? '#2ecc71' : '#3498db';
    
    console.log(`[DEBUG] [${timestamp}] [${category.toUpperCase()}] ${message}`);
  }

  drawGrid(size: number = 32, color: string = 'rgba(255, 255, 255, 0.1)', majorLineColor: string = 'rgba(255, 255, 255, 0.3)') {
    if (!this.enabled) return;
    
    const camera = this.renderSystem.getCameraPosition();
    const zoom = this.renderSystem.getCameraZoom();
    const width = this.canvas.width / zoom;
    const height = this.canvas.height / zoom;
    
    this.ctx.save();
    this.ctx.translate(-camera.x, -camera.y);
    this.ctx.scale(zoom, zoom);
    
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 1;
    
    for (let x = Math.floor(camera.x / size) * size; x < camera.x + width; x += size) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, camera.y);
      this.ctx.lineTo(x, camera.y + height);
      
      if (Math.abs(x) % (size * 10) === 0) {
        this.ctx.strokeStyle = majorLineColor;
        this.ctx.lineWidth = 2;
      } else {
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1;
      }
      
      this.ctx.stroke();
    }
    
    for (let y = Math.floor(camera.y / size) * size; y < camera.y + height; y += size) {
      this.ctx.beginPath();
      this.ctx.moveTo(camera.x, y);
      this.ctx.lineTo(camera.x + width, y);
      
      if (Math.abs(y) % (size * 10) === 0) {
        this.ctx.strokeStyle = majorLineColor;
        this.ctx.lineWidth = 2;
      } else {
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1;
      }
      
      this.ctx.stroke();
    }
    
    this.ctx.restore();
  }
}

export function toggleDebugOverlay() {
  if (!debugOverlaySystem) return false;
  return debugOverlaySystem.toggle();
}

export function isDebugOverlayEnabled() {
  return (debugOverlaySystem as any)?.enabled || false;
}

export function logDebug(message: string, category: string = 'info') {
  if (debugOverlaySystem) {
    debugOverlaySystem.log(message, category);
  }
}

let debugOverlaySystem: DebugOverlaySystem | null = null;

export default DebugOverlaySystem;
