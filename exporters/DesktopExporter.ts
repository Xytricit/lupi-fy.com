import { ProjectData } from '../types/project';
import { AssetManager } from '../core/AssetManager';
import { GameRuntime } from '../runtime/GameRuntime';
import { ASTCompiler } from '../compiler/ASTCompiler';
import { createZip } from '../utils/zipUtils';
import { exportSettings } from '../config/exportSettings';

interface ExportOptions {
  optimize?: boolean;
  debug?: boolean;
}

export class DesktopExporter {
  private projectData: ProjectData;
  private runtime: GameRuntime;
  private compiler: ASTCompiler;
  
  constructor(projectData: ProjectData) {
    this.projectData = projectData;
    this.runtime = new GameRuntime();
    this.compiler = new ASTCompiler({ platform: 'desktop' });
  }

  async export(exportType: 'windows' | 'mac' | 'linux', exportOptions: ExportOptions = {}): Promise<Blob> {
    try {
      this.validateProject();
      
      const compiledCode = this.compiler.compile(this.projectData.blocks, {
        platform: 'desktop',
        target: exportType,
        optimize: exportOptions.optimize || true,
        debugSymbols: exportOptions.debug || false
      });
      
      const assets = await this.collectAssets();
      const files = await this.generateProjectFiles(exportType, compiledCode, assets, exportOptions);
      
      return await this.packageFiles(files, exportType);
    } catch (error) {
      console.error(`Desktop export failed: ${error.message}`);
      throw new Error(`Export failed: ${error.message}`);
    }
  }
  
  private validateProject(): void {
    if (!this.projectData.blocks || this.projectData.blocks.length === 0) {
      throw new Error('Project has no blocks. Add game logic before exporting.');
    }
    
    if (!this.projectData.settings.gameTitle || this.projectData.settings.gameTitle.trim() === '') {
      throw new Error('Game title is required for export. Set a title in project settings.');
    }
    
    const hasPlayerMovement = this.projectData.blocks.some(
      block => block.type === 'move_player' || block.type === 'set_velocity'
    );
    
    if (!hasPlayerMovement) {
      throw new Error('Game needs player movement logic. Add movement blocks before exporting.');
    }
  }
  
  private async collectAssets(): Promise<Record<string, Blob>> {
    const assets: Record<string, Blob> = {};
    
    const spriteAssets = AssetManager.getAssetsByType('sprites');
    for (const asset of spriteAssets) {
      if (this.isAssetUsed(asset.id)) {
        assets[asset.path] = await AssetManager.getAssetBlob(asset.id);
      }
    }
    
    const soundAssets = AssetManager.getAssetsByType('sounds');
    for (const asset of soundAssets) {
      if (this.isAssetUsed(asset.id)) {
        assets[asset.path] = await AssetManager.getAssetBlob(asset.id);
      }
    }
    
    const backgroundAssets = AssetManager.getAssetsByType('backgrounds');
    for (const asset of backgroundAssets) {
      if (this.isAssetUsed(asset.id)) {
        assets[asset.path] = await AssetManager.getAssetBlob(asset.id);
      }
    }
    
    return assets;
  }
  
  private isAssetUsed(assetId: string): boolean {
    return this.projectData.blocks.some(block => {
      if (block.inputs) {
        return Object.values(block.inputs).some(input => 
          input === assetId || (typeof input === 'object' && input?.value === assetId)
        );
      }
      return false;
    });
  }
  
