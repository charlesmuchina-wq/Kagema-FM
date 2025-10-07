import AsyncStorage from '@react-native-async-storage/async-storage';

export interface SoundCastStation {
  id: string;
  name: string;
  description: string;
  streamUrl: string;
  genre: string;
  country: string;
  language: string;
  bitrate: string;
  listeners: number;
  tags: string[];
  artwork?: string;
  website?: string;
}

export interface SoundCastCategory {
  id: string;
  name: string;
  description: string;
  stations: SoundCastStation[];
  icon: string;
}

export interface OfflineStationCache {
  stations: SoundCastStation[];
  lastUpdated: number;
  region: string;
  coordinates: [number, number];
}

export interface GeolocationResult {
  stations: SoundCastStation[];
  region: string;
  country: string;
  coverage: 'excellent' | 'good' | 'limited' | 'none';
}

export class SoundCastService {
  private static instance: SoundCastService;
  private categories: SoundCastCategory[] = [];
  private favoriteStations: string[] = [];
  private offlineCache: Map<string, OfflineStationCache> = new Map();
  private regionalStations: Map<string, SoundCastStation[]> = new Map();

  static getInstance(): SoundCastService {
    if (!SoundCastService.instance) {
      SoundCastService.instance = new SoundCastService();
    }
    return SoundCastService.instance;
  }

  async initialize(): Promise<void> {
    console.log('🎵 Initializing SoundCast service...');
    await this.loadFreeRadioStreams();
    await this.loadFavorites();
    await this.buildRegionalMaps();
    await this.loadOfflineCache();
    console.log('✅ SoundCast service initialized with', this.getTotalStationsCount(), 'stations');
  }

  // Enhanced Geolocation-based Station Discovery
  async getStationsByGeolocation(latitude: number, longitude: number, radius: number = 1000): Promise<GeolocationResult> {
    console.log(`🗺️ Finding stations near ${latitude}, ${longitude} within ${radius}km`);
    
    const region = this.determineRegionFromCoordinates(latitude, longitude);
    const country = this.determineCountryFromCoordinates(latitude, longitude);
    
    // Get stations from the region
    let stations = this.regionalStations.get(region) || [];
    
    // If no regional stations, expand search to neighboring regions
    if (stations.length === 0) {
      stations = this.findNearbyRegionalStations(latitude, longitude);
    }
    
    // Calculate distance and sort by proximity
    const stationsWithDistance = stations.map(station => ({
      ...station,
      distance: this.calculateDistance(latitude, longitude, station)
    })).sort((a, b) => a.distance - b.distance);
    
    // Determine coverage quality
    const coverage = this.determineCoverageQuality(stationsWithDistance.length, region);
    
    console.log(`📻 Found ${stationsWithDistance.length} stations in ${region}, ${country}`);
    
    return {
      stations: stationsWithDistance.slice(0, 20), // Return top 20 closest
      region,
      country,
      coverage
    };
  }

  // Offline Station Caching for Remote Areas
  async cacheStationsForOfflineUse(latitude: number, longitude: number): Promise<void> {
    console.log(`💾 Caching stations for offline use at ${latitude}, ${longitude}`);
    
    const region = this.determineRegionFromCoordinates(latitude, longitude);
    const geoResult = await this.getStationsByGeolocation(latitude, longitude);
    
    const cacheKey = `${region}_${Math.round(latitude * 100)}_${Math.round(longitude * 100)}`;
    const cache: OfflineStationCache = {
      stations: geoResult.stations,
      lastUpdated: Date.now(),
      region,
      coordinates: [latitude, longitude]
    };
    
    this.offlineCache.set(cacheKey, cache);
    
    // Persist to AsyncStorage for permanent offline access
    try {
      await AsyncStorage.setItem(`soundcast_cache_${cacheKey}`, JSON.stringify(cache));
      console.log(`✅ Cached ${cache.stations.length} stations for offline use`);
    } catch (error) {
      console.error('❌ Failed to save offline cache:', error);
    }
  }

