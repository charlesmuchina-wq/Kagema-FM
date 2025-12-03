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

// Web-specific resolver to exclude native-only modules
config.resolver.resolverMainFields = ['react-native', 'browser', 'main'];
config.resolver.platforms = ['web', 'native', 'ios', 'android'];

// Exclude problematic native modules for web builds
config.resolver.alias = {
  'react-native-maps': require.resolve('./web-stubs/react-native-maps.js'),
  'expo-gl': require.resolve('./web-stubs/expo-gl.js'),
  'expo-three': require.resolve('./web-stubs/expo-three.js'),
};

// Reduce the number of workers to decrease resource usage
config.maxWorkers = 2;

module.exports = config;
