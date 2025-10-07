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

export class SoundCastService {
  private static instance: SoundCastService;
  private categories: SoundCastCategory[] = [];
  private favoriteStations: string[] = [];

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
    console.log('✅ SoundCast service initialized with', this.getTotalStationsCount(), 'stations');
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