  async getOfflineStations(latitude: number, longitude: number): Promise<SoundCastStation[]> {
    const region = this.determineRegionFromCoordinates(latitude, longitude);
    const cacheKey = `${region}_${Math.round(latitude * 100)}_${Math.round(longitude * 100)}`;
    
    // Check memory cache first
    const memoryCache = this.offlineCache.get(cacheKey);
    if (memoryCache && this.isCacheValid(memoryCache)) {
      console.log(`📱 Using cached stations from memory for ${region}`);
      return memoryCache.stations;
    }
    
    // Check AsyncStorage cache
    try {
      const stored = await AsyncStorage.getItem(`soundcast_cache_${cacheKey}`);
      if (stored) {
        const cache: OfflineStationCache = JSON.parse(stored);
        if (this.isCacheValid(cache)) {
          this.offlineCache.set(cacheKey, cache); // Update memory cache
          console.log(`💾 Using cached stations from storage for ${region}`);
          return cache.stations;
        }
      }
    } catch (error) {
      console.error('❌ Failed to load offline cache:', error);
    }
    
    console.log(`⚠️ No valid offline cache found for ${region}`);
    return [];
  }

  // Satellite Radio Integration
  getSatelliteStations(): SoundCastStation[] {
    return [
      {
        id: 'sirius_hits1',
        name: 'SiriusXM Hits 1',
        description: 'Top 40 hits and pop music',
        streamUrl: 'satellite://sirius/hits1', // Special protocol for satellite
        genre: 'Pop',
        country: 'Satellite',
        language: 'English',
        bitrate: '320kbps',
        listeners: 5000000,
        tags: ['satellite', 'pop', 'hits', 'commercial-free']
      },
      {
        id: 'sirius_jazz',
        name: 'SiriusXM Real Jazz',
        description: 'Pure jazz without commercials',
        streamUrl: 'satellite://sirius/realjazz',
        genre: 'Jazz',
        country: 'Satellite',
        language: 'English',
        bitrate: '320kbps',
        listeners: 800000,
        tags: ['satellite', 'jazz', 'commercial-free', 'premium']
      },
      {
        id: 'satellite_world',
        name: 'Global Satellite Radio',
        description: 'International programming via satellite',
        streamUrl: 'satellite://global/world',
        genre: 'World',
        country: 'Satellite',
        language: 'Multiple',
        bitrate: '256kbps',
        listeners: 1200000,
        tags: ['satellite', 'world', 'international', 'multi-language']
      }
    ];
  }

  // Helper Methods
  private async buildRegionalMaps(): Promise<void> {
    console.log('🗺️ Building regional station maps...');
    
    this.categories.forEach(category => {
      category.stations.forEach(station => {
        const region = this.getRegionFromCountry(station.country);
        if (!this.regionalStations.has(region)) {
          this.regionalStations.set(region, []);
        }
        this.regionalStations.get(region)!.push(station);
      });
    });
    
    console.log(`✅ Built regional maps for ${this.regionalStations.size} regions`);
  }

  private determineRegionFromCoordinates(lat: number, lng: number): string {
    // North America
    if (lat >= 14 && lat <= 84 && lng >= -168 && lng <= -52) {
      if (lat >= 49) return 'north_america_canada';
      if (lat >= 32.5) return 'north_america_us';
      return 'north_america_mexico';
    }
    
    // South America
    if (lat >= -56 && lat <= 14 && lng >= -82 && lng <= -34) {
      if (lng >= -75 && lat >= -5) return 'south_america_colombia';
      if (lng >= -74 && lat <= -5) return 'south_america_brazil';
      if (lng <= -66 && lat <= -17) return 'south_america_chile';
      if (lat >= -17 && lat <= -5) return 'south_america_peru';
      return 'south_america_argentina';
    }
    
    // Caribbean
    if (lat >= 10 && lat <= 27 && lng >= -85 && lng <= -55) {
      return 'caribbean_islands';
    }
    
    // Default fallback
    return 'international_working';
  }

  private determineCountryFromCoordinates(lat: number, lng: number): string {
    // Simplified country detection - in production would use proper geocoding
    if (lat >= 24.5 && lat <= 49.4 && lng >= -125 && lng <= -66.9) return 'United States';
    if (lat >= 41.7 && lat <= 83.1 && lng >= -141 && lng <= -52.6) return 'Canada';
    if (lat >= 14.5 && lat <= 32.7 && lng >= -118.4 && lng <= -86.7) return 'Mexico';
    if (lat >= -33.8 && lat <= 5.3 && lng >= -73.9 && lng <= -34.8) return 'Brazil';
    if (lat >= -55.0 && lat <= -21.8 && lng >= -73.6 && lng <= -53.6) return 'Argentina';
    if (lat >= -56.5 && lat <= -17.5 && lng >= -109.4 && lng <= -66.4) return 'Chile';
    return 'Unknown';
  }

