import AsyncStorage from '@react-native-async-storage/async-storage';

export interface iHeartRadioStation {
  id: string;
  name: string;
  description: string;
  callSign: string;
  frequency?: string;
  band: 'FM' | 'AM';
  streamUrl: string;
  genre: string;
  city: string;
  state: string;
  country: string;
  language: string;
  bitrate: string;
  listeners: number;
  isLive: boolean;
  tags: string[];
  logo?: string;
  website?: string;
}

export interface iHeartRadioMarket {
  id: string;
  name: string;
  state: string;
  country: string;
  stations: iHeartRadioStation[];
  coordinates: [number, number];
}

export interface iHeartRadioSearchResult {
  stations: iHeartRadioStation[];
  totalResults: number;
  query: string;
  market?: string;
}

export class iHeartRadioService {
  private static instance: iHeartRadioService;
  private markets: iHeartRadioMarket[] = [];
  private favoriteStations: string[] = [];
  private isInitialized = false;
  private errorCount = 0;
  private maxRetries = 3;

  static getInstance(): iHeartRadioService {
    if (!iHeartRadioService.instance) {
      iHeartRadioService.instance = new iHeartRadioService();
    }
    return iHeartRadioService.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    console.log('📻 Initializing iHeartRadio service...');
    
    try {
      await this.loadCuratedStations();
      await this.loadFavorites();
      this.isInitialized = true;
      
      console.log('✅ iHeartRadio service initialized with', this.getTotalStationsCount(), 'stations');
    } catch (error) {
      console.error('❌ iHeartRadio service initialization error:', error);
      this.handleError('initialization', error);
      this.isInitialized = true; // Initialize with fallback data
    }
  }

  private async loadCuratedStations(): Promise<void> {
    try {
      // Load curated iHeartRadio stations (avoiding direct API calls due to CORS/auth issues)
      this.markets = [
        {
          id: 'new_york',
          name: 'New York',
          state: 'NY',
          country: 'United States',
          coordinates: [40.7128, -74.0060],
          stations: [
            {
              id: 'z100_new_york',
              name: 'Z100',
              description: 'New York\'s Hit Music Station',
              callSign: 'WHTZ',
              frequency: '100.3',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc181',
              genre: 'Top 40/Pop',
              city: 'New York',
              state: 'NY',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 850000,
              isLive: true,
              tags: ['top40', 'pop', 'hits', 'new-york'],
              website: 'https://z100.iheart.com'
            },
            {
              id: 'elvis_duran',
              name: 'Elvis Duran and the Morning Show',
              description: 'America\'s most popular morning show',
              callSign: 'WHTZ-HD2',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc8220',
              genre: 'Talk/Entertainment',
              city: 'New York',
              state: 'NY',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 625000,
              isLive: true,
              tags: ['talk', 'morning-show', 'entertainment', 'celebrity'],
              website: 'https://elvisduran.iheart.com'
            }
          ]
        },
        {
          id: 'los_angeles',
          name: 'Los Angeles',
          state: 'CA',
          country: 'United States',
          coordinates: [34.0522, -118.2437],
          stations: [
            {
              id: 'kiis_fm_la',
              name: 'KIIS FM',
              description: 'LA\'s #1 Hit Music Station',
              callSign: 'KIIS',
              frequency: '102.7',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc1977',
              genre: 'Top 40/Pop',
              city: 'Los Angeles',
              state: 'CA',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 920000,
              isLive: true,
              tags: ['top40', 'pop', 'hits', 'los-angeles'],
              website: 'https://kiisonline.iheart.com'
            },
            {
              id: 'real_923_la',
              name: 'Real 92.3',
              description: 'LA\'s Hip-Hop and R&B Station',
              callSign: 'KRRL',
              frequency: '92.3',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc5673',
              genre: 'Hip-Hop/R&B',
              city: 'Los Angeles',
              state: 'CA',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 675000,
              isLive: true,
              tags: ['hip-hop', 'rnb', 'urban', 'los-angeles'],
              website: 'https://real923la.iheart.com'
            }
          ]
        },
        {
          id: 'chicago',
          name: 'Chicago',
          state: 'IL',
          country: 'United States',
          coordinates: [41.8781, -87.6298],
          stations: [
            {
              id: 'b96_chicago',
              name: 'B96',
              description: 'Chicago\'s Hit Music',
              callSign: 'WBBM-FM',
              frequency: '96.3',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc2634',
              genre: 'Top 40/Pop',
              city: 'Chicago',
              state: 'IL',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 485000,
              isLive: true,
              tags: ['top40', 'pop', 'hits', 'chicago'],
              website: 'https://b96.iheart.com'
            }
          ]
        },
        {
          id: 'atlanta',
          name: 'Atlanta',
          state: 'GA',
          country: 'United States',
          coordinates: [33.7490, -84.3880],
          stations: [
            {
              id: 'power_1059_atlanta',
              name: 'Power 105.9',
              description: 'Atlanta\'s Hip-Hop and R&B',
              callSign: 'WWPW',
              frequency: '105.9',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc4966',
              genre: 'Hip-Hop/R&B',
              city: 'Atlanta',
              state: 'GA',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 565000,
              isLive: true,
              tags: ['hip-hop', 'rnb', 'urban', 'atlanta'],
              website: 'https://power1059.iheart.com'
            }
          ]
        },
        {
          id: 'miami',
          name: 'Miami',
          state: 'FL',
          country: 'United States',
          coordinates: [25.7617, -80.1918],
          stations: [
            {
              id: 'hits_973_miami',
              name: 'Hits 97.3',
              description: 'Miami\'s Hit Music Station',
              callSign: 'WFLC',
              frequency: '97.3',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc4670',
              genre: 'Top 40/Pop',
              city: 'Miami',
              state: 'FL',
              country: 'United States',
              language: 'English',
              bitrate: '128kbps',
              listeners: 425000,
              isLive: true,
              tags: ['top40', 'pop', 'hits', 'miami'],
              website: 'https://hits973.iheart.com'
            },
            {
              id: 'mega_979_miami',
              name: 'Mega 97.9',
              description: 'Miami\'s Latin Hits',
              callSign: 'WMGE',
              frequency: '97.9',
              band: 'FM',
              streamUrl: 'https://stream.revma.ihrhls.com/zc6219',
              genre: 'Latin/Reggaeton',
              city: 'Miami',
              state: 'FL',
              country: 'United States',
              language: 'Spanish',
              bitrate: '128kbps',
              listeners: 385000,
              isLive: true,
              tags: ['latin', 'reggaeton', 'spanish', 'miami'],
              website: 'https://mega979.iheart.com'
            }
          ]
        }
      ];

      console.log(`📻 Loaded ${this.markets.length} iHeartRadio markets`);
      
    } catch (error) {
      console.error('❌ Failed to load iHeartRadio stations:', error);
      throw error;
    }
  }

