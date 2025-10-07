import AsyncStorage from '@react-native-async-storage/async-storage';

export interface StreemaStation {
  id: string;
  name: string;
  description: string;
  streamUrl: string;
  websiteUrl?: string;
  genre: string;
  city: string;
  country: string;
  countryCode: string;
  language: string;
  bitrate: string;
  listeners: number;
  tags: string[];
  logo?: string;
  frequency?: string;
  band?: 'FM' | 'AM' | 'DAB' | 'Online';
  coordinates?: [number, number];
}

export interface StreemaCountry {
  name: string;
  code: string;
  flag: string;
  stations: StreemaStation[];
  cities: StreemaCity[];
  totalStations: number;
}

export interface StreemaCity {
  name: string;
  country: string;
  coordinates: [number, number];
  stations: StreemaStation[];
}

export interface StreemaSearchResult {
  stations: StreemaStation[];
  totalResults: number;
  query: string;
  country?: string;
  city?: string;
}

export class StreemaService {
  private static instance: StreemaService;
  private countries: StreemaCountry[] = [];
  private favoriteStations: string[] = [];
  private isInitialized = false;
  private errorCount = 0;
  private maxRetries = 3;
  private retryDelay = 1000;

  static getInstance(): StreemaService {
    if (!StreemaService.instance) {
      StreemaService.instance = new StreemaService();
    }
    return StreemaService.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    console.log('🌍 Initializing Streema service...');
    
    try {
      await this.loadCuratedStations();
      await this.loadFavorites();
      this.isInitialized = true;
      
      console.log('✅ Streema service initialized with', this.getTotalStationsCount(), 'stations');
    } catch (error) {
      console.error('❌ Streema service initialization error:', error);
      this.handleError('initialization', error);
      this.isInitialized = true; // Initialize with fallback data
    }
  }