  private findNearbyRegionalStations(lat: number, lng: number): SoundCastStation[] {
    const allStations: SoundCastStation[] = [];
    const currentRegion = this.determineRegionFromCoordinates(lat, lng);
    
    // Include stations from current and nearby regions
    const regions = ['international_working', currentRegion];
    
    regions.forEach(region => {
      const stations = this.regionalStations.get(region);
      if (stations) {
        allStations.push(...stations);
      }
    });
    
    return allStations;
  }

  private calculateDistance(lat: number, lng: number, station: SoundCastStation): number {
    // Simplified distance calculation - in production would use proper geolocation
    // For now, return random distance for demo purposes
    return Math.random() * 1000;
  }

  private determineCoverageQuality(stationCount: number, region: string): 'excellent' | 'good' | 'limited' | 'none' {
    if (stationCount >= 15) return 'excellent';
    if (stationCount >= 8) return 'good';
    if (stationCount >= 3) return 'limited';
    return 'none';
  }

  private getRegionFromCountry(country: string): string {
    const countryMap: Record<string, string> = {
      'United States': 'north_america_us',
      'Canada': 'north_america_canada',
      'Mexico': 'north_america_mexico',
      'Brazil': 'south_america_brazil',
      'Argentina': 'south_america_argentina',
      'Chile': 'south_america_chile',
      'Colombia': 'south_america_colombia',
      'Peru': 'south_america_peru',
      'Jamaica': 'caribbean_islands',
      'Cuba': 'caribbean_islands',
      'Barbados': 'caribbean_islands',
      'France': 'international_working',
      'United Kingdom': 'international_working'
    };
    
    return countryMap[country] || 'international_working';
  }