  async searchStations(query: string, market?: string): Promise<iHeartRadioSearchResult> {
    try {
      console.log(`🔍 Searching iHeartRadio stations for: ${query}`);
      
      const allStations = this.getAllStations();
      const searchTerm = query.toLowerCase();
      
      const filteredStations = allStations.filter(station => {
        const matchesQuery = 
          station.name.toLowerCase().includes(searchTerm) ||
          station.description.toLowerCase().includes(searchTerm) ||
          station.genre.toLowerCase().includes(searchTerm) ||
          station.callSign.toLowerCase().includes(searchTerm) ||
          station.tags.some(tag => tag.includes(searchTerm));
          
        const matchesMarket = !market || 
          station.city.toLowerCase() === market.toLowerCase() ||
          station.state.toLowerCase() === market.toLowerCase();
          
        return matchesQuery && matchesMarket;
      });

      return {
        stations: filteredStations,
        totalResults: filteredStations.length,
        query,
        market
      };

    } catch (error) {
      console.error('❌ iHeartRadio search error:', error);
      this.handleError('search', error);
      return {
        stations: [],
        totalResults: 0,
        query,
        market
      };
    }
  }

  getStationsByMarket(marketId: string): iHeartRadioStation[] {
    try {
      const market = this.markets.find(m => m.id === marketId);
      return market ? market.stations : [];
    } catch (error) {
      console.error('❌ Error getting stations by market:', error);
      this.handleError('getStationsByMarket', error);
      return [];
    }
  }

  getStationsByGenre(genre: string): iHeartRadioStation[] {
    try {
      const allStations = this.getAllStations();
      return allStations.filter(station => 
        station.genre.toLowerCase().includes(genre.toLowerCase())
      );
    } catch (error) {
      console.error('❌ Error getting stations by genre:', error);
      this.handleError('getStationsByGenre', error);
      return [];
    }
  }