  private async loadCuratedStations(): Promise<void> {
    try {
      // Load curated international stations (avoiding direct Streema API due to rate limits/auth)
      this.countries = [
        {
          name: 'United States',
          code: 'US',
          flag: '🇺🇸',
          totalStations: 15000,
          cities: [
            {
              name: 'New York',
              country: 'United States',
              coordinates: [40.7128, -74.0060],
              stations: []
            }
          ],
          stations: [
            {
              id: 'npr_news',
              name: 'NPR News',
              description: 'National Public Radio - News and Information',
              streamUrl: 'https://npr-ice.streamguys1.com/live.mp3',
              websiteUrl: 'https://www.npr.org',
              genre: 'News/Talk',
              city: 'Washington DC',
              country: 'United States',
              countryCode: 'US',
              language: 'English',
              bitrate: '128kbps',
              listeners: 2500000,
              band: 'Online',
              tags: ['news', 'talk', 'public-radio', 'information'],
              coordinates: [38.9072, -77.0369]
            },
            {
              id: 'kexp_seattle',
              name: 'KEXP 90.3 FM',
              description: 'Where the Music Matters - Seattle Public Radio',
              streamUrl: 'https://kexp-mp3-128.streamguys1.com/kexp128.mp3',
              websiteUrl: 'https://www.kexp.org',
              genre: 'Alternative/Indie',
              city: 'Seattle',
              country: 'United States',
              countryCode: 'US',
              language: 'English',
              bitrate: '128kbps',
              listeners: 185000,
              frequency: '90.3',
              band: 'FM',
              tags: ['alternative', 'indie', 'seattle', 'public'],
              coordinates: [47.6062, -122.3321]
            },
            {
              id: 'wnyc_new_york',
              name: 'WNYC 93.9 FM',
              description: 'New York Public Radio',
              streamUrl: 'https://fm939.wnyc.org/wnycfm',
              websiteUrl: 'https://www.wnyc.org',
              genre: 'News/Talk',
              city: 'New York',
              country: 'United States',
              countryCode: 'US',
              language: 'English',
              bitrate: '128kbps',
              listeners: 450000,
              frequency: '93.9',
              band: 'FM',
              tags: ['news', 'talk', 'new-york', 'public'],
              coordinates: [40.7128, -74.0060]
            }
          ]
        },
        {
          name: 'United Kingdom',
          code: 'GB',
          flag: '🇬🇧',
          totalStations: 8500,
          cities: [
            {
              name: 'London',
              country: 'United Kingdom',
              coordinates: [51.5074, -0.1278],
              stations: []
            }
          ],
          stations: [
            {
              id: 'bbc_radio1',
              name: 'BBC Radio 1',
              description: 'The best new music and entertainment',
              streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
              websiteUrl: 'https://www.bbc.co.uk/radio1',
              genre: 'Pop/Dance',
              city: 'London',
              country: 'United Kingdom',
              countryCode: 'GB',
              language: 'English',
              bitrate: '128kbps',
              listeners: 8500000,
              frequency: '97-99',
              band: 'FM',
              tags: ['pop', 'dance', 'new-music', 'bbc'],
              coordinates: [51.5074, -0.1278]
            },
            {
              id: 'bbc_radio4',
              name: 'BBC Radio 4',
              description: 'Intelligent speech with news, current affairs, drama',
              streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm',
              websiteUrl: 'https://www.bbc.co.uk/radio4',
              genre: 'News/Talk',
              city: 'London',
              country: 'United Kingdom',
              countryCode: 'GB',
              language: 'English',
              bitrate: '128kbps',
              listeners: 9200000,
              frequency: '92.4-94.6',
              band: 'FM',
              tags: ['news', 'current-affairs', 'drama', 'speech'],
              coordinates: [51.5074, -0.1278]
            },
            {
              id: 'bbc_6music',
              name: 'BBC 6 Music',
              description: 'Alternative music - past, present and future',
              streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_6music',
              websiteUrl: 'https://www.bbc.co.uk/6music',
              genre: 'Alternative/Rock',
              city: 'London',
              country: 'United Kingdom',
              countryCode: 'GB',
              language: 'English',
              bitrate: '320kbps',
              listeners: 2450000,
              band: 'DAB',
              tags: ['alternative', 'rock', 'indie', 'experimental'],
              coordinates: [51.5074, -0.1278]
            }
          ]
        },
        {
          name: 'Germany',
          code: 'DE',
          flag: '🇩🇪',
          totalStations: 12000,
          cities: [
            {
              name: 'Berlin',
              country: 'Germany',
              coordinates: [52.5200, 13.4050],
              stations: []
            }
          ],
          stations: [
            {
              id: 'deutschlandfunk',
              name: 'Deutschlandfunk',
              description: 'German national public radio - news and culture',
              streamUrl: 'https://st01.sslstream.dlf.de/dlf/01/128/mp3/stream.mp3',
              websiteUrl: 'https://www.deutschlandfunk.de',
              genre: 'News/Culture',
              city: 'Berlin',
              country: 'Germany',
              countryCode: 'DE',
              language: 'German',
              bitrate: '128kbps',
              listeners: 3200000,
              band: 'Online',
              tags: ['news', 'culture', 'public-radio', 'german'],
              coordinates: [52.5200, 13.4050]
            },
            {
              id: 'bayern3',
              name: 'Bayern 3',
              description: 'Bavaria\'s hit radio with the newest pop music',
              streamUrl: 'https://br-bayern3-live.cast.addradio.de/br/bayern3/live/mp3/128/stream.mp3',
              websiteUrl: 'https://www.bayern3.de',
              genre: 'Pop/Rock',
              city: 'Munich',
              country: 'Germany',
              countryCode: 'DE',
              language: 'German',
              bitrate: '128kbps',
              listeners: 1850000,
              frequency: 'Various',
              band: 'FM',
              tags: ['pop', 'rock', 'hits', 'bavaria'],
              coordinates: [48.1351, 11.5820]
            }
          ]
        },
        {
          name: 'France',
          code: 'FR',
          flag: '🇫🇷',
          totalStations: 9800,
          cities: [
            {
              name: 'Paris',
              country: 'France',
              coordinates: [48.8566, 2.3522],
              stations: []
            }
          ],
          stations: [
            {
              id: 'fip_radio',
              name: 'FIP Radio',
              description: 'Eclectic music without advertising',
              streamUrl: 'https://icecast.radiofrance.fr/fip-hifi.aac',
              websiteUrl: 'https://www.fip.fr',
              genre: 'Eclectic',
              city: 'Paris',
              country: 'France',
              countryCode: 'FR',
              language: 'French',
              bitrate: '320kbps',
              listeners: 1250000,
              frequency: '105.1',
              band: 'FM',
              tags: ['eclectic', 'no-ads', 'french', 'quality'],
              coordinates: [48.8566, 2.3522]
            },
            {
              id: 'france_inter',
              name: 'France Inter',
              description: 'French national public radio',
              streamUrl: 'https://icecast.radiofrance.fr/franceinter-hifi.aac',
              websiteUrl: 'https://www.franceinter.fr',
              genre: 'News/Talk',
              city: 'Paris',
              country: 'France',
              countryCode: 'FR',
              language: 'French',
              bitrate: '320kbps',
              listeners: 5850000,
              frequency: '87.8',
              band: 'FM',
              tags: ['news', 'talk', 'public-radio', 'french'],
              coordinates: [48.8566, 2.3522]
            }
          ]
        },
        {
          name: 'Canada',
          code: 'CA',
          flag: '🇨🇦',
          totalStations: 6200,
          cities: [
            {
              name: 'Toronto',
              country: 'Canada',
              coordinates: [43.6532, -79.3832],
              stations: []
            }
          ],
          stations: [
            {
              id: 'cbc_radio_one_toronto',
              name: 'CBC Radio One Toronto',
              description: 'Canadian public radio - news and information',
              streamUrl: 'https://cbc_r1_tor.akacast.akamaistream.net/7/877/451661/v1/rc.akacast.akamaistream.net/cbc_r1_tor',
              websiteUrl: 'https://www.cbc.ca/radio/radio1',
              genre: 'News/Talk',
              city: 'Toronto',
              country: 'Canada',
              countryCode: 'CA',
              language: 'English',
              bitrate: '128kbps',
              listeners: 2450000,
              frequency: '99.1',
              band: 'FM',
              tags: ['news', 'talk', 'public-radio', 'canadian'],
              coordinates: [43.6532, -79.3832]
            }
          ]
        },
        {
          name: 'Australia',
          code: 'AU',
          flag: '🇦🇺',
          totalStations: 4800,
          cities: [
            {
              name: 'Sydney',
              country: 'Australia',
              coordinates: [-33.8688, 151.2093],
              stations: []
            }
          ],
          stations: [
            {
              id: 'abc_classic',
              name: 'ABC Classic',
              description: 'Australia\'s classical music radio',
              streamUrl: 'https://live-radio01.mediahubaustralia.com/2CLW/mp3/',
              websiteUrl: 'https://www.abc.net.au/classic',
              genre: 'Classical',
              city: 'Sydney',
              country: 'Australia',
              countryCode: 'AU',
              language: 'English',
              bitrate: '128kbps',
              listeners: 950000,
              frequency: '92.9',
              band: 'FM',
              tags: ['classical', 'abc', 'australian', 'culture'],
              coordinates: [-33.8688, 151.2093]
            },
            {
              id: 'triple_j',
              name: 'triple j',
              description: 'Alternative youth radio - unearthing new music',
              streamUrl: 'https://live-radio01.mediahubaustralia.com/2JJW/mp3/',
              websiteUrl: 'https://www.abc.net.au/triplej',
              genre: 'Alternative/Youth',
              city: 'Sydney',
              country: 'Australia',
              countryCode: 'AU',
              language: 'English',
              bitrate: '128kbps',
              listeners: 1850000,
              frequency: '105.7',
              band: 'FM',
              tags: ['alternative', 'youth', 'new-music', 'australian'],
              coordinates: [-33.8688, 151.2093]
            }
          ]
        }
      ];

      console.log(`🌍 Loaded ${this.countries.length} Streema countries with ${this.getTotalStationsCount()} stations`);
      
    } catch (error) {
      console.error('❌ Failed to load Streema stations:', error);
      throw error;
    }
  }

