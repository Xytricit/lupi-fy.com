import { ProjectData } from '../types/project';
import { AssetManager } from '../core/AssetManager';
import { GameRuntime } from '../runtime/GameRuntime';
import { ASTCompiler } from '../compiler/ASTCompiler';
import { createZip } from '../utils/zipUtils';
import { exportSettings } from '../config/exportSettings';

export class MobileExporter {
  private projectData: ProjectData;
  private runtime: GameRuntime;
  private compiler: ASTCompiler;
  
  constructor(projectData: ProjectData) {
    this.projectData = projectData;
    this.runtime = new GameRuntime();
    this.compiler = new ASTCompiler({ platform: 'mobile' });
  }

  /**
   * Exports the project as a mobile application package
   * 
   * @param exportType - The mobile platform to export to ('ios', 'android')
   * @param exportOptions - Additional export configuration options
   * @returns A Promise resolving to a Blob containing the exported package
   */
  async export(exportType: 'ios' | 'android', exportOptions: ExportOptions = {}): Promise<Blob> {
    try {
      this.validateProject();
      
      const compiledCode = this.compiler.compile(this.projectData.blocks, {
        platform: 'mobile',
        target: exportType,
        optimize: exportOptions.optimize || true,
        debugSymbols: exportOptions.debug || false
      });
      
      const assets = await this.collectAssets();
      
      const files = await this.generateProjectFiles(exportType, compiledCode, assets, exportOptions);
      
      return await this.packageFiles(files, exportType);
    } catch (error) {
      console.error(`Mobile export failed: ${error.message}`);
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
    
    const hasTouchBlocks = this.projectData.blocks.some(
      block => block.type.startsWith('on_touch_') || 
               block.type.startsWith('on_swipe') || 
               block.type.startsWith('on_pinch') ||
               block.type.startsWith('on_double_tap')
    );
    
    if (!hasTouchBlocks) {
      throw new Error('Game needs touch input logic for mobile. Add touch or gesture blocks before exporting.');
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
    platform: 'ios' | 'android',
    compiledCode: string,
    assets: Record<string, Blob>,
    options: ExportOptions
  ): Promise<Record<string, string | Blob>> {
    const files: Record<string, string | Blob> = {};
    const gameTitle = this.projectData.settings.gameTitle.replace(/[^\w\s-]/g, '').trim();
    const safeGameTitle = gameTitle.replace(/\s+/g, '_');
    const projectVersion = this.projectData.settings.version || '1.0.0';
    const packageName = `com.lupiforge.${safeGameTitle.toLowerCase()}`;
    
    files[platform === 'ios' ? 'Game.xcodeproj/Game.js' : 'app/src/main/assets/game.js'] = this.generateMainGameFile(
      compiledCode,
      options
    );
    
    switch (platform) {
      case 'android':
        files['app/build.gradle'] = this.generateAndroidBuildGradle(gameTitle, projectVersion, packageName);
        files['app/src/main/AndroidManifest.xml'] = this.generateAndroidManifest(packageName, gameTitle);
        files['app/src/main/java/com/lupiforge/game/MainActivity.java'] = this.generateAndroidActivity(packageName);
        files['app/src/main/res/values/strings.xml'] = this.generateAndroidStrings(gameTitle);
        files['CordovaConfig.xml'] = this.generateCordovaConfig(gameTitle, packageName, projectVersion);
        break;
      case 'ios':
        files['Game.xcodeproj/project.pbxproj'] = this.generateXcodeProjectFile(gameTitle, packageName);
        files['Game/Info.plist'] = this.generateiOSInfoPlist(gameTitle, packageName, projectVersion);
        files['Game/AppDelegate.m'] = this.generateiOSAppDelegate();
        files['Game/ViewController.m'] = this.generateiOSViewController();
        break;
    }
    
    Object.entries(assets).forEach(([path, blob]) => {
      if (platform === 'android') {
        if (path.match(/\.(png|jpg|jpeg)$/i)) {
          const assetPath = path.replace(/\//g, '_');
          files[`app/src/main/res/drawable/${assetPath}`] = blob;
        } else if (path.match(/\.(mp3|wav|m4a)$/i)) {
          const assetPath = path.replace(/\//g, '_');
          files[`app/src/main/res/raw/${assetPath}`] = blob;
        } else {
          files[`app/src/main/assets/${path}`] = blob;
        }
      } else {
        files[`Game/Assets/${path}`] = blob;
      }
    });
    
    await this.addPlatformIcons(files, platform, gameTitle);
    
    files['lupiforge_mobile_config.json'] = JSON.stringify({
      gameTitle: gameTitle,
      packageName: packageName,
      version: projectVersion,
      exportPlatform: platform,
      exportDate: new Date().toISOString(),
      touchConfig: {
        enableMultiTouch: this.projectData.settings.touchConfig?.enableMultiTouch !== false,
        swipeSensitivity: this.projectData.settings.touchConfig?.swipeSensitivity || 0.5,
        pinchEnabled: this.projectData.settings.touchConfig?.pinchEnabled !== false
      },
      orientation: this.projectData.settings.orientation || 'landscape',
      settings: this.projectData.settings
    }, null, 2);
    
    files['touch_config.json'] = this.generateTouchConfig();
    
    return files;
  }
  
  private generateMainGameFile(compiledCode: string, options: ExportOptions): string {
    const gameSettings = this.projectData.settings;
    const optimizedCode = options.optimize ? this.optimizeCode(compiledCode) : compiledCode;
    
    return `// Lupiforge Mobile Game Engine - Auto-generated Game Code
// Game: ${gameSettings.gameTitle}
// Version: ${gameSettings.version || '1.0.0'}
// Platform: ${gameSettings.orientation || 'landscape'}
// Exported: ${new Date().toISOString()}

// Engine initialization for mobile
const engine = new LupiforgeMobileEngine({
  width: ${gameSettings.resolution?.width || 800},
  height: ${gameSettings.resolution?.height || 600},
  orientation: "${gameSettings.orientation || 'landscape'}",
  audioMuted: false,
  touchConfig: {
    enableMultiTouch: ${gameSettings.touchConfig?.enableMultiTouch !== false},
    swipeSensitivity: ${gameSettings.touchConfig?.swipeSensitivity || 0.5},
    pinchEnabled: ${gameSettings.touchConfig?.pinchEnabled !== false}
  },
  physics: {
    gravity: ${gameSettings.physics?.gravity || 9.8},
    friction: ${gameSettings.physics?.friction || 0.8}
  }
});

// Game logic compiled from blocks
${optimizedCode}

// Initialize touch events
engine.initTouchEvents();

// Start the game engine
engine.start();
`;
  }
  
  private generateAndroidManifest(packageName: string, appName: string): string {
    return `<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="${packageName}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:label="@string/app_name"
            android:screenOrientation="${this.projectData.settings.orientation === 'portrait' ? 'portrait' : 'landscape'}"
            android:configChanges="orientation|keyboardHidden|screenSize"
            android:launchMode="singleTask"
            android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>`;
  }
  
  private generateAndroidActivity(packageName: string): string {
    return `package ${packageName.replace(/\./g, '/')};

import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        
        setContentView(R.layout.activity_main);
        webView = findViewById(R.id.webview);
        
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        webSettings.setMediaPlaybackRequiresUserGesture(false);
        
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("file:///android_asset/index.html");
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
        }
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.onPause();
        }
    }
    
    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
    
    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}`;
  }
  
  private generateAndroidStrings(appName: string): string {
    return `<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">${appName}</string>
</resources>`;
  }
  
  private generateCordovaConfig(appName: string, packageName: string, version: string): string {
    return `<?xml version='1.0' encoding='utf-8'?>
<widget id="${packageName}" version="${version}" xmlns="http://www.w3.org/ns/widgets" xmlns:cdv="http://cordova.apache.org/ns/1.0">
    <name>${appName}</name>
    <description>A Lupiforge game</description>
    <author email="dev@example.com" href="https://lupiforge.com">
        Game Developer
    </author>
    <content src="index.html" />
    <access origin="*" />
    <allow-intent href="http://*/*" />
    <allow-intent href="https://*/*" />
    <preference name="orientation" value="${this.projectData.settings.orientation || 'landscape'}" />
    <preference name="Fullscreen" value="true" />
    <preference name="HideKeyboardFormAccessoryBar" value="true" />
    <preference name="AndroidLaunchMode" value="singleTask" />
    <feature name="Device">
        <param name="android-package" value="org.apache.cordova.device.Device" />
    </feature>
    <feature name="Media">
        <param name="android-package" value="org.apache.cordova.media.AudioHandler" />
    </feature>
    <feature name="Vibration">
        <param name="android-package" value="org.apache.cordova.vibration.Vibration" />
    </feature>
    <platform name="android">
        <icon src="res/icon/android/icon-36-ldpi.png" density="ldpi" />
        <icon src="res/icon/android/icon-48-mdpi.png" density="mdpi" />
        <icon src="res/icon/android/icon-72-hdpi.png" density="hdpi" />
        <icon src="res/icon/android/icon-96-xhdpi.png" density="xhdpi" />
        <icon src="res/icon/android/icon-144-xxhdpi.png" density="xxhdpi" />
        <icon src="res/icon/android/icon-192-xxxhdpi.png" density="xxxhdpi" />
        <splash src="res/screen/android/screen-ldpi-portrait.png" density="port-ldpi" />
        <splash src="res/screen/android/screen-mdpi-portrait.png" density="port-mdpi" />
        <splash src="res/screen/android/screen-hdpi-portrait.png" density="port-hdpi" />
        <splash src="res/screen/android/screen-xhdpi-portrait.png" density="port-xhdpi" />
    </platform>
</widget>`;
  }
  
  private generateXcodeProjectFile(appName: string, packageName: string): string {
    return `// !$*UTF8*$!
{
  archiveVersion = 1;
  classes = {
  };
  objectVersion = 52;
  objects = {
    /* Project object */
    1234567890ABCDEF = {
      isa = PBXProject;
      attributes = {
        LastUpgradeCheck = 1300;
        TargetAttributes = {
          0123456789ABCDEF = {
            CreatedOnToolsVersion = 13.0;
          };
        };
      };
      buildConfigurationList = 1234567890ABCDEF /* Build configuration list for PBXProject */;
      compatibilityVersion = "Xcode 13.0";
      developmentRegion = en;
      hasScannedForEncodings = 0;
      knownRegions = (
        en,
        Base,
      );
      mainGroup = 1234567890ABCDEF;
      productRefGroup = 1234567890ABCDEF /* Products */;
      projectDirPath = "";
      projectRoot = "";
      targets = (
        0123456789ABCDEF /* ${appName} */,
      );
    };
  };
  rootObject = 1234567890ABCDEF /* Project object */;
}`;
  }
  
  private generateiOSInfoPlist(appName: string, packageName: string, version: string): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleDisplayName</key>
  <string>${appName}</string>
  <key>CFBundleExecutable</key>
  <string>${appName.replace(/\s+/g, '')}</string>
  <key>CFBundleIdentifier</key>
  <string>${packageName}</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>${appName}</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>${version}</string>
  <key>CFBundleVersion</key>
  <string>${version}</string>
  <key>LSRequiresIPhoneOS</key>
  <true/>
  <key>UILaunchStoryboardName</key>
  <string>LaunchScreen</string>
  <key>UIRequiredDeviceCapabilities</key>
  <array>
    <string>armv7</string>
  </array>
  <key>UIStatusBarHidden</key>
  <true/>
  <key>UISupportedInterfaceOrientations</key>
  <array>
    ${this.projectData.settings.orientation === 'portrait' ? 
      '<string>UIInterfaceOrientationPortrait</string>' : 
      '<string>UIInterfaceOrientationLandscapeLeft</string>\n    <string>UIInterfaceOrientationLandscapeRight</string>'
    }
  </array>
  <key>UISupportedInterfaceOrientations~ipad</key>
  <array>
    ${this.projectData.settings.orientation === 'portrait' ? 
      '<string>UIInterfaceOrientationPortrait</string>\n    <string>UIInterfaceOrientationPortraitUpsideDown</string>' : 
      '<string>UIInterfaceOrientationLandscapeLeft</string>\n    <string>UIInterfaceOrientationLandscapeRight</string>'
    }
  </array>
  <key>UIViewControllerBasedStatusBarAppearance</key>
  <false/>
  <key>UIRequiresFullScreen</key>
  <true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
  </dict>
</dict>
</plist>`;
  }
  
  private generateiOSAppDelegate(): string {
    return `#import "AppDelegate.h"
#import "ViewController.h"

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];
    
    ViewController *viewController = [[ViewController alloc] init];
    UINavigationController *navigationController = [[UINavigationController alloc] initWithRootViewController:viewController];
    navigationController.navigationBarHidden = YES;
    
    self.window.rootViewController = navigationController;
    [self.window makeKeyAndVisible];
    
    [[UIApplication sharedApplication] setIdleTimerDisabled:YES];
    
    return YES;
}

- (void)applicationWillResignActive:(UIApplication *)application {
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
}

- (void)applicationWillEnterForeground:(UIApplication *)application {
}

- (void)applicationDidBecomeActive:(UIApplication *)application {
}

- (void)applicationWillTerminate:(UIApplication *)application {
}

@end`;
  }
  
  private generateiOSViewController(): string {
    return `#import "ViewController.h"
#import <WebKit/WebKit.h>

@interface ViewController ()
@property (nonatomic, strong) WKWebView *webView;
@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor blackColor];
    self.edgesForExtendedLayout = UIRectEdgeNone;
    self.navigationController.navigationBarHidden = YES;
    [[UIApplication sharedApplication] setStatusBarHidden:YES withAnimation:UIStatusBarAnimationNone];
    
    WKWebViewConfiguration *config = [[WKWebViewConfiguration alloc] init];
    config.mediaTypesRequiringUserActionForPlayback = WKAudiovisualMediaTypesNone;
    
    self.webView = [[WKWebView alloc] initWithFrame:self.view.bounds configuration:config];
    [self.view addSubview:self.webView];
    
    NSString *path = [[NSBundle mainBundle] pathForResource:@"index" ofType:@"html" inDirectory:@"www"];
    NSURL *url = [NSURL fileURLWithPath:path];
    NSURLRequest *request = [NSURLRequest requestWithURL:url];
    [self.webView loadRequest:request];
}

- (void)viewWillLayoutSubviews {
    [super viewWillLayoutSubviews];
    self.webView.frame = self.view.bounds;
}

- (BOOL)prefersStatusBarHidden {
    return YES;
}

@end`;
  }
  
  private generateTouchConfig(): string {
    const touchConfig = this.projectData.settings.touchConfig || {};
    return JSON.stringify({
      enableMultiTouch: touchConfig.enableMultiTouch !== false,
      swipeSensitivity: touchConfig.swipeSensitivity || 0.5,
      pinchEnabled: touchConfig.pinchEnabled !== false,
      doubleTapThreshold: touchConfig.doubleTapThreshold || 300,
      longPressThreshold: touchConfig.longPressThreshold || 500,
      hapticFeedback: touchConfig.hapticFeedback || true,
      touchAreas: touchConfig.touchAreas || [
        {
          id: "main_area",
          x: 0,
          y: 0,
          width: 1.0,
          height: 1.0,
          type: "full"
        }
      ]
    }, null, 2);
  }
  
  private async addPlatformIcons(files: Record<string, string | Blob>, platform: 'ios' | 'android', gameTitle: string): Promise<void> {
    const iconAsset = this.projectData.settings.iconAsset 
      ? await AssetManager.getAssetBlob(this.projectData.settings.iconAsset)
      : await this.generateDefaultIcon(gameTitle);
    
    switch (platform) {
      case 'android':
        files['app/src/main/res/mipmap-hdpi/ic_launcher.png'] = await this.resizeIcon(iconAsset, 72);
        files['app/src/main/res/mipmap-mdpi/ic_launcher.png'] = await this.resizeIcon(iconAsset, 48);
        files['app/src/main/res/mipmap-xhdpi/ic_launcher.png'] = await this.resizeIcon(iconAsset, 96);
        files['app/src/main/res/mipmap-xxhdpi/ic_launcher.png'] = await this.resizeIcon(iconAsset, 144);
        files['app/src/main/res/mipmap-xxxhdpi/ic_launcher.png'] = await this.resizeIcon(iconAsset, 192);
        break;
      case 'ios':
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-20x20@2x.png'] = await this.resizeIcon(iconAsset, 40);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-20x20@3x.png'] = await this.resizeIcon(iconAsset, 60);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-29x29@2x.png'] = await this.resizeIcon(iconAsset, 58);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-29x29@3x.png'] = await this.resizeIcon(iconAsset, 87);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-40x40@2x.png'] = await this.resizeIcon(iconAsset, 80);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-40x40@3x.png'] = await this.resizeIcon(iconAsset, 120);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-60x60@2x.png'] = await this.resizeIcon(iconAsset, 120);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-60x60@3x.png'] = await this.resizeIcon(iconAsset, 180);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-76x76@2x.png'] = await this.resizeIcon(iconAsset, 152);
        files['Game/Assets.xcassets/AppIcon.appiconset/Icon-83.5x83.5@2x.png'] = await this.resizeIcon(iconAsset, 167);
        break;
    }
  }
  
  private async packageFiles(files: Record<string, string | Blob>, platform: 'ios' | 'android'): Promise<Blob> {
    const gameTitle = this.projectData.settings.gameTitle.replace(/[^\w\s-]/g, '').trim();
    const safeGameTitle = gameTitle.replace(/\s+/g, '_');
    const version = this.projectData.settings.version || '1.0.0';
    
    const zip = await createZip(files);
    
    let filename = '';
    switch (platform) {
      case 'ios':
        filename = `${safeGameTitle}_v${version}.ipa`;
        break;
      case 'android':
        filename = `${safeGameTitle}_v${version}.apk`;
        break;
    }
    
    const blob = new Blob([zip], { type: platform === 'ios' ? 'application/octet-stream' : 'application/vnd.android.package-archive' });
    Object.assign(blob, { name: filename });
    
    return blob;
  }
  
  private optimizeCode(code: string): string {
    return code
      .replace(/\s+/g, ' ')
      .replace(/\/\/.*$/gm, '')
      .replace(/\/\*[\s\S]*?\*\//g, '');
  }
  
  private async generateDefaultIcon(title: string): Promise<Blob> {
    return new Blob([/* icon data */], { type: 'image/png' });
  }
  
  private async resizeIcon(imageBlob: Blob, size: number): Promise<Blob> {
    return imageBlob;
  }
  
  private generateAndroidBuildGradle(appName: string, version: string, packageName: string): string {
    return `apply plugin: 'com.android.application'

android {
    compileSdkVersion 33
    buildToolsVersion "33.0.0"
    
    defaultConfig {
        applicationId "${packageName}"
        minSdkVersion 24
        targetSdkVersion 33
        versionCode 1
        versionName "${version}"
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    sourceSets {
        main {
            assets.srcDirs = ['src/main/assets']
            res.srcDirs = ['src/main/res']
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.webkit:webkit:1.7.0'
    implementation 'androidx.core:core:1.10.1'
}`;
  }
}

interface ExportOptions {
  optimize?: boolean;
  debug?: boolean;
  resolution?: {
    width: number;
    height: number;
  };
  orientation?: 'portrait' | 'landscape';
  includeSourceMaps?: boolean;
  includeDevTools?: boolean;
  touchConfig?: {
    enableMultiTouch?: boolean;
    swipeSensitivity?: number;
    pinchEnabled?: boolean;
    doubleTapThreshold?: number;
    longPressThreshold?: number;
    hapticFeedback?: boolean;
    touchAreas?: Array<{
      id: string;
      x: number;
      y: number;
      width: number;
      height: number;
      type: 'button' | 'slider' | 'area' | 'full';
    }>;
  };
}

export async function exportMobileGame(projectData: ProjectData, platform: 'ios' | 'android', options: ExportOptions = {}): Promise<Blob> {
  const exporter = new MobileExporter(projectData);
  return exporter.export(platform, options);
}
