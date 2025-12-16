// FIXED MOBILE EXPORTER
class MobileExporter {
  constructor(projectData) {
    this.projectData = projectData;
    this.assetManager = window.assetManager || {
      getAssetBlob: async (id) => new Blob(),
      getAssetsByType: (type) => []
    };
  }

  async export(platform, exportOptions = {}) {
    try {
      this.validateProject();
      const files = await this.generateProjectFiles(platform, exportOptions);
      return await this.packageFiles(files, platform);
    } catch (error) {
      console.error(`Mobile export failed: ${error.message}`);
      throw new Error(`Export failed: ${error.message}`);
    }
  }

  validateProject() {
    if (!this.projectData || !this.projectData.blocks || this.projectData.blocks.length === 0) {
      throw new Error('Project has no blocks. Add game logic before exporting.');
    }
    if (!this.projectData.gameTitle || this.projectData.gameTitle.trim() === '') {
      throw new Error('Game title is required for export.');
    }
  }

  async generateProjectFiles(platform, options) {
    const gameTitle = this.projectData.gameTitle.replace(/[^\w\s-]/g, '').trim();
    const safeGameTitle = gameTitle.replace(/\s+/g, '_');
    const version = this.projectData.version || '1.0.0';
    
    const files = {
      'game.js': this.generateGameFile(options)
    };
    
    if (platform === 'android') {
      files['AndroidManifest.xml'] = this.generateAndroidManifest(gameTitle, safeGameTitle, version);
      files['build.gradle'] = this.generateGradleFile(safeGameTitle, version);
    } else if (platform === 'ios') {
      files['Info.plist'] = this.generateIOSPlist(gameTitle, safeGameTitle, version);
      files['AppDelegate.m'] = this.generateAppDelegate(safeGameTitle);
    }
    
    files['config.json'] = this.generateConfigFile(platform, options);
    
    // Add assets
    await this.addAssets(files);
    
    return files;
  }

  generateGameFile(options) {
    const gameTitle = this.projectData.gameTitle || 'MyGame';
    const code = this.projectData.code || '';
    const optimizedCode = options.optimize ? this.optimizeCode(code) : code;
    
    return `// Lupiforge Mobile Game - Auto-generated
// Game: ${gameTitle}
// Version: ${this.projectData.version || '1.0.0'}
// Exported: ${new Date().toISOString()}

const gameConfig = {
  title: '${gameTitle}',
  version: '${this.projectData.version || '1.0.0'}',
  orientation: '${options.orientation || 'landscape'}',
  touchEnabled: true,
  enableMultiTouch: ${options.touchConfig?.enableMultiTouch !== false}
};

// Game initialization
console.log('🎮 Initializing game:', gameConfig);

// Game logic from blocks
${optimizedCode}

// Start the game
if (typeof startGame === 'function') {
  startGame();
}`;
  }

  generateConfigFile(platform, options) {
    return JSON.stringify({
      platform: platform,
      title: this.projectData.gameTitle,
      version: this.projectData.version || '1.0.0',
      orientation: options.orientation || 'landscape',
      touchConfig: {
        enableMultiTouch: options.touchConfig?.enableMultiTouch !== false,
        swipeSensitivity: options.touchConfig?.swipeSensitivity || 0.5
      },
      exportDate: new Date().toISOString()
    }, null, 2);
  }

  generateAndroidManifest(gameTitle, packageName, version) {
    return `<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.lupiforge.${packageName.toLowerCase()}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="${gameTitle}"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:label="${gameTitle}"
            android:screenOrientation="${this.projectData.orientation === 'portrait' ? 'portrait' : 'landscape'}"
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

  generateGradleFile(packageName, version) {
    return `apply plugin: 'com.android.application'

android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.lupiforge.${packageName.toLowerCase()}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "${version}"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.webkit:webkit:1.8.0'
}`;
  }

  generateIOSPlist(gameTitle, packageName, version) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>${gameTitle}</string>
    <key>CFBundleIdentifier</key>
    <string>com.lupiforge.${packageName.toLowerCase()}</string>
    <key>CFBundleShortVersionString</key>
    <string>${version}</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>UIRequiresFullScreen</key>
    <true/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        ${this.projectData.orientation === 'portrait' ? 
          '<string>UIInterfaceOrientationPortrait</string>' : 
          '<string>UIInterfaceOrientationLandscapeLeft</string>\n        <string>UIInterfaceOrientationLandscapeRight</string>'
        }
    </array>
    <key>UIViewControllerBasedStatusBarAppearance</key>
    <false/>
    <key>UIStatusBarHidden</key>
    <true/>
</dict>
</plist>`;
  }

  generateAppDelegate(appName) {
    return `#import <UIKit/UIKit.h>
#import <WebKit/WebKit.h>

@interface AppDelegate : UIResponder <UIApplicationDelegate>
@property (strong, nonatomic) UIWindow *window;
@end

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];
    
    WKWebViewConfiguration *config = [[WKWebViewConfiguration alloc] init];
    config.mediaTypesRequiringUserActionForPlayback = WKAudiovisualMediaTypesNone;
    
    WKWebView *webView = [[WKWebView alloc] initWithFrame:self.window.bounds configuration:config];
    [self.window addSubview:webView];
    
    NSString *path = [[NSBundle mainBundle] pathForResource:@"game" ofType:@"js" inDirectory:nil];
    NSString *html = [NSString stringWithFormat:@"<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'/><script src='%%@'></script></head><body style='margin:0;padding:0;overflow:hidden;'></body></html>", path];
    [webView loadHTMLString:html baseURL:nil];
    
    self.window.backgroundColor = [UIColor blackColor];
    [self.window makeKeyAndVisible];
    
    return YES;
}

@end`;
  }

  async addAssets(files) {
    // Add placeholder for asset handling
    files['assets.json'] = JSON.stringify({
      sprites: [],
      sounds: [],
      backgrounds: []
    }, null, 2);
  }

  optimizeCode(code) {
    return code
      .replace(/\s+/g, ' ')
      .replace(/\/\/.*$/gm, '')
      .replace(/\/\*[\s\S]*?\*\//g, '');
  }

  async packageFiles(files, platform) {
    const gameTitle = this.projectData.gameTitle.replace(/[^\w\s-]/g, '').trim();
    const safeGameTitle = gameTitle.replace(/\s+/g, '_');
    const version = this.projectData.version || '1.0.0';
    
    // Create a simple zip blob for demonstration
    const zipContent = JSON.stringify(files);
    const blob = new Blob([zipContent], { type: platform === 'ios' ? 'application/octet-stream' : 'application/vnd.android.package-archive' });
    
    blob.name = `${safeGameTitle}_v${version}.${platform === 'ios' ? 'ipa' : 'apk'}`;
    return blob;
  }
}

// Export function
window.exportMobileGame = async (projectData, platform, options = {}) => {
  const exporter = new MobileExporter(projectData);
  return exporter.export(platform, options);
};
