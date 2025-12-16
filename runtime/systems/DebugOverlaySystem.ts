export interface RenderSystem {
  getCameraPosition(): { x: number; y: number };
  getCameraZoom?(): number;
  worldToScreen?(x: number, y: number): { x: number; y: number };
  screenToWorld?(x: number, y: number): { x: number; y: number };
}

export interface Entity {
  id?: string;
  type?: string;
  x: number;
  y: number;
  width?: number;
  height?: number;
  health?: number;
  velocityX?: number;
  velocityY?: number;
  tags?: string[];
}

export interface EntityManager {
  getAllEntities(): Entity[];
  getEntityCount(): number;
  getEntitiesNear?(x: number, y: number, radius: number): Entity[];
}

export interface DebugDrawingOptions {
  color?: string;
  lineWidth?: number;
}

export class DebugOverlaySystem {
  private enabled: boolean = false;
  private showHitboxes: boolean = true;
  private showPerformance: boolean = true;
  private showEntityInfo: boolean = true;
  private renderSystem: RenderSystem | null;
  private entityManager: EntityManager | null;
  private lastFrameTime: number = 0;
  private frameCount: number = 0;
  private fps: number = 60;
  private canvas: HTMLCanvasElement | null;
  private ctx: CanvasRenderingContext2D | null;
  private debugText: Array<{ text: string; x: number; y: number; color: string; size: number }> = [];
  private debugRects: Array<{ x: number; y: number; width: number; height: number; color: string; lineWidth: number }> = [];
  private debugCircles: Array<{ x: number; y: number; radius: number; color: string; lineWidth: number }> = [];
  private debugLines: Array<{ x1: number; y1: number; x2: number; y2: number; color: string; lineWidth: number }> = [];
  private logs: Array<{ timestamp: string; category: string; message: string; color: string }> = [];
  private maxLogs: number = 100;

  constructor(renderSystem: RenderSystem | null, entityManager: EntityManager | null, canvas: HTMLCanvasElement | null) {
    this.renderSystem = renderSystem;
    this.entityManager = entityManager;
    this.canvas = canvas;
    this.ctx = canvas ? canvas.getContext('2d') : null;
    this.setupEventListeners();
    this.init();
  }

  private init(): void {
    const debugOverlay = document.createElement('div');
    debugOverlay.id = 'debug-overlay';
    debugOverlay.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: rgba(22, 33, 62, 0.85);
      color: white;
      padding: 10px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 12px;
      z-index: 1000;
      display: none;
      max-width: 300px;
      max-height: 80vh;
      overflow: auto;
      border: 2px solid #533483;
    `;
    document.body.appendChild(debugOverlay);

    const debugConsole = document.createElement('div');
    debugConsole.id = 'debug-console';
    debugConsole.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      background: rgba(22, 33, 62, 0.9);
      color: white;
      padding: 15px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 12px;
      z-index: 1000;
      display: none;
      min-width: 400px;
      max-height: 300px;
      overflow-y: auto;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
      border: 2px solid #533483;
    `;
    document.body.appendChild(debugConsole);

    this.log('Debug system initialized', 'info');
  }

