import AsyncStorage from '@react-native-async-storage/async-storage';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

class ContentService {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 15 * 60 * 1000; // 15 minutes
  }

  async getWeatherData(latitude, longitude) {
    const cacheKey = `weather_${latitude.toFixed(2)}_${longitude.toFixed(2)}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/location/weather`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude, longitude }),
      });

      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('Weather service unavailable');
      }
    } catch (error) {
      console.error('Error fetching weather:', error);
      return null;
    }
  }

  async getLocalNews(limit = 20) {
    const cacheKey = `local_news_${limit}`;
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/news/local?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('News service unavailable');
      }
    } catch (error) {
      console.error('Error fetching local news:', error);
      return { articles: [], summary: null, total_count: 0 };
    }
  }

  async getInternationalNews(limit = 15) {
    const cacheKey = `international_news_${limit}`;
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/news/international?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('International news service unavailable');
      }
    } catch (error) {
      console.error('Error fetching international news:', error);
      return { articles: [], summary: null, total_count: 0 };
    }
  }

  async getTrendingMusic(country = 'KE', limit = 30) {
    const cacheKey = `trending_music_${country}_${limit}`;
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/music/trending?country=${country}&limit=${limit}`
      );
      
      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('Music service unavailable');
      }
    } catch (error) {
      console.error('Error fetching trending music:', error);
      return { tracks: [], recommendations: null };
    }
  }

  async getKenyanMusic(limit = 20) {
    const cacheKey = `kenyan_music_${limit}`;
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/music/kenyan?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
      } else {
        throw new Error('Kenyan music service unavailable');
      }
    } catch (error) {
      console.error('Error fetching Kenyan music:', error);
      return { tracks: [], recommendations: null };
    }
  }

  async getPersonalizedContent(location, preferences) {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/personalized-content`, {
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
          age_group: preferences.age_group
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        throw new Error('Personalized content service unavailable');
      }
    } catch (error) {
      console.error('Error fetching personalized content:', error);
      return null;
    }
  }

  async saveUserPreferences(preferences) {
    try {
      await AsyncStorage.setItem('userPreferences', JSON.stringify(preferences));
    } catch (error) {
      console.error('Error saving user preferences:', error);
    }
  }

  async getUserPreferences() {
    try {
      const preferences = await AsyncStorage.getItem('userPreferences');
      return preferences ? JSON.parse(preferences) : {
        interests: [],
        favorite_genres: [],
        location: null,
        age_group: null
      };
    } catch (error) {
      console.error('Error getting user preferences:', error);
      return {
        interests: [],
        favorite_genres: [],
        location: null,
        age_group: null
      };
    }
  }

  clearCache() {
    this.cache.clear();
  }
}

export default new ContentService();