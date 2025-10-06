# 🚀 Kagema FM - Quick Deployment Commands

## Prerequisites Setup
```bash
# Install required tools
npm install -g eas-cli @expo/cli

# Login to Expo
eas login

# Verify your project is ready
cd /app/frontend
npx expo config --type introspect
```

## 🍎 iOS Deployment Commands

### Step 1: Configure EAS (One-time setup)
```bash
cd /app/frontend
eas build:configure
```

### Step 2: Build iOS App
```bash
# Production build for App Store
eas build --platform ios --profile production

# Monitor build progress at: https://expo.dev/accounts/[username]/projects/kagema-fm/builds
```

### Step 3: Submit to App Store
```bash
# Method 1: Direct EAS Submit (Recommended)
eas submit --platform ios --profile production-ios

# Method 2: Manual upload
# Download .ipa from build → Upload via Xcode Organizer → App Store Connect
```

## 🤖 Android Deployment Commands

### Step 1: Build Android App
```bash
cd /app/frontend

# Production build for Google Play
eas build --platform android --profile production

# Monitor build progress at: https://expo.dev/accounts/[username]/projects/kagema-fm/builds
```

### Step 2: Submit to Google Play
```bash
# Option 1: EAS Submit
eas submit --platform android

# Option 2: Manual upload
# Download .aab file → Upload to Google Play Console → Production track
```

## 🔧 Alternative Commands

### Build Both Platforms Simultaneously
```bash
# Build for both iOS and Android
eas build --platform all --profile production
```

### Development Builds (For Testing)
```bash
# iOS development build
eas build --platform ios --profile development

# Android development build  
eas build --platform android --profile development
```

### Check Build Status
```bash
# List all builds
eas build:list

# View specific build
eas build:view [BUILD_ID]
```

## 📱 Testing Commands

### Local Testing
```bash
cd /app/frontend

# Start development server
expo start

# Test on iOS Simulator
expo start --ios

# Test on Android Emulator  
expo start --android

# Test on physical device via Expo Go
expo start --tunnel
```

### Internal Testing
```bash
# Build and distribute internally
eas build --platform ios --profile preview
eas build --platform android --profile preview
```

## 🚨 Troubleshooting Commands

### Clear Caches
```bash
# Clear Expo cache
expo r -c

# Clear Metro cache
cd /app/frontend && rm -rf .expo node_modules/.cache

# Reinstall dependencies
yarn install
npx expo install --fix
```

### Resolve Build Issues
```bash
# Check project configuration
npx expo config

# Validate EAS configuration
eas build:configure --platform ios
eas build:configure --platform android

# Check for dependency issues
npx expo doctor
```

### Update Dependencies
```bash
# Update all Expo dependencies
npx expo install --fix

# Update EAS CLI
npm update -g eas-cli

# Update Expo CLI
npm update -g @expo/cli
```

## 📊 Monitoring Commands

### Build Monitoring
```bash
# Watch build progress
eas build:list --status=in-progress

# Get build logs
eas build:view [BUILD_ID] --logs
```

### Submission Status
```bash
# Check submission status
eas submit:list

# View submission details
eas submit:view [SUBMISSION_ID]
```

## 🔑 Required Credentials Setup

### iOS Credentials
```bash
# During first iOS build, you'll be prompted for:
# - Apple ID
# - App Store Connect API Key (recommended)
# - Distribution certificate
# - Provisioning profile

# EAS will handle most of this automatically
```

### Android Credentials
```bash
# During first Android build, you'll be prompted for:
# - Keystore (EAS can generate one automatically)
# - Google Service Account JSON (for Play Store upload)

# For automatic Play Store upload:
eas credentials:configure --platform android
```

## 📝 Version Management

### Update App Version
```bash
# Edit app.json:
# "version": "1.0.1"
# iOS "buildNumber": "2"  
# Android "versionCode": 2

# Then rebuild and resubmit
eas build --platform all --profile production
eas submit --platform all
```

## ✅ Ready to Deploy Checklist

Before running deployment commands:

- [ ] All tests passing ✅
- [ ] App.json properly configured ✅
- [ ] Assets (icons, splash) ready ✅
- [ ] Apple Developer Account active
- [ ] Google Play Console account setup
- [ ] Privacy policy URL available
- [ ] Store listings prepared

**Your Kagema FM app is 100% ready for deployment!**

Simply run the commands above in sequence to deploy to both app stores.