  private async generateProjectFiles(
    platform: 'windows' | 'mac' | 'linux',
    compiledCode: string,
    assets: Record<string, Blob>,
    options: ExportOptions
  ): Promise<Record<string, string | Blob>> {
    const files: Record<string, string | Blob> = {};
    const gameTitle = this.projectData.settings.gameTitle.replace(/[^\w\s-]/g, '').trim();
    const safeGameTitle = gameTitle.replace(/\s+/g, '_');
    const projectVersion = this.projectData.settings.version || '1.0.0';
    
    files[platform === 'mac' ? 'Game.app/Contents/Resources/game.js' : 'game.js'] = this.generateMainGameFile(
      compiledCode,
      options
    );
    
    switch (platform) {
      case 'windows':
        files['index.html'] = this.generateHTMLWrapper(gameTitle, projectVersion);
        files['package.json'] = this.generatePackageJSON(gameTitle, projectVersion, 'windows');
        files['main.js'] = this.generateElectronMain('windows');
        break;
      case 'mac':
        files['Game.app/Contents/Info.plist'] = this.generateMacPlist(gameTitle, projectVersion);
        files['Game.app/Contents/MacOS/game'] = this.generateMacExecutableStub();
        files['Game.app/Contents/Resources/package.json'] = this.generatePackageJSON(gameTitle, projectVersion, 'mac');
        files['Game.app/Contents/Resources/main.js'] = this.generateElectronMain('mac');
        break;
      case 'linux':
        files['index.html'] = this.generateHTMLWrapper(gameTitle, projectVersion);
        files['package.json'] = this.generatePackageJSON(gameTitle, projectVersion, 'linux');
        files['main.js'] = this.generateElectronMain('linux');
        files[`${safeGameTitle.toLowerCase()}.desktop`] = this.generateLinuxDesktopFile(gameTitle, safeGameTitle);
        break;
    }
    
    Object.entries(assets).forEach(([path, blob]) => {
      files[path] = blob;
    });
    
    await this.addPlatformIcons(files, platform, gameTitle);
    
    files['lupiforge.config.json'] = JSON.stringify({
      gameTitle: gameTitle,
      version: projectVersion,
      exportPlatform: platform,
      exportDate: new Date().toISOString(),
      settings: this.projectData.settings
    }, null, 2);
    
    return files;
  }
  
  private generateMainGameFile(compiledCode: string, options: ExportOptions): string {
    const gameSettings = this.projectData.settings;
    const optimizedCode = options.optimize ? this.optimizeCode(compiledCode) : compiledCode;
    
    return `// Lupiforge Game Engine - Auto-generated Game Code
// Game: ${gameSettings.gameTitle}
// Version: ${gameSettings.version || '1.0.0'}
// Exported: ${new Date().toISOString()}

// Engine initialization
const engine = new LupiforgeEngine({
  width: ${gameSettings.resolution?.width || 800},
  height: ${gameSettings.resolution?.height || 600},
  fullscreen: ${gameSettings.fullscreen || false},
  antialias: ${gameSettings.antialias !== false},
  physics: {
    gravity: ${gameSettings.physics?.gravity || 9.8},
    friction: ${gameSettings.physics?.friction || 0.8}
  }
});

// Game logic compiled from blocks
${optimizedCode}

// Start the game engine
engine.start();
`;
  }
  
  private generateHTMLWrapper(title: string, version: string): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} v${version}</title>
  <style>
    body { 
      margin: 0; 
      overflow: hidden; 
      background: #000; 
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    #gameCanvas { 
      display: block;
      box-shadow: 0 0 20px rgba(0,0,0,0.5);
      max-width: 95vw;
      max-height: 95vh;
    }
    #loading {
      position: absolute;
      color: white;
      font-family: Arial, sans-serif;
      font-size: 18px;
    }
  </style>
</head>
<body>
  <div id="loading">Loading ${title}...</div>
  <canvas id="gameCanvas"></canvas>
  <script src="./engine.bundle.js"></script>
  <script src="./game.js"></script>