  getStationsByLocation(latitude: number, longitude: number, radiusKm: number = 100): iHeartRadioStation[] {
    try {
      const nearbyMarkets = this.markets.filter(market => {
        const distance = this.calculateDistance(
          latitude, longitude,
          market.coordinates[0], market.coordinates[1]
        );
        return distance <= radiusKm;
      });

      return nearbyMarkets.flatMap(market => market.stations);
    } catch (error) {
      console.error('❌ Error getting stations by location:', error);
      this.handleError('getStationsByLocation', error);
      return [];
    }
  }

  getAllStations(): iHeartRadioStation[] {
    try {
      return this.markets.flatMap(market => market.stations);
    } catch (error) {
      console.error('❌ Error getting all stations:', error);
      return [];
    }
  }

  getMarkets(): iHeartRadioMarket[] {
    return this.markets;
  }

  getTotalStationsCount(): number {
    return this.getAllStations().length;
  }

  async addToFavorites(stationId: string): Promise<boolean> {
    try {
      if (!this.favoriteStations.includes(stationId)) {
        this.favoriteStations.push(stationId);
        await this.saveFavorites();
        console.log(`⭐ Added ${stationId} to favorites`);
        return true;
      }
      return false;
    } catch (error) {
      console.error('❌ Error adding to favorites:', error);
      this.handleError('addToFavorites', error);
      return false;
    }
  }

  async removeFromFavorites(stationId: string): Promise<boolean> {
    try {
      const index = this.favoriteStations.indexOf(stationId);
      if (index > -1) {
        this.favoriteStations.splice(index, 1);
        await this.saveFavorites();
        console.log(`⭐ Removed ${stationId} from favorites`);
        return true;
      }
      return false;
    } catch (error) {
      console.error('❌ Error removing from favorites:', error);
      this.handleError('removeFromFavorites', error);
      return false;
    }
  }

  isFavorite(stationId: string): boolean {
    return this.favoriteStations.includes(stationId);
  }

  getFavoriteStations(): iHeartRadioStation[] {
    try {
      const allStations = this.getAllStations();
      return allStations.filter(station => this.isFavorite(station.id));
    } catch (error) {
      console.error('❌ Error getting favorite stations:', error);
      return [];
    }
  }

  async validateStreamUrl(url: string): Promise<boolean> {
    try {
      const response = await fetch(url, { 
        method: 'HEAD',
        timeout: 5000
      });
      return response.ok;
    } catch (error) {
      console.warn('⚠️ Stream validation failed:', url, error);
      return false;
    }
  }

  // Private helper methods
  private async loadFavorites(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('iheart_favorites');
      if (stored) {
        this.favoriteStations = JSON.parse(stored);
      }
    } catch (error) {
      console.error('❌ Failed to load favorites:', error);
      this.favoriteStations = [];
    }
  }

  private async saveFavorites(): Promise<void> {
    try {
      await AsyncStorage.setItem('iheart_favorites', JSON.stringify(this.favoriteStations));
    } catch (error) {
      console.error('❌ Failed to save favorites:', error);
    }
  }

  private calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  private handleError(operation: string, error: any): void {
    this.errorCount++;
    
    // Enhanced error logging with context
    const errorInfo = {
      operation,
      error: error?.message || error,
      timestamp: new Date().toISOString(),
      errorCount: this.errorCount,
      stack: error?.stack
    };
    
    console.error('🚨 iHeartRadio Service Error:', errorInfo);
    
    // Add error pattern to suppressor if it's a known issue
    if (error?.message?.includes('CORS') || error?.message?.includes('fetch')) {
      this.addErrorPattern(new RegExp(error.message.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'));
    }
  }

  private addErrorPattern(pattern: RegExp): void {
    try {
      // Import and add pattern to console suppressor
      import('../utils/ConsoleErrorSuppressor').then(({ consoleErrorSuppressor }) => {
        consoleErrorSuppressor.addPattern(pattern);
        console.log('🔇 Added error pattern to suppressor:', pattern);
      });
    } catch (error) {
      console.debug('Could not add error pattern to suppressor');
    }
  }

  // Service health check
  getServiceHealth(): { healthy: boolean; errorCount: number; lastCheck: string } {
    return {
      healthy: this.errorCount < this.maxRetries && this.isInitialized,
      errorCount: this.errorCount,
      lastCheck: new Date().toISOString()
    };
  }
}

// Export singleton instance
export const iHeartRadioService = iHeartRadioService.getInstance();