// metro.config.js
const { getDefaultConfig } = require("expo/metro-config");
const path = require('path');
const { FileStore } = require('metro-cache');

const config = getDefaultConfig(__dirname);

// Use a stable on-disk store (shared across web/android)
const root = process.env.METRO_CACHE_ROOT || path.join(__dirname, '.metro-cache');
config.cacheStores = [
  new FileStore({ root: path.join(root, 'cache') }),
];

// Platform-specific resolution order (web gets priority for .web.tsx files)
config.resolver.sourceExts = ['web.tsx', 'web.ts', 'web.jsx', 'web.js', ...config.resolver.sourceExts];
config.resolver.platforms = ['web', 'native', 'ios', 'android'];

// Ensure font files are recognized as assets for @expo/vector-icons
config.resolver.assetExts = [...config.resolver.assetExts, 'ttf', 'otf'];

// Block native-only packages from web builds
config.resolver.blockList = [
  // Block react-native-maps for web platform
  /node_modules\/react-native-maps\/.*/,
  // Block expo-gl and expo-three for web
  /node_modules\/expo-gl\/.*/,
  /node_modules\/expo-three\/.*/,
];

// Override resolver to handle blocked modules
const originalResolveRequest = config.resolver.resolveRequest;
config.resolver.resolveRequest = (context, moduleName, platform) => {
  // For web platform, redirect native modules to empty stubs
  if (platform === 'web') {
    if (moduleName === 'react-native-maps' || moduleName.startsWith('react-native-maps/')) {
      return {
        filePath: path.resolve(__dirname, 'web-stubs/react-native-maps.js'),
        type: 'sourceFile',
      };
    }
    if (moduleName === 'expo-gl') {
      return {
        filePath: path.resolve(__dirname, 'web-stubs/expo-gl.js'),
        type: 'sourceFile',
      };
    }
    if (moduleName === 'expo-three') {
      return {
        filePath: path.resolve(__dirname, 'web-stubs/expo-three.js'),
        type: 'sourceFile',
      };
    }
  }
  
  // Fallback to default resolution
  if (originalResolveRequest) {
    return originalResolveRequest(context, moduleName, platform);
  }
  return context.resolveRequest(context, moduleName, platform);
};

// Reduce the number of workers to decrease resource usage
config.maxWorkers = 2;

module.exports = config;