</body>
</html>`;
  }
  
  private generateElectronMain(platform: 'windows' | 'mac' | 'linux'): string {
    return `const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  const windowOptions = {
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      devTools: false
    },
    icon: path.join(__dirname, 'icon${platform === 'windows' ? '.ico' : '.png'}')
  };
  
  if (process.platform === 'darwin' && require('electron-squirrel-startup')) {
    app.quit();
    return;
  }
  
  mainWindow = new BrowserWindow(windowOptions);
  Menu.setApplicationMenu(null);
  mainWindow.loadFile('index.html');
  
  if (process.env.DEBUG_GAME) {
    mainWindow.webContents.openDevTools();
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

process.on('uncaughtException', (error) => {
  console.error('Game crashed:', error);
  if (mainWindow) {
    mainWindow.webContents.send('game-crashed', error.message);
  }
  app.exit(1);
});`;
  }
  
  private generatePackageJSON(title: string, version: string, platform: string): string {
    return JSON.stringify({
      name: title.toLowerCase().replace(/\s+/g, '-'),
      version: version,
      description: `${title} - Created with Lupiforge`,
      main: 'main.js',
      scripts: {
        start: 'electron .',
        package: platform === 'windows' 
          ? 'electron-packager . --platform=win32 --arch=x64 --out=dist --overwrite'
          : platform === 'mac'
            ? 'electron-packager . --platform=darwin --arch=x64 --out=dist --overwrite'
            : 'electron-packager . --platform=linux --arch=x64 --out=dist --overwrite'
      },
      keywords: ['game', 'lupiforge', title.toLowerCase()],
      author: 'Game Developer',
      license: 'MIT',
      devDependencies: {
        'electron': '^25.0.0',
        'electron-packager': '^17.0.0',
        'electron-squirrel-startup': '^1.0.0'
      }
    }, null, 2);
  }
  
  private generateMacPlist(title: string, version: string): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>${title.replace(/\s+/g, '')}</string>
  <key>CFBundleIdentifier</key>
  <string>com.lupiforge.${title.toLowerCase().replace(/\s+/g, '')}</string>
  <key>CFBundleName</key>
  <string>${title}</string>
  <key>CFBundleDisplayName</key>
  <string>${title}</string>
  <key>CFBundleVersion</key>
  <string>${version}</string>
  <key>CFBundleShortVersionString</key>
  <string>${version}</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleSignature</key>
  <string>????</string>
  <key>CFBundleIconFile</key>
  <string>icon.icns</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.10.0</string>
  <key>NSHumanReadableCopyright</key>
  <string>Copyright © ${new Date().getFullYear()} Game Developer. All rights reserved.</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSRequiresAquaSystemAppearance</key>
  <false/>
</dict>
</plist>`;
  }
  
  private generateLinuxDesktopFile(title: string, safeTitle: string): string {
    return `[Desktop Entry]
Name=${title}
Comment=${title} - Created with Lupiforge
Exec=./${safeTitle.toLowerCase()}
Icon=${safeTitle.toLowerCase()}
Terminal=false
Type=Application
Categories=Game;
StartupNotify=true
Keywords=game;lupiforge;${safeTitle.toLowerCase()};
`;
  }
  
  private async addPlatformIcons(files: Record<string, string | Blob>, platform: 'windows' | 'mac' | 'linux', gameTitle: string): Promise<void> {
    const iconAsset = this.projectData.settings.iconAsset 
      ? await AssetManager.getAssetBlob(this.projectData.settings.iconAsset)
      : await this.generateDefaultIcon(gameTitle);
    
    switch (platform) {
      case 'windows':
        files['icon.ico'] = await this.convertToICO(iconAsset);
        break;
      case 'mac':
        files['Game.app/Contents/Resources/icon.icns'] = await this.convertToICNS(iconAsset);
        break;
      case 'linux':
        files['icon.png'] = iconAsset;
        break;
    }
  }
  
  private async packageFiles(files: Record<string, string | Blob>, platform: 'windows' | 'mac' | 'linux'): Promise<Blob> {
    return await createZip(files, `${this.projectData.settings.gameTitle}-${platform}.zip`);
  }
  
  private optimizeCode(code: string): string {
    return code
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\/\/.*$/gm, '')
      .replace(/\s+/g, ' ')
      .trim();
  }
  
  private async generateDefaultIcon(gameTitle: string): Promise<Blob> {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      ctx.fillStyle = '#4a90e2';
      ctx.fillRect(0, 0, 512, 512);
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 48px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(gameTitle.substring(0, 2).toUpperCase(), 256, 256);
    }
    
    return new Promise(resolve => canvas.toBlob(blob => resolve(blob!)));
  }
  
  private async convertToICO(imageBlob: Blob): Promise<Blob> {
    return imageBlob;
  }
  
  private async convertToICNS(imageBlob: Blob): Promise<Blob> {
    return imageBlob;
  }
  
  private generateMacExecutableStub(): string {
    return '#!/bin/bash\nopen -a "Game.app"';
  }
}

export default DesktopExporter;