  async searchStations(query: string, country?: string, city?: string): Promise<StreemaSearchResult> {
    try {
      console.log(`🔍 Searching Streema stations for: ${query}`);
      
      const allStations = this.getAllStations();
      const searchTerm = query.toLowerCase();
      
      const filteredStations = allStations.filter(station => {
        const matchesQuery = 
          station.name.toLowerCase().includes(searchTerm) ||
          station.description.toLowerCase().includes(searchTerm) ||
          station.genre.toLowerCase().includes(searchTerm) ||
          station.city.toLowerCase().includes(searchTerm) ||
          station.tags.some(tag => tag.includes(searchTerm));
          
        const matchesCountry = !country || 
          station.country.toLowerCase() === country.toLowerCase() ||
          station.countryCode.toLowerCase() === country.toLowerCase();
          
        const matchesCity = !city || 
          station.city.toLowerCase() === city.toLowerCase();
          
        return matchesQuery && matchesCountry && matchesCity;
      });

      return {
        stations: filteredStations,
        totalResults: filteredStations.length,
        query,
        country,
        city
      };

    } catch (error) {
      console.error('❌ Streema search error:', error);
      this.handleError('search', error);
      return {
        stations: [],
        totalResults: 0,
        query,
        country,
        city
      };
    }
  }

  getStationsByCountry(countryCode: string): StreemaStation[] {
    try {
      const country = this.countries.find(c => 
        c.code.toLowerCase() === countryCode.toLowerCase() ||
        c.name.toLowerCase() === countryCode.toLowerCase()
      );
      return country ? country.stations : [];
    } catch (error) {
      console.error('❌ Error getting stations by country:', error);
      this.handleError('getStationsByCountry', error);
      return [];
    }
  }

