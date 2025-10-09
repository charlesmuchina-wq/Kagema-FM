#!/usr/bin/env node

/**
 * Version Manager for Kagema FM
 * Handles automatic version incrementing for iOS and Android builds
 * Usage: node version-manager.js [patch|minor|major] [--build-only]
 */

const fs = require('fs');
const path = require('path');

// File paths
const APP_JSON_PATH = path.join(__dirname, '../app.json');
const PACKAGE_JSON_PATH = path.join(__dirname, '../package.json');
const VERSION_LOG_PATH = path.join(__dirname, '../version.log');

// Version types
const VERSION_TYPES = ['patch', 'minor', 'major'];

class VersionManager {
  constructor() {
    this.appConfig = null;
    this.packageConfig = null;
    this.loadConfigs();
  }

  loadConfigs() {
    try {
      this.appConfig = JSON.parse(fs.readFileSync(APP_JSON_PATH, 'utf8'));
      this.packageConfig = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, 'utf8'));
    } catch (error) {
      console.error('❌ Error loading configuration files:', error.message);
      process.exit(1);
    }
  }

  parseVersion(versionString) {
    const parts = versionString.split('.');
    return {
      major: parseInt(parts[0] || 0),
      minor: parseInt(parts[1] || 0),
      patch: parseInt(parts[2] || 0)
    };
  }

  incrementVersion(currentVersion, type) {
    const version = this.parseVersion(currentVersion);
    
    switch (type) {
      case 'major':
        version.major++;
        version.minor = 0;
        version.patch = 0;
        break;
      case 'minor':
        version.minor++;
        version.patch = 0;
        break;
      case 'patch':
      default:
        version.patch++;
        break;
    }
    
    return `${version.major}.${version.minor}.${version.patch}`;
  }

  incrementBuildNumbers() {
    // Increment iOS build number
    const currentIosBuild = parseInt(this.appConfig.expo.ios.buildNumber || 1);
    this.appConfig.expo.ios.buildNumber = (currentIosBuild + 1).toString();
    
    // Increment Android version code
    const currentAndroidVersion = parseInt(this.appConfig.expo.android.versionCode || 1);
    this.appConfig.expo.android.versionCode = currentAndroidVersion + 1;
    
    console.log(`📱 iOS Build Number: ${currentIosBuild} → ${this.appConfig.expo.ios.buildNumber}`);
    console.log(`🤖 Android Version Code: ${currentAndroidVersion} → ${this.appConfig.expo.android.versionCode}`);
  }

  updateVersion(type = 'patch', buildOnly = false) {
    const currentVersion = this.appConfig.expo.version;
    
    if (!buildOnly) {
      // Update semantic version
      const newVersion = this.incrementVersion(currentVersion, type);
      this.appConfig.expo.version = newVersion;
      this.packageConfig.version = newVersion;
      
      console.log(`📦 App Version: ${currentVersion} → ${newVersion} (${type})`);
    } else {
      console.log(`📦 App Version: ${currentVersion} (unchanged)`);
    }
    
    // Always increment build numbers
    this.incrementBuildNumbers();
    
    return {
      version: this.appConfig.expo.version,
      iosBuildNumber: this.appConfig.expo.ios.buildNumber,
      androidVersionCode: this.appConfig.expo.android.versionCode
    };
  }

  saveConfigs() {
    try {
      // Save app.json with proper formatting
      fs.writeFileSync(APP_JSON_PATH, JSON.stringify(this.appConfig, null, 2) + '\n');
      
      // Save package.json with proper formatting
      fs.writeFileSync(PACKAGE_JSON_PATH, JSON.stringify(this.packageConfig, null, 2) + '\n');
      
      console.log('✅ Configuration files updated successfully');
    } catch (error) {
      console.error('❌ Error saving configuration files:', error.message);
      process.exit(1);
    }
  }

  logVersionChange(versionInfo, type, buildOnly) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      type: buildOnly ? 'build-increment' : `version-${type}`,
      version: versionInfo.version,
      iosBuildNumber: versionInfo.iosBuildNumber,
      androidVersionCode: versionInfo.androidVersionCode,
      buildOnly
    };
    
    let versionLog = [];
    
    // Load existing log
    try {
      if (fs.existsSync(VERSION_LOG_PATH)) {
        const logData = fs.readFileSync(VERSION_LOG_PATH, 'utf8');
        versionLog = JSON.parse(logData);
      }
    } catch (error) {
      console.warn('⚠️ Could not load existing version log, creating new one');
      versionLog = [];
    }
    
    // Add new entry
    versionLog.push(logEntry);
    
    // Keep only last 100 entries
    if (versionLog.length > 100) {
      versionLog = versionLog.slice(-100);
    }
    
    // Save log
    try {
      fs.writeFileSync(VERSION_LOG_PATH, JSON.stringify(versionLog, null, 2) + '\n');
      console.log('📝 Version change logged');
    } catch (error) {
      console.warn('⚠️ Could not save version log:', error.message);
    }
  }

  generateVersionReport() {
    console.log('\n🔍 CURRENT VERSION STATUS');
    console.log('=' .repeat(50));
    console.log(`📦 App Version: ${this.appConfig.expo.version}`);
    console.log(`📱 iOS Build Number: ${this.appConfig.expo.ios.buildNumber}`);
    console.log(`🤖 Android Version Code: ${this.appConfig.expo.android.versionCode}`);
    console.log(`📱 iOS Bundle ID: ${this.appConfig.expo.ios.bundleIdentifier}`);
    console.log(`🤖 Android Package: ${this.appConfig.expo.android.package}`);
    
    // Show recent version history
    if (fs.existsSync(VERSION_LOG_PATH)) {
      try {
        const logData = JSON.parse(fs.readFileSync(VERSION_LOG_PATH, 'utf8'));
        const recentEntries = logData.slice(-5);
        
        console.log('\n📜 RECENT VERSION HISTORY');
        console.log('-'.repeat(30));
        recentEntries.forEach(entry => {
          const date = new Date(entry.timestamp).toLocaleString();
          console.log(`${date} - ${entry.type}: v${entry.version} (iOS: ${entry.iosBuildNumber}, Android: ${entry.androidVersionCode})`);
        });
      } catch (error) {
        console.warn('⚠️ Could not load version history');
      }
    }
    
    console.log('=' .repeat(50));
  }

  validateVersions() {
    const issues = [];
    
    // Check version format
    const versionRegex = /^\d+\.\d+\.\d+$/;
    if (!versionRegex.test(this.appConfig.expo.version)) {
      issues.push(`Invalid version format: ${this.appConfig.expo.version}`);
    }
    
    // Check iOS build number
    if (!/^\d+$/.test(this.appConfig.expo.ios.buildNumber)) {
      issues.push(`Invalid iOS build number: ${this.appConfig.expo.ios.buildNumber}`);
    }
    
    // Check Android version code
    if (!/^\d+$/.test(this.appConfig.expo.android.versionCode.toString())) {
      issues.push(`Invalid Android version code: ${this.appConfig.expo.android.versionCode}`);
    }
    
    // Check bundle identifiers
    if (!this.appConfig.expo.ios.bundleIdentifier || !this.appConfig.expo.ios.bundleIdentifier.includes('.')) {
      issues.push('Invalid iOS bundle identifier');
    }
    
    if (!this.appConfig.expo.android.package || !this.appConfig.expo.android.package.includes('.')) {
      issues.push('Invalid Android package name');
    }
    
    return issues;
  }

  run() {
    const args = process.argv.slice(2);
    const type = args[0] || 'patch';
    const buildOnly = args.includes('--build-only');
    
    // Show current status
    this.generateVersionReport();
    
    // Validate arguments
    if (!buildOnly && !VERSION_TYPES.includes(type)) {
      console.error(`❌ Invalid version type: ${type}`);
      console.log(`Valid types: ${VERSION_TYPES.join(', ')}`);
      process.exit(1);
    }
    
    // Validate current versions
    const issues = this.validateVersions();
    if (issues.length > 0) {
      console.error('❌ Version validation failed:');
      issues.forEach(issue => console.error(`  - ${issue}`));
      process.exit(1);
    }
    
    if (args.includes('--status')) {
      console.log('\n✅ Version status check complete');
      return;
    }
    
    console.log(`\n🚀 ${buildOnly ? 'Incrementing build numbers' : `Updating version (${type})`}...`);
    
    // Update versions
    const versionInfo = this.updateVersion(type, buildOnly);
    
    // Save changes
    this.saveConfigs();
    
    // Log changes
    this.logVersionChange(versionInfo, type, buildOnly);
    
    console.log('\n✅ Version update complete!');
    console.log('\nNext steps:');
    console.log('1. Build the app: npx expo build:ios && npx expo build:android');
    console.log('2. Test the build in deployment simulation');
    console.log('3. Submit to app stores if everything works correctly');
  }
}

// Export for programmatic use
module.exports = VersionManager;

// Run if called directly
if (require.main === module) {
  const manager = new VersionManager();
  manager.run();
}