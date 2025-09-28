import AsyncStorage from '@react-native-async-storage/async-storage';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

class LanguageService {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 30 * 60 * 1000; // 30 minutes
    this.currentLanguage = null;
    this.currentLocation = null;
  }

  async detectLanguage(latitude, longitude) {
    const cacheKey = `language_${latitude.toFixed(3)}_${longitude.toFixed(3)}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/language/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude, longitude }),
      });

      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        this.currentLanguage = data.detected_language;
        this.currentLocation = data.county;
        
        // Save language preference
        await this.saveLanguagePreference(data);
        
        return data;
      } else {
        throw new Error('Language detection service unavailable');
      }
    } catch (error) {
      console.error('Error detecting language:', error);
      return this.getFallbackLanguage();
    }
  }

  async getMultilingualStationInfo(latitude, longitude) {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/station-info/multilingual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude, longitude }),
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error('Multilingual station info service unavailable');
      }
    } catch (error) {
      console.error('Error getting multilingual station info:', error);
      return null;
    }
  }

  async getSupportedLanguages() {
    const cacheKey = 'supported_languages';
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/languages`);
      
      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('Languages service unavailable');
      }
    } catch (error) {
      console.error('Error getting supported languages:', error);
      return { supported_languages: [], total_count: 0 };
    }
  }

  async getRegionalStations(languageCode) {
    const cacheKey = `regional_stations_${languageCode}`;
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/regional-stations/${languageCode}`);
      
      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('Regional stations service unavailable');
      }
    } catch (error) {
      console.error('Error getting regional stations:', error);
      return { stations: [], total_count: 0 };
    }
  }

  async getMultilingualPersonalizedContent(location, preferences) {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/personalized-content/multilingual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          interests: preferences.interests || [],
          favorite_genres: preferences.favorite_genres || [],
          location: preferences.location,
          age_group: preferences.age_group,
          preferred_language: preferences.preferred_language
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error('Multilingual personalized content service unavailable');
      }
    } catch (error) {
      console.error('Error fetching multilingual personalized content:', error);
      return null;
    }
  }

  getFallbackLanguage() {
    return {
      detected_language: 'en',
      alternative_languages: ['sw'],
      county: 'Unknown',
      distance_km: 0,
      confidence: 0.5,
      language_info: {
        code: 'en',
        name: 'English',
        native_name: 'English',
        region: 'National'
      },
      radio_streams: ['http://ice1.somafm.com/groovesalad-256-mp3'],
      regional_stations: [
        { name: 'Kagema FM', stream: 'http://ice1.somafm.com/groovesalad-256-mp3', frequency: '103.5 FM' }
      ],
      localized_content: {
        content: {
          greeting: 'Welcome to Kagema FM',
          weather_intro: 'Current weather in your area:',
          news_intro: 'Here are the latest news updates:',
          music_intro: 'Trending music for you:',
          traffic_intro: 'Traffic update:',
          emergency_prefix: 'EMERGENCY ALERT:'
        }
      }
    };
  }

  async saveLanguagePreference(languageData) {
    try {
      const preferences = {
        detected_language: languageData.detected_language,
        county: languageData.county,
        confidence: languageData.confidence,
        timestamp: Date.now()
      };
      await AsyncStorage.setItem('languagePreferences', JSON.stringify(preferences));
    } catch (error) {
      console.error('Error saving language preferences:', error);
    }
  }

  async getLanguagePreferences() {
    try {
      const preferences = await AsyncStorage.getItem('languagePreferences');
      return preferences ? JSON.parse(preferences) : null;
    } catch (error) {
      console.error('Error getting language preferences:', error);
      return null;
    }
  }

  getLanguageDisplayName(languageCode) {
    const languageNames = {
      'en': 'English',
      'sw': 'Kiswahili',
      'ki': 'Gĩkũyũ',
      'luo': 'Dholuo',
      'luy': 'Luluhya',
      'kam': 'Kikamba',
      'kal': 'Kalenjin'
    };
    
    return languageNames[languageCode] || languageCode;
  }

  formatLocalizedContent(content, data) {
    if (!content || !data) return data;
    
    const localized = { ...data };
    
    // Apply localized prefixes/introductions
    if (data.weather && content.weather_intro) {
      localized.weather_intro = content.weather_intro;
    }
    
    if (data.news && content.news_intro) {
      localized.news_intro = content.news_intro;
    }
    
    if (data.music && content.music_intro) {
      localized.music_intro = content.music_intro;
    }
    
    return localized;
  }

  getCurrentLanguage() {
    return this.currentLanguage || 'en';
  }

  getCurrentLocation() {
    return this.currentLocation || 'Unknown';
  }

  clearCache() {
    this.cache.clear();
  }
}

export default new LanguageService();