  getStationsByGenre(genre: string): StreemaStation[] {
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

  getStationsByLocation(latitude: number, longitude: number, radiusKm: number = 200): StreemaStation[] {
    try {
      const allStations = this.getAllStations();
      
      return allStations.filter(station => {
        if (!station.coordinates) return false;
        
        const distance = this.calculateDistance(
          latitude, longitude,
          station.coordinates[0], station.coordinates[1]
        );
        return distance <= radiusKm;
      }).sort((a, b) => {
        if (!a.coordinates || !b.coordinates) return 0;
        
        const distanceA = this.calculateDistance(latitude, longitude, a.coordinates[0], a.coordinates[1]);
        const distanceB = this.calculateDistance(latitude, longitude, b.coordinates[0], b.coordinates[1]);
        return distanceA - distanceB;
      });
    } catch (error) {
      console.error('❌ Error getting stations by location:', error);
      this.handleError('getStationsByLocation', error);
      return [];
    }
  }

  getPopularStations(limit: number = 20): StreemaStation[] {
    try {
      const allStations = this.getAllStations();
      return allStations
        .sort((a, b) => b.listeners - a.listeners)
        .slice(0, limit);
    } catch (error) {
      console.error('❌ Error getting popular stations:', error);
      return [];
    }
  }

  getAllStations(): StreemaStation[] {
    try {
      return this.countries.flatMap(country => country.stations);
    } catch (error) {
      console.error('❌ Error getting all stations:', error);
      return [];
    }
  }

  getCountries(): StreemaCountry[] {
    return this.countries;
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

  getFavoriteStations(): StreemaStation[] {
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(url, { 
        method: 'HEAD',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.warn('⚠️ Stream validation failed:', url, error);
      return false;
    }
  }

  // Private helper methods
  private async loadFavorites(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('streema_favorites');
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
      await AsyncStorage.setItem('streema_favorites', JSON.stringify(this.favoriteStations));
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
    
    console.error('🚨 Streema Service Error:', errorInfo);
    
    // Add error pattern to suppressor if it's a known issue
    if (error?.message?.includes('CORS') || 
        error?.message?.includes('fetch') ||
        error?.message?.includes('AbortError') ||
        error?.message?.includes('NetworkError')) {
      this.addErrorPattern(new RegExp(error.message.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'));
    }

    // Implement retry logic for critical operations
    if (this.errorCount <= this.maxRetries && 
        ['initialization', 'loadCuratedStations'].includes(operation)) {
      console.log(`🔄 Retrying ${operation} in ${this.retryDelay}ms (attempt ${this.errorCount}/${this.maxRetries})`);
      setTimeout(() => {
        if (operation === 'initialization') {
          this.initialize();
        }
      }, this.retryDelay);
      
      this.retryDelay *= 2; // Exponential backoff
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

  // Service health and monitoring
  getServiceHealth(): { 
    healthy: boolean; 
    errorCount: number; 
    lastCheck: string; 
    totalStations: number;
    countries: number;
  } {
    return {
      healthy: this.errorCount < this.maxRetries && this.isInitialized,
      errorCount: this.errorCount,
      lastCheck: new Date().toISOString(),
      totalStations: this.getTotalStationsCount(),
      countries: this.countries.length
    };
  }

  // Get service statistics
  getServiceStats(): {
    totalStations: number;
    countriesAvailable: number;
    topGenres: { genre: string; count: number }[];
    topCountries: { country: string; count: number }[];
  } {
    try {
      const allStations = this.getAllStations();
      
      // Calculate genre distribution
      const genreMap = new Map<string, number>();
      const countryMap = new Map<string, number>();
      
      allStations.forEach(station => {
        genreMap.set(station.genre, (genreMap.get(station.genre) || 0) + 1);
        countryMap.set(station.country, (countryMap.get(station.country) || 0) + 1);
      });

      const topGenres = Array.from(genreMap.entries())
        .map(([genre, count]) => ({ genre, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      const topCountries = Array.from(countryMap.entries())
        .map(([country, count]) => ({ country, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);

      return {
        totalStations: allStations.length,
        countriesAvailable: this.countries.length,
        topGenres,
        topCountries
      };
    } catch (error) {
      console.error('❌ Error getting service stats:', error);
      return {
        totalStations: 0,
        countriesAvailable: 0,
        topGenres: [],
        topCountries: []
      };
    }
  }
}

// Export singleton instance
export const streemaService = StreemaService.getInstance();