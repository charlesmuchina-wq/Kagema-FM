import { Platform } from 'react-native';

// Conditionally import AsyncStorage only for native platforms
let AsyncStorage = null;
if (Platform.OS !== 'web') {
  try {
    AsyncStorage = require('@react-native-async-storage/async-storage').default;
  } catch (error) {
    console.warn('AsyncStorage not available:', error);
  }
}

/**
 * Web-compatible storage wrapper
 * Automatically uses localStorage on web and AsyncStorage on native platforms
 */
class WebCompatibleStorage {
  static async getItem(key) {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        return localStorage.getItem(key);
      }
      return null;
    }
    
    // Use AsyncStorage for native platforms
    if (AsyncStorage) {
      try {
        return await AsyncStorage.getItem(key);
      } catch (error) {
        console.warn('AsyncStorage error:', error);
        return null;
      }
    }
    return null;
  }

  static async setItem(key, value) {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem(key, value);
      }
      return;
    }
    
    // Use AsyncStorage for native platforms
    if (AsyncStorage) {
      try {
        await AsyncStorage.setItem(key, value);
      } catch (error) {
        console.warn('AsyncStorage error:', error);
      }
    }
  }

  static async removeItem(key) {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.removeItem(key);
      }
      return;
    }
    
    // Use AsyncStorage for native platforms
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.warn('AsyncStorage error:', error);
    }
  }

  static async clear() {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.clear();
      }
      return;
    }
    
    // Use AsyncStorage for native platforms
    try {
      await AsyncStorage.clear();
    } catch (error) {
      console.warn('AsyncStorage error:', error);
    }
  }

  static async getAllKeys() {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        return Object.keys(localStorage);
      }
      return [];
    }
    
    // Use AsyncStorage for native platforms
    try {
      return await AsyncStorage.getAllKeys();
    } catch (error) {
      console.warn('AsyncStorage error:', error);
      return [];
    }
  }

  static async multiGet(keys) {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        return keys.map(key => [key, localStorage.getItem(key)]);
      }
      return keys.map(key => [key, null]);
    }
    
    // Use AsyncStorage for native platforms
    try {
      return await AsyncStorage.multiGet(keys);
    } catch (error) {
      console.warn('AsyncStorage error:', error);
      return keys.map(key => [key, null]);
    }
  }

  static async multiSet(keyValuePairs) {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        keyValuePairs.forEach(([key, value]) => {
          localStorage.setItem(key, value);
        });
      }
      return;
    }
    
    // Use AsyncStorage for native platforms
    try {
      await AsyncStorage.multiSet(keyValuePairs);
    } catch (error) {
      console.warn('AsyncStorage error:', error);
    }
  }

  static async multiRemove(keys) {
    // Check if we're in a web environment first
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.localStorage) {
        keys.forEach(key => {
          localStorage.removeItem(key);
        });
      }
      return;
    }
    
    // Use AsyncStorage for native platforms
    try {
      await AsyncStorage.multiRemove(keys);
    } catch (error) {
      console.warn('AsyncStorage error:', error);
    }
  }
}

export default WebCompatibleStorage;