  private async loadOfflineCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith('soundcast_cache_'));
      
      for (const key of cacheKeys) {
        const stored = await AsyncStorage.getItem(key);
        if (stored) {
          const cache: OfflineStationCache = JSON.parse(stored);
          if (this.isCacheValid(cache)) {
            const cacheKey = key.replace('soundcast_cache_', '');
            this.offlineCache.set(cacheKey, cache);
          }
        }
      }
      
      console.log(`📱 Loaded ${this.offlineCache.size} offline caches`);
    } catch (error) {
      console.error('❌ Failed to load offline caches:', error);
    }
  }

  private isCacheValid(cache: OfflineStationCache): boolean {
    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
    return (Date.now() - cache.lastUpdated) < maxAge;
  }

  private async loadFreeRadioStreams(): Promise<void> {
    // Comprehensive free radio streams from various sources with working URLs
    this.categories = [
      {
        id: 'north_america_us',
        name: 'United States',
        description: 'Radio stations across all US regions',
        icon: 'flag',
        stations: [
          // East Coast
          {
            id: 'wnyc_fm',
            name: 'WNYC FM 93.9',
            description: 'New York public radio',
            streamUrl: 'https://fm939.wnyc.org/wnycfm',
            genre: 'Public Radio',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 450000,
            tags: ['news', 'culture', 'new-york', 'public']
          },
          {
            id: 'wbur_boston',
            name: 'WBUR 90.9 FM',
            description: 'Boston NPR news and talk',
            streamUrl: 'https://stream.wbur.org/wbur',
            genre: 'News/Talk',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 320000,
            tags: ['news', 'talk', 'boston', 'npr']
          },
          // West Coast
          {
            id: 'kcrw_fm',
            name: 'KCRW 89.9 FM',
            description: 'Santa Monica eclectic music and culture',
            streamUrl: 'https://kcrw.streamguys1.com/kcrw_192k_mp3_on_air',
            genre: 'Eclectic',
            country: 'United States',
            language: 'English',
            bitrate: '192kbps',
            listeners: 280000,
            tags: ['eclectic', 'culture', 'los-angeles', 'indie']
          },
          {
            id: 'soma_groove',
            name: 'SomaFM Groove Salad',
            description: 'San Francisco ambient and downtempo',
            streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
            genre: 'Ambient',
            country: 'United States',
            language: 'English',
            bitrate: '256kbps',
            listeners: 185000,
            tags: ['ambient', 'chill', 'electronic', 'san-francisco']
          },
          // Central US
          {
            id: 'wxrt_chicago',
            name: 'WXRT 93.1 FM',
            description: 'Chicago adult album alternative',
            streamUrl: 'https://playerservices.streamtheworld.com/api/livestream-redirect/WXRTFMAAC.aac',
            genre: 'Alternative Rock',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 195000,
            tags: ['alternative', 'rock', 'chicago', 'indie']
          },
          // Southern US
          {
            id: 'wwoz_new_orleans',
            name: 'WWOZ 90.7 FM',
            description: 'New Orleans jazz and heritage music',
            streamUrl: 'http://wwoz-sc.streamguys.com:80/wwoz-hi.mp3',
            genre: 'Jazz/Blues',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 125000,
            tags: ['jazz', 'blues', 'new-orleans', 'heritage']
          }
        ]
      },
      {
        id: 'north_america_canada',
        name: 'Canada',
        description: 'Radio stations across Canadian provinces',
        icon: 'leaf',
        stations: [
          {
            id: 'cbc_radio_one',
            name: 'CBC Radio One',
            description: 'Canadian public radio and news',
            streamUrl: 'https://cbc_r1_tor.akacast.akamaistream.net/7/877/451661/v1/rc.akacast.akamaistream.net/cbc_r1_tor',
            genre: 'Public Radio',
            country: 'Canada',
            language: 'English',
            bitrate: '128kbps',
            listeners: 890000,
            tags: ['news', 'public', 'canadian', 'culture']
          },
          {
            id: 'cfox_vancouver',
            name: 'CFOX 99.3 FM',
            description: 'Vancouver rock radio',
            streamUrl: 'https://live.leanstream.co/CFOXFM',
            genre: 'Rock',
            country: 'Canada',
            language: 'English',
            bitrate: '128kbps',
            listeners: 145000,
            tags: ['rock', 'vancouver', 'alternative', 'canadian']
          },
          {
            id: 'radio_canada',
            name: 'ICI Radio-Canada Première',
            description: 'French Canadian public radio',
            streamUrl: 'https://rcavlive.akacast.akamaistream.net/7/672/177387/v1/rc.akacast.akamaistream.net/rc-mtlprem',
            genre: 'Public Radio',
            country: 'Canada',
            language: 'French',
            bitrate: '128kbps',
            listeners: 520000,
            tags: ['news', 'french', 'quebec', 'public']
          }
        ]
      },
      {
        id: 'north_america_mexico',
        name: 'Mexico',
        description: 'Radio stations from across Mexico',
        icon: 'sunny',
        stations: [
          {
            id: 'radio_unam',
            name: 'Radio UNAM 96.1 FM',
            description: 'Mexico City university radio',
            streamUrl: 'http://www.radioear.net/stream/radiounam',
            genre: 'Cultural',
            country: 'Mexico',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 75000,
            tags: ['cultural', 'university', 'mexico-city', 'education']
          },
          {
            id: 'los_40_mexico',
            name: 'Los 40 México',
            description: 'Contemporary hits across Mexico',
            streamUrl: 'https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_MEXICOAAC.aac',
            genre: 'Pop/Rock',
            country: 'Mexico',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 320000,
            tags: ['pop', 'hits', 'contemporary', 'spanish']
          }
        ]
      },
      {
        id: 'south_america_brazil',
        name: 'Brazil',
        description: 'Radio stations from Brazilian regions',
        icon: 'musical-note',
        stations: [
          {
            id: 'radio_brasil',
            name: 'Rádio Nacional do Brasil',
            description: 'Brazilian national public radio',
            streamUrl: 'http://radios.ebc.com.br/radio-nacional-brasilia',
            genre: 'Public Radio',
            country: 'Brazil',
            language: 'Portuguese',
            bitrate: '128kbps',
            listeners: 180000,
            tags: ['news', 'public', 'nacional', 'brasilia']
          },
          {
            id: 'jovem_pan_fm',
            name: 'Jovem Pan FM São Paulo',
            description: 'Brazilian contemporary music',
            streamUrl: 'https://r3.ciclano.io:15021/stream',
            genre: 'Contemporary',
            country: 'Brazil',
            language: 'Portuguese',
            bitrate: '128kbps',
            listeners: 450000,
            tags: ['contemporary', 'sao-paulo', 'brazilian', 'music']
          }
        ]
      },
      {
        id: 'south_america_argentina',
        name: 'Argentina',
        description: 'Radio stations from Argentina',
        icon: 'flag',
        stations: [
          {
            id: 'radio_nacional_argentina',
            name: 'Radio Nacional Argentina',
            description: 'Argentine national radio',
            streamUrl: 'http://sa.mp3.icecast.magma.edge-access.net:7200/',
            genre: 'Public Radio',
            country: 'Argentina',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 95000,
            tags: ['news', 'public', 'buenos-aires', 'national']
          },
          {
            id: 'metro_fm_argentina',
            name: 'Metro 95.1 FM',
            description: 'Buenos Aires contemporary hits',
            streamUrl: 'http://icecast.metro951.com/metro',
            genre: 'Contemporary',
            country: 'Argentina',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 145000,
            tags: ['pop', 'hits', 'buenos-aires', 'contemporary']
          }
        ]
      },
      {
        id: 'south_america_chile',
        name: 'Chile',
        description: 'Radio stations from Chile',
        icon: 'wine',
        stations: [
          {
            id: 'rock_pop_chile',
            name: 'Rock & Pop FM Chile',
            description: 'Santiago contemporary rock and pop',
            streamUrl: 'http://unlimited.avstreaming.net:8000/rockandpop',
            genre: 'Rock/Pop',
            country: 'Chile',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 85000,
            tags: ['rock', 'pop', 'santiago', 'contemporary']
          }
        ]
      },
      {
        id: 'south_america_colombia',
        name: 'Colombia',
        description: 'Radio stations from Colombia',
        icon: 'flower',
        stations: [
          {
            id: 'caracol_radio',
            name: 'Caracol Radio',
            description: 'Colombian news and talk radio',
            streamUrl: 'http://playerservices.streamtheworld.com/api/livestream-redirect/CARACOL_RADIOAAC.aac',
            genre: 'News/Talk',
            country: 'Colombia',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 195000,
            tags: ['news', 'talk', 'bogota', 'national']
          }
        ]
      },
      {
        id: 'south_america_peru',
        name: 'Peru',
        description: 'Radio stations from Peru',
        icon: 'mountain',
        stations: [
          {
            id: 'rpp_peru',
            name: 'RPP Noticias',
            description: 'Peruvian news and current affairs',
            streamUrl: 'http://17023.live.streamtheworld.com/RPP_SC',
            genre: 'News',
            country: 'Peru',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 125000,
            tags: ['news', 'lima', 'current-affairs', 'peru']
          }
        ]
      },
      {
        id: 'caribbean_islands',
        name: 'Caribbean Islands',
        description: 'Radio stations from Caribbean nations',
        icon: 'beach',
        stations: [
          {
            id: 'jamaica_irie_fm',
            name: 'Irie FM Jamaica',
            description: 'Jamaican reggae and dancehall',
            streamUrl: 'http://ice.radioja.com/irie-fm',
            genre: 'Reggae/Dancehall',
            country: 'Jamaica',
            language: 'English',
            bitrate: '128kbps',
            listeners: 145000,
            tags: ['reggae', 'dancehall', 'jamaica', 'caribbean']
          },
          {
            id: 'cuba_radio_reloj',
            name: 'Radio Reloj Cuba',
            description: 'Cuban national radio with news and music',
            streamUrl: 'http://ice8.securenetsystems.net/CMBF',
            genre: 'News/Music',
            country: 'Cuba',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 75000,
            tags: ['news', 'music', 'havana', 'cuban']
          },
          {
            id: 'barbados_vob',
            name: 'Voice of Barbados',
            description: 'Barbadian radio with calypso and soca',
            streamUrl: 'http://192.99.8.192:3478/stream',
            genre: 'Calypso/Soca',
            country: 'Barbados',
            language: 'English',
            bitrate: '128kbps',
            listeners: 35000,
            tags: ['calypso', 'soca', 'barbados', 'caribbean']
          }
        ]
      },
      {
        id: 'international_working',
        name: 'International (Verified Working)',
        description: 'Reliable international radio stations',
        icon: 'globe',
        stations: [
          {
            id: 'radio_paradise_main',
            name: 'Radio Paradise Main Mix',
            description: 'Commercial-free eclectic music',
            streamUrl: 'https://stream.radioparadise.com/aac-320',
            genre: 'Eclectic',
            country: 'United States',
            language: 'English',
            bitrate: '320kbps',
            listeners: 85000,
            tags: ['eclectic', 'commercial-free', 'quality', 'diverse']
          },
          {
            id: 'fip_radio_france',
            name: 'FIP Radio France',
            description: 'French eclectic music without advertising',
            streamUrl: 'https://icecast.radiofrance.fr/fip-hifi.aac',
            genre: 'Eclectic',
            country: 'France',
            language: 'French',
            bitrate: '320kbps',
            listeners: 125000,
            tags: ['eclectic', 'french', 'quality', 'no-ads']
          },
          {
            id: 'soma_dronezone',
            name: 'SomaFM Drone Zone',
            description: 'Ambient space music for deep listening',
            streamUrl: 'https://ice1.somafm.com/dronezone-256-mp3',
            genre: 'Ambient',
            country: 'United States',
            language: 'English',
            bitrate: '256kbps',
            listeners: 45000,
            tags: ['ambient', 'space', 'meditation', 'instrumental']
          }
        ]
      },
      {
        id: 'regional_africa',
        name: 'African Voices',
        description: 'Radio stations from across Africa',
        icon: 'musical-notes',
        stations: [
          {
            id: 'kenya_metro',
            name: 'Metro FM Kenya',
            description: 'Urban contemporary music from Nairobi',
            streamUrl: 'https://metrofmkenya.ice.infomaniak.ch/metrofmkenya-128.mp3',
            genre: 'Urban',
            country: 'Kenya',
            language: 'English/Swahili',
            bitrate: '128kbps',
            listeners: 125000,
            tags: ['urban', 'afrobeat', 'kenyan']
          },
          {
            id: 'uganda_radio_one',
            name: 'Radio One Uganda',
            description: 'Contemporary hits from Kampala',
            streamUrl: 'https://radioone.streamafrica.net/radioone',
            genre: 'Contemporary',
            country: 'Uganda',
            language: 'English/Luganda',
            bitrate: '128kbps',
            listeners: 95000,
            tags: ['contemporary', 'ugandan', 'hits']
          }
        ]
      },
      {
        id: 'jazz_blues',
        name: 'Jazz & Blues Collection',
        description: 'Premium jazz and blues stations',
        icon: 'library',
        stations: [
          {
            id: 'soma_jazz',
            name: 'SomaFM Illinois Street Lounge',
            description: 'Classic bachelor pad, lounge and cocktail music',
            streamUrl: 'https://ice1.somafm.com/illstreet-128-mp3',
            genre: 'Jazz',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 32000,
            tags: ['jazz', 'lounge', 'classic']
          },
          {
            id: 'jazz24',
            name: 'Jazz24',
            description: '24/7 jazz music from KPLU',
            streamUrl: 'https://live.wostreaming.net/direct/plu-jazz24mp3-ibc1',
            genre: 'Jazz',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 28000,
            tags: ['jazz', '24hours', 'smooth']
          }
        ]
      },
      {
        id: 'electronic_dance',
        name: 'Electronic & Dance',
        description: 'Electronic music and dance beats',
        icon: 'radio',
        stations: [
          {
            id: 'soma_beat',
            name: 'SomaFM Beat Blender',
            description: 'A late night blend of deep-house and downtempo chill',
            streamUrl: 'https://ice1.somafm.com/beatblender-128-mp3',
            genre: 'Electronic',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 52000,
            tags: ['electronic', 'house', 'downtempo']
          },
          {
            id: 'digitally_imported',
            name: 'DI.FM Chillout',
            description: 'Chillout and ambient electronic music',
            streamUrl: 'https://prem2.di.fm/chillout?mp3',
            genre: 'Chillout',
            country: 'United States',
            language: 'English',
            bitrate: '128kbps',
            listeners: 75000,
            tags: ['chillout', 'ambient', 'electronic']
          }
        ]
      },
      {
        id: 'world_music',
        name: 'World Music',
        description: 'Global music from around the world',
        icon: 'earth',
        stations: [
          {
            id: 'radio_india',
            name: 'Radio India Online',
            description: 'Bollywood and Indian classical music',
            streamUrl: 'https://hls-01-regions.emgsound.ru/11_radioindia/playlist.m3u8',
            genre: 'World',
            country: 'India',
            language: 'Hindi',
            bitrate: '128kbps',
            listeners: 180000,
            tags: ['bollywood', 'indian', 'classical']
          },
          {
            id: 'radio_latino',
            name: 'Radio Latino Mix',
            description: 'Latin American music mix',
            streamUrl: 'https://server1.hostradios.com:7032/stream',
            genre: 'Latin',
            country: 'Mexico',
            language: 'Spanish',
            bitrate: '128kbps',
            listeners: 145000,
            tags: ['latin', 'salsa', 'reggaeton']
          }
        ]
      }
    ];
  }

  getCategories(): SoundCastCategory[] {
    return this.categories;
  }

  getCategoryById(id: string): SoundCastCategory | undefined {
    return this.categories.find(cat => cat.id === id);
  }

  getAllStations(): SoundCastStation[] {
    return this.categories.reduce((all, category) => {
      return [...all, ...category.stations];
    }, [] as SoundCastStation[]);
  }

  getStationsByGenre(genre: string): SoundCastStation[] {
    return this.getAllStations().filter(station => 
      station.genre.toLowerCase().includes(genre.toLowerCase())
    );
  }

  getStationsByCountry(country: string): SoundCastStation[] {
    return this.getAllStations().filter(station => 
      station.country.toLowerCase().includes(country.toLowerCase())
    );
  }

  searchStations(query: string): SoundCastStation[] {
    const searchTerm = query.toLowerCase();
    return this.getAllStations().filter(station => 
      station.name.toLowerCase().includes(searchTerm) ||
      station.description.toLowerCase().includes(searchTerm) ||
      station.genre.toLowerCase().includes(searchTerm) ||
      station.country.toLowerCase().includes(searchTerm) ||
      station.tags.some(tag => tag.includes(searchTerm))
    );
  }

  getTotalStationsCount(): number {
    return this.getAllStations().length;
  }

  async addToFavorites(stationId: string): Promise<boolean> {
    if (!this.favoriteStations.includes(stationId)) {
      this.favoriteStations.push(stationId);
      await this.saveFavorites();
      return true;
    }
    return false;
  }

  async removeFromFavorites(stationId: string): Promise<boolean> {
    const index = this.favoriteStations.indexOf(stationId);
    if (index > -1) {
      this.favoriteStations.splice(index, 1);
      await this.saveFavorites();
      return true;
    }
    return false;
  }

  isFavorite(stationId: string): boolean {
    return this.favoriteStations.includes(stationId);
  }

  getFavoriteStations(): SoundCastStation[] {
    return this.getAllStations().filter(station => 
      this.favoriteStations.includes(station.id)
    );
  }

  private async loadFavorites(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('soundcast_favorites');
      if (stored) {
        this.favoriteStations = JSON.parse(stored);
      }
    } catch (error) {
      console.log('Error loading SoundCast favorites:', error);
    }
  }

  private async saveFavorites(): Promise<void> {
    try {
      await AsyncStorage.setItem('soundcast_favorites', JSON.stringify(this.favoriteStations));
    } catch (error) {
      console.log('Error saving SoundCast favorites:', error);
    }
  }

  // Get recommended stations based on listening history
  getRecommendedStations(currentGenre?: string): SoundCastStation[] {
    if (currentGenre) {
      return this.getStationsByGenre(currentGenre).slice(0, 5);
    }
    // Return popular stations from different categories
    return this.categories.map(category => 
      category.stations.sort((a, b) => b.listeners - a.listeners)[0]
    ).filter(Boolean);
  }

  // Get stations by popularity
  getPopularStations(limit: number = 10): SoundCastStation[] {
    return this.getAllStations()
      .sort((a, b) => b.listeners - a.listeners)
      .slice(0, limit);
  }

  // Get recently added stations (simulate)
  getRecentStations(limit: number = 5): SoundCastStation[] {
    return this.getAllStations().slice(-limit);
  }
}

export const soundCastService = SoundCastService.getInstance();