  private setupEventListeners(): void {
    window.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'F3') {
        this.toggle();
      } else if (e.key === 'F4') {
        this.toggleHitboxes();
      } else if (e.key === 'F5') {
        this.togglePerformance();
      } else if (e.key === 'F6') {
        this.toggleEntityInfo();
      } else if (e.key === 'F7') {
        this.toggleConsole();
      }
    });
  }

  toggle(): boolean {
    this.enabled = !this.enabled;
    const overlay = document.getElementById('debug-overlay') as HTMLDivElement;
    if (overlay) {
      overlay.style.display = this.enabled ? 'block' : 'none';
    }
    this.log(`Debug overlay ${this.enabled ? 'enabled' : 'disabled'}`, 'info');
    return this.enabled;
  }

  toggleHitboxes(): boolean {
    this.showHitboxes = !this.showHitboxes;
    this.log(`Hitboxes ${this.showHitboxes ? 'enabled' : 'disabled'}`, 'info');
    return this.showHitboxes;
  }

  togglePerformance(): boolean {
    this.showPerformance = !this.showPerformance;
    this.log(`Performance metrics ${this.showPerformance ? 'enabled' : 'disabled'}`, 'info');
    return this.showPerformance;
  }

  toggleEntityInfo(): boolean {
    this.showEntityInfo = !this.showEntityInfo;
    this.log(`Entity info ${this.showEntityInfo ? 'enabled' : 'disabled'}`, 'info');
    return this.showEntityInfo;
  }

  toggleConsole(): void {
    const consoleEl = document.getElementById('debug-console') as HTMLDivElement;
    if (consoleEl) {
      consoleEl.style.display = consoleEl.style.display === 'block' ? 'none' : 'block';
      this.log(`Debug console ${consoleEl.style.display === 'block' ? 'shown' : 'hidden'}`, 'info');
    }
  }

  update(deltaTime: number): void {
    if (!this.enabled) return;

    this.frameCount++;
    const now = performance.now();
    if (now - this.lastFrameTime >= 1000) {
      this.fps = this.frameCount;
      this.frameCount = 0;
      this.lastFrameTime = now;
    }

    this.clearDebugDrawings();
  }

  render(): void {
    if (!this.enabled || !this.ctx) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);

    if (this.showHitboxes && this.renderSystem && this.entityManager) {
      this.renderHitboxes();
    }

    if (this.showPerformance) {
      this.renderPerformanceMetrics();
    }

    if (this.showEntityInfo && this.renderSystem && this.entityManager) {
      this.renderEntityInfo();
    }

    this.renderDebugDrawings();

    this.ctx.restore();
  }

  private renderHitboxes(): void {
    if (!this.entityManager?.getAllEntities) return;

    const entities = this.entityManager.getAllEntities();
    const zoom = this.renderSystem?.getCameraZoom?.() ?? 1;

    entities.forEach((entity) => {
      if (!entity.width || !entity.height) return;

      const screenPos = this.renderSystem?.worldToScreen
        ? this.renderSystem.worldToScreen(entity.x, entity.y)
        : { x: entity.x, y: entity.y };

      if (this.ctx) {
        this.ctx.save();
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);

        this.ctx.strokeStyle = entity.tags?.includes('player')
          ? '#3498db'
          : entity.tags?.includes('enemy')
            ? '#e74c3c'
            : entity.tags?.includes('collectible')
              ? '#2ecc71'
              : '#f1c40f';
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
          entity.tags.forEach((tag, index) => {
            this.ctx?.fillText(tag, screenPos.x, screenPos.y - (entity.height! / 2) * zoom + (index * 10) + 10);
          });
        }

        this.ctx.restore();
      }
    });
  }

  private renderPerformanceMetrics(): void {
    if (!this.ctx) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);

    const metrics = [
      `FPS: ${Math.round(this.fps)}`,
      `Entities: ${this.entityManager?.getEntityCount?.() || 'N/A'}`,
      `Memory: ${Math.round((performance as any).memory?.usedJSHeapSize / 1048576 || 0)}MB`,
    ];

    if (this.renderSystem?.getCameraPosition) {
      const pos = this.renderSystem.getCameraPosition();
      metrics.push(`Camera: (${Math.round(pos.x)}, ${Math.round(pos.y)})`);
    }

    if (this.renderSystem?.getCameraZoom) {
      metrics.push(`Zoom: ${this.renderSystem.getCameraZoom().toFixed(2)}`);
    }

    this.ctx.font = '12px Arial';
    this.ctx.fillStyle = '#27ae60';
    this.ctx.textAlign = 'left';

    metrics.forEach((metric, index) => {
      this.ctx?.fillText(metric, 10, 30 + index * 20);
    });

    this.ctx.restore();
  }

  private renderEntityInfo(): void {
    const mousePos = this.getMousePosition();
    if (!mousePos || !this.ctx) return;

    const worldMouse = this.renderSystem?.screenToWorld
      ? this.renderSystem.screenToWorld(mousePos.x, mousePos.y)
      : mousePos;

    const nearbyEntities = this.entityManager?.getEntitiesNear
      ? this.entityManager.getEntitiesNear(worldMouse.x, worldMouse.y, 100)
      : [];

    if (nearbyEntities.length === 0) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);

    const panelX = mousePos.x + 20;
    const panelY = mousePos.y + 20;
    const panelWidth = 200;

    this.ctx.fillStyle = 'rgba(22, 33, 62, 0.85)';
    this.ctx.fillRect(panelX, panelY, panelWidth, nearbyEntities.length * 80 + 20);
    this.ctx.strokeStyle = '#533483';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(panelX, panelY, panelWidth, nearbyEntities.length * 80 + 20);

    this.ctx.font = '14px Arial';
    this.ctx.fillStyle = '#ecf0f1';
    this.ctx.textAlign = 'left';
    this.ctx.fillText('Entity Inspector', panelX + 10, panelY + 20);

    nearbyEntities.forEach((entity, index) => {
      const startY = panelY + 40 + index * 80;

      this.ctx!.font = '12px Arial';
      this.ctx!.fillStyle = '#3498db';
      this.ctx!.fillText(`Type: ${entity.type || 'Unknown'}`, panelX + 10, startY);
      this.ctx!.fillStyle = '#95a5a6';
      this.ctx!.fillText(`ID: ${entity.id || 'N/A'}`, panelX + 10, startY + 15);

      this.ctx!.fillStyle = '#2ecc71';
      this.ctx!.fillText(`Pos: (${Math.round(entity.x)}, ${Math.round(entity.y)})`, panelX + 10, startY + 30);

      if (entity.health !== undefined) {
        this.ctx!.fillStyle = '#e74c3c';
        this.ctx!.fillText(`Health: ${Math.round(entity.health)}`, panelX + 10, startY + 45);
      }

      if (entity.velocityX !== undefined || entity.velocityY !== undefined) {
        this.ctx!.fillStyle = '#9b59b6';
        const velX = entity.velocityX ? Math.round(entity.velocityX) : 0;
        const velY = entity.velocityY ? Math.round(entity.velocityY) : 0;
        this.ctx!.fillText(`Velocity: (${velX}, ${velY})`, panelX + 10, startY + 60);
      }
    });

    this.ctx.restore();
  }

  private getMousePosition(): { x: number; y: number } | null {
    const inputSystem = (window as any).inputSystem;
    if (inputSystem?.getMouseX && inputSystem?.getMouseY) {
      return {
        x: inputSystem.getMouseX(),
        y: inputSystem.getMouseY(),
      };
    }
    return null;
  }

  drawDebugText(text: string, x: number, y: number, color: string = '#ecf0f1', size: number = 12): void {
    if (!this.enabled || !this.ctx) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.font = `${size}px Arial`;
    this.ctx.fillStyle = color;
    this.ctx.textAlign = 'left';
    this.ctx.fillText(text, x, y);
    this.ctx.restore();
  }

  drawDebugRect(
    x: number,
    y: number,
    width: number,
    height: number,
    color: string = '#f1c40f',
    lineWidth: number = 2
  ): void {
    if (!this.enabled || !this.ctx) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = lineWidth;
    this.ctx.strokeRect(x, y, width, height);
    this.ctx.restore();
  }

  drawDebugCircle(x: number, y: number, radius: number, color: string = '#3498db', lineWidth: number = 2): void {
    if (!this.enabled || !this.ctx) return;

    this.ctx.save();
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, Math.PI * 2);
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = lineWidth;
    this.ctx.stroke();
    this.ctx.restore();
  }

  drawDebugLine(x1: number, y1: number, x2: number, y2: number, color: string = '#e74c3c', lineWidth: number = 2): void {
    if (!this.enabled || !this.ctx) return;

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

  private renderDebugDrawings(): void {
    this.debugRects.forEach((rect) => {
      this.drawDebugRect(rect.x, rect.y, rect.width, rect.height, rect.color, rect.lineWidth);
    });

    this.debugCircles.forEach((circle) => {
      this.drawDebugCircle(circle.x, circle.y, circle.radius, circle.color, circle.lineWidth);
    });

    this.debugLines.forEach((line) => {
      this.drawDebugLine(line.x1, line.y1, line.x2, line.y2, line.color, line.lineWidth);
    });

    this.debugText.forEach((text) => {
      this.drawDebugText(text.text, text.x, text.y, text.color, text.size);
    });
  }

  private clearDebugDrawings(): void {
    this.debugRects = [];
    this.debugCircles = [];
    this.debugLines = [];
    this.debugText = [];
  }

  log(message: string, category: string = 'info'): void {
    const timestamp = new Date().toLocaleTimeString();
    const color =
      category === 'error'
        ? '#e74c3c'
        : category === 'warning'
          ? '#f39c12'
          : category === 'success'
            ? '#2ecc71'
            : '#3498db';

    console.log(`[DEBUG] [${timestamp}] [${category.toUpperCase()}] ${message}`);

    this.logs.push({ timestamp, category, message, color });
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    const debugConsole = document.getElementById('debug-console') as HTMLDivElement;
    if (debugConsole && this.enabled) {
      const logEntry = document.createElement('div');
      logEntry.style.marginBottom = '4px';
      logEntry.innerHTML = `[<span style="color: #95a5a6">${timestamp}</span>] [<span style="color: ${color}">${category.toUpperCase()}</span>] ${message}`;
      debugConsole.appendChild(logEntry);
      debugConsole.scrollTop = debugConsole.scrollHeight;
    }

    const overlay = document.getElementById('debug-overlay') as HTMLDivElement;
    if (overlay && this.enabled) {
      overlay.innerHTML = this.logs
        .map(
          (log) =>
            `[<span style="color: #95a5a6">${log.timestamp}</span>] [<span style="color: ${log.color}">${log.category.toUpperCase()}</span>] ${log.message}`
        )
        .join('<br>');
    }
  }

  destroy(): void {
    const overlay = document.getElementById('debug-overlay');
    const debugConsole = document.getElementById('debug-console');
    if (overlay) overlay.remove();
    if (debugConsole) debugConsole.remove();
    this.logs = [];
  }
}

export default DebugOverlaySystem;
