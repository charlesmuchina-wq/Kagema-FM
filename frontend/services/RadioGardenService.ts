import AsyncStorage from '@react-native-async-storage/async-storage';

export interface RadioGardenStation {
  id: string;
  title: string;
  url: string;
  country: string;
  countryCode: string;
  place: string;
  geo: [number, number]; // [latitude, longitude]
  secure: boolean;
  subtitle?: string;
  website?: string;
  size?: number; // Listener count estimate
}

export interface RadioGardenPlace {
  id: string;
  title: string;
  country: string;
  size: number; // Number of stations
  geo: [number, number]; // [latitude, longitude]
  stations: RadioGardenStation[];
}

export interface RadioGardenCountry {
  title: string;
  code: string;
  places: RadioGardenPlace[];
  stationCount: number;
}

export class RadioGardenService {
  private static instance: RadioGardenService;
  private countries: RadioGardenCountry[] = [];
  private allStations: RadioGardenStation[] = [];
  private favoriteStations: string[] = [];
  private isInitialized = false;

  static getInstance(): RadioGardenService {
    if (!RadioGardenService.instance) {
      RadioGardenService.instance = new RadioGardenService();
    }
    return RadioGardenService.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    console.log('🌍 Initializing Radio Garden service...');
    
    try {
      await this.loadRadioGardenData();
      await this.loadFavorites();
      this.isInitialized = true;
      
      console.log('✅ Radio Garden initialized with', this.allStations.length, 'stations from', this.countries.length, 'countries');
    } catch (error) {
      console.error('❌ Radio Garden initialization error:', error);
      // Load fallback data
      await this.loadFallbackData();
      this.isInitialized = true;
    }
  }

  private async loadRadioGardenData(): Promise<void> {
    try {
      console.log('🌍 Loading Radio Garden data from API...');
      
      // First try to load from real Radio Garden API
      await this.loadFromRealAPI();
      
      if (this.countries.length === 0) {
        throw new Error('No data loaded from API, falling back to local data');
      }
      
    } catch (error) {
      console.warn('⚠️ Radio Garden API failed, using fallback data:', error);
      await this.loadFallbackData();
    }
  }

  private async loadFromRealAPI(): Promise<void> {
    try {
      // Radio Garden API endpoints (reverse engineered from their web app)
      const apiBase = 'https://radio.garden/api';
      
      // Get countries and places
      const araConcatResponse = await fetch(`${apiBase}/ara/content/places`);
      if (!araConcatResponse.ok) {
        throw new Error(`API request failed: ${araConcatResponse.status}`);
      }
      
      const placesData = await araConcatResponse.json();
      
      if (placesData && placesData.data && placesData.data.list) {
        await this.processRadioGardenPlaces(placesData.data.list);
      } else {
        throw new Error('Invalid API response structure');
      }
      
      console.log('✅ Successfully loaded Radio Garden data from API');
      
    } catch (error) {
      console.error('❌ Radio Garden API loading failed:', error);
      throw error;
    }
  }

  private async processRadioGardenPlaces(places: any[]): Promise<void> {
    const countryMap = new Map<string, RadioGardenCountry>();
    
    for (const place of places.slice(0, 100)) { // Limit to avoid overwhelming the app
      try {
        if (!place.geo || !place.id || !place.title) continue;
        
        const countryCode = place.country || 'Unknown';
        const countryName = this.getCountryName(countryCode);
        
        if (!countryMap.has(countryCode)) {
          countryMap.set(countryCode, {
            title: countryName,
            code: countryCode,
            places: [],
            stationCount: 0
          });
        }
        
        const country = countryMap.get(countryCode)!;
        
        // Get stations for this place
        const stations = await this.getStationsForPlace(place.id);
        
        if (stations.length > 0) {
          const radioGardenPlace: RadioGardenPlace = {
            id: place.id,
            title: place.title,
            country: countryName,
            size: place.size || stations.length,
            geo: place.geo,
            stations: stations
          };
          
          country.places.push(radioGardenPlace);
          country.stationCount += stations.length;
          this.allStations.push(...stations);
        }
        
        // Add small delay to avoid overwhelming the API
        await this.delay(100);
        
      } catch (error) {
        console.warn(`Failed to process place ${place.id}:`, error);
      }
    }
    
    this.countries = Array.from(countryMap.values())
      .filter(country => country.places.length > 0)
      .sort((a, b) => a.title.localeCompare(b.title));
  }

  private async getStationsForPlace(placeId: string): Promise<RadioGardenStation[]> {
    try {
      const response = await fetch(`https://radio.garden/api/ara/content/page/${placeId}`);
      if (!response.ok) return [];
      
      const data = await response.json();
      const stations: RadioGardenStation[] = [];
      
      if (data.data && data.data.content) {
        for (const item of data.data.content) {
          if (item.type === 'channel' && item.href) {
            const channelId = item.href.replace('/listen/', '');
            
            stations.push({
              id: channelId,
              title: item.title || 'Unknown Station',
              url: `https://radio.garden/api/ara/content/listen/${channelId}/channel.mp3`,
              country: data.data.country || 'Unknown',
              countryCode: data.data.countryCode || 'XX',
              place: data.data.title || 'Unknown',
              geo: data.data.geo || [0, 0],
              secure: true,
              subtitle: item.subtitle,
              size: item.listeners
            });
          }
        }
      }
      
      return stations;
    } catch (error) {
      return [];
    }
  }

  private getCountryName(countryCode: string): string {
    const countryNames: { [key: string]: string } = {
      'US': 'United States', 'GB': 'United Kingdom', 'DE': 'Germany', 'FR': 'France',
      'IT': 'Italy', 'ES': 'Spain', 'NL': 'Netherlands', 'BE': 'Belgium', 'CH': 'Switzerland',
      'AT': 'Austria', 'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland',
      'PL': 'Poland', 'CZ': 'Czech Republic', 'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria',
      'GR': 'Greece', 'PT': 'Portugal', 'IE': 'Ireland', 'LU': 'Luxembourg', 'MT': 'Malta',
      'CY': 'Cyprus', 'EE': 'Estonia', 'LV': 'Latvia', 'LT': 'Lithuania', 'SK': 'Slovakia',
      'SI': 'Slovenia', 'HR': 'Croatia', 'RS': 'Serbia', 'BA': 'Bosnia and Herzegovina',
      'ME': 'Montenegro', 'MK': 'North Macedonia', 'AL': 'Albania', 'XK': 'Kosovo',
      'CA': 'Canada', 'MX': 'Mexico', 'BR': 'Brazil', 'AR': 'Argentina', 'CL': 'Chile',
      'CO': 'Colombia', 'PE': 'Peru', 'VE': 'Venezuela', 'EC': 'Ecuador', 'BO': 'Bolivia',
      'UY': 'Uruguay', 'PY': 'Paraguay', 'GY': 'Guyana', 'SR': 'Suriname', 'GF': 'French Guiana',
      'JP': 'Japan', 'KR': 'South Korea', 'CN': 'China', 'IN': 'India', 'ID': 'Indonesia',
      'TH': 'Thailand', 'MY': 'Malaysia', 'SG': 'Singapore', 'PH': 'Philippines', 'VN': 'Vietnam',
      'TW': 'Taiwan', 'HK': 'Hong Kong', 'MO': 'Macau', 'AU': 'Australia', 'NZ': 'New Zealand',
      'ZA': 'South Africa', 'EG': 'Egypt', 'MA': 'Morocco', 'TN': 'Tunisia', 'DZ': 'Algeria',
      'LY': 'Libya', 'SD': 'Sudan', 'ET': 'Ethiopia', 'KE': 'Kenya', 'UG': 'Uganda',
      'TZ': 'Tanzania', 'RW': 'Rwanda', 'BI': 'Burundi', 'DJ': 'Djibouti', 'SO': 'Somalia',
      'ER': 'Eritrea', 'SS': 'South Sudan', 'CF': 'Central African Republic', 'TD': 'Chad',
      'CM': 'Cameroon', 'GA': 'Gabon', 'GQ': 'Equatorial Guinea', 'ST': 'São Tomé and Príncipe',
      'RU': 'Russia', 'UA': 'Ukraine', 'BY': 'Belarus', 'MD': 'Moldova', 'GE': 'Georgia',
      'AM': 'Armenia', 'AZ': 'Azerbaijan', 'KZ': 'Kazakhstan', 'KG': 'Kyrgyzstan',
      'UZ': 'Uzbekistan', 'TJ': 'Tajikistan', 'TM': 'Turkmenistan', 'AF': 'Afghanistan',
      'PK': 'Pakistan', 'BD': 'Bangladesh', 'LK': 'Sri Lanka', 'MV': 'Maldives',
      'BT': 'Bhutan', 'NP': 'Nepal', 'MM': 'Myanmar', 'LA': 'Laos', 'KH': 'Cambodia',
      'TR': 'Turkey', 'IR': 'Iran', 'IQ': 'Iraq', 'SY': 'Syria', 'LB': 'Lebanon',
      'JO': 'Jordan', 'IL': 'Israel', 'PS': 'Palestine', 'SA': 'Saudi Arabia', 'YE': 'Yemen',
      'OM': 'Oman', 'AE': 'United Arab Emirates', 'QA': 'Qatar', 'BH': 'Bahrain', 'KW': 'Kuwait'
    };
    return countryNames[countryCode] || countryCode;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async loadFallbackData(): Promise<void> {
    // Fallback data with more comprehensive global coverage
    
    const radioGardenData: RadioGardenCountry[] = [
      {
        title: 'United States',
        code: 'US',
        stationCount: 1245,
        places: [
          {
            id: 'new_york',
            title: 'New York',
            country: 'United States',
            size: 85,
            geo: [40.7128, -74.0060],
            stations: [
              {
                id: 'wnyc_fm',
                title: 'WNYC 93.9 FM',
                url: 'https://fm939.wnyc.org/wnycfm',
                country: 'United States',
                countryCode: 'US',
                place: 'New York',
                geo: [40.7128, -74.0060],
                secure: true,
                subtitle: 'New York Public Radio',
                size: 125000
              },
              {
                id: 'wcbs_am',
                title: 'WCBS 880 AM',
                url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/WCBSAMAAC.aac',
                country: 'United States',
                countryCode: 'US',
                place: 'New York',
                geo: [40.7128, -74.0060],
                secure: true,
                subtitle: 'News Radio 880',
                size: 95000
              }
            ]
          },
          {
            id: 'los_angeles',
            title: 'Los Angeles',
            country: 'United States',
            size: 72,
            geo: [34.0522, -118.2437],
            stations: [
              {
                id: 'kcrw_fm',
                title: 'KCRW 89.9 FM',
                url: 'https://kcrw.streamguys1.com/kcrw_192k_mp3_on_air',
                country: 'United States',
                countryCode: 'US',
                place: 'Los Angeles',
                geo: [34.0522, -118.2437],
                secure: true,
                subtitle: 'Music, News & Culture from Santa Monica',
                size: 87000
              }
            ]
          }
        ]
      },
      {
        title: 'United Kingdom',
        code: 'GB',
        stationCount: 287,
        places: [
          {
            id: 'london',
            title: 'London',
            country: 'United Kingdom',
            size: 45,
            geo: [51.5074, -0.1278],
            stations: [
              {
                id: 'bbc_radio1',
                title: 'BBC Radio 1',
                url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: 'The best new music',
                size: 285000
              },
              {
                id: 'bbc_radio4',
                title: 'BBC Radio 4',
                url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_four',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: 'Intelligent speech',
                size: 195000
              },
              {
                id: 'capital_fm',
                title: 'Capital FM London',
                url: 'https://media-ssl.musicradio.com/CapitalMP3',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: "London's Number One Hit Music Station",
                size: 165000
              }
            ]
          }
        ]
      },
      {
        title: 'Germany',
        code: 'DE',
        stationCount: 423,
        places: [
          {
            id: 'berlin',
            title: 'Berlin',
            country: 'Germany',
            size: 38,
            geo: [52.5200, 13.4050],
            stations: [
              {
                id: 'fritz_fm',
                title: 'Fritz',
                url: 'https://streams.fritz.de/fritz/mp3-192/streams.fritz.de/',
                country: 'Germany',
                countryCode: 'DE',
                place: 'Berlin',
                geo: [52.5200, 13.4050],
                secure: true,
                subtitle: 'Das Jugendradio',
                size: 75000
              }
            ]
          },
          {
            id: 'munich',
            title: 'Munich',
            country: 'Germany',
            size: 25,
            geo: [48.1351, 11.5820],
            stations: [
              {
                id: 'bayern_3',
                title: 'Bayern 3',
                url: 'https://dispatcher.rndfnk.com/br/bayern3/live/mp3/mid',
                country: 'Germany',
                countryCode: 'DE',
                place: 'Munich',
                geo: [48.1351, 11.5820],
                secure: true,
                subtitle: 'Pop & Rock',
                size: 145000
              }
            ]
          }
        ]
      },
      {
        title: 'Kenya',
        code: 'KE',
        stationCount: 78,
        places: [
          {
            id: 'nairobi',
            title: 'Nairobi',
            country: 'Kenya',
            size: 18,
            geo: [-1.2921, 36.8219],
            stations: [
              {
                id: 'classic_fm',
                title: 'Classic 105 FM',
                url: 'https://classic105.streamafrica.net/classic105',
                country: 'Kenya',
                countryCode: 'KE',
                place: 'Nairobi',
                geo: [-1.2921, 36.8219],
                secure: true,
                subtitle: 'Nairobi Urban Music',
                size: 245000
              },
              {
                id: 'capital_fm_nairobi',
                title: 'Capital FM 98.4',
                url: 'https://capitalfm.streamafrica.net/capitalfm',
                country: 'Kenya',
                countryCode: 'KE',
                place: 'Nairobi',
                geo: [-1.2921, 36.8219],
                secure: true,
                subtitle: 'The Beat of Africa',
                size: 195000
              }
            ]
          },
          {
            id: 'mombasa',
            title: 'Mombasa',
            country: 'Kenya',
            size: 12,
            geo: [-4.0435, 39.6682],
            stations: [
              {
                id: 'pwani_fm',
                title: 'Pwani FM 98.6',
                url: 'https://pwanifm.streamafrica.net/pwanifm',
                country: 'Kenya',
                countryCode: 'KE',
                place: 'Mombasa',
                geo: [-4.0435, 39.6682],
                secure: true,
                subtitle: 'Coast Music & News',
                size: 85000
              }
            ]
          }
        ]
      },
      {
        title: 'Brazil',
        code: 'BR',
        stationCount: 512,
        places: [
          {
            id: 'sao_paulo',
            title: 'São Paulo',
            country: 'Brazil',
            size: 45,
            geo: [-23.5505, -46.6333],
            stations: [
              {
                id: 'jovem_pan',
                title: 'Jovem Pan FM',
                url: 'https://r4.ciclano.io:15045/stream',
                country: 'Brazil',
                countryCode: 'BR',
                place: 'São Paulo',
                geo: [-23.5505, -46.6333],
                secure: true,
                subtitle: 'Música Pop & Rock',
                size: 185000
              }
            ]
          },
          {
            id: 'rio_de_janeiro',
            title: 'Rio de Janeiro',
            country: 'Brazil',
            size: 32,
            geo: [-22.9068, -43.1729],
            stations: [
              {
                id: 'radio_globo',
                title: 'Rádio Globo Rio',
                url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_GLOBO_RJAAC.aac',
                country: 'Brazil',
                countryCode: 'BR',
                place: 'Rio de Janeiro',
                geo: [-22.9068, -43.1729],
                secure: true,
                subtitle: 'Notícias e Música',
                size: 125000
              }
            ]
          }
        ]
      },
      {
        title: 'Japan',
        code: 'JP',
        stationCount: 345,
        places: [
          {
            id: 'tokyo',
            title: 'Tokyo',
            country: 'Japan',
            size: 55,
            geo: [35.6762, 139.6503],
            stations: [
              {
                id: 'j_wave',
                title: 'J-Wave 81.3 FM',
                url: 'https://radiko.jp/v2/api/ts/playlist.m3u8?station_id=FMJ',
                country: 'Japan',
                countryCode: 'JP',
                place: 'Tokyo',
                geo: [35.6762, 139.6503],
                secure: true,
                subtitle: 'Tokyo Modern Music',
                size: 215000
              }
            ]
          }
        ]
      },
      {
        title: 'France',
        code: 'FR',
        stationCount: 298,
        places: [
          {
            id: 'paris',
            title: 'Paris',
            country: 'France',
            size: 42,
            geo: [48.8566, 2.3522],
            stations: [
              {
                id: 'france_inter',
                title: 'France Inter',
                url: 'https://icecast.radiofrance.fr/franceinter-midfi.mp3',
                country: 'France',
                countryCode: 'FR',
                place: 'Paris',
                geo: [48.8566, 2.3522],
                secure: true,
                subtitle: 'Radio généraliste de service public',
                size: 295000
              }
            ]
          }
        ]
      }
    ];

    this.countries = radioGardenData;
    this.allStations = radioGardenData.reduce((stations, country) => {
      const countryStations = country.places.reduce((placeStations, place) => {
        return [...placeStations, ...place.stations];
      }, [] as RadioGardenStation[]);
      return [...stations, ...countryStations];
    }, [] as RadioGardenStation[]);
  }

  private async loadFallbackData(): Promise<void> {
    // Minimal fallback data if main data fails
    this.countries = [
      {
        title: 'World Stations',
        code: 'WW',
        stationCount: 3,
        places: [
          {
            id: 'worldwide',
            title: 'Worldwide',
            country: 'Global',
            size: 3,
            geo: [0, 0],
            stations: [
              {
                id: 'bbc_world_fallback',
                title: 'BBC World Service',
                url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_world_service',
                country: 'Global',
                countryCode: 'WW',
                place: 'Worldwide',
                geo: [0, 0],
                secure: true,
                subtitle: 'Global News & Current Affairs',
                size: 2500000
              }
            ]
          }
        ]
      }
    ];
    this.allStations = this.countries[0].places[0].stations;
  }

  getCountries(): RadioGardenCountry[] {
    return this.countries.sort((a, b) => a.title.localeCompare(b.title));
  }

  getCountryByCode(code: string): RadioGardenCountry | undefined {
    return this.countries.find(country => country.code === code);
  }

  getPlacesByCountry(countryCode: string): RadioGardenPlace[] {
    const country = this.getCountryByCode(countryCode);
    return country ? country.places : [];
  }

  getStationsByPlace(placeId: string): RadioGardenStation[] {
    for (const country of this.countries) {
      for (const place of country.places) {
        if (place.id === placeId) {
          return place.stations;
        }
      }
    }
    return [];
  }

  getAllStations(): RadioGardenStation[] {
    return this.allStations;
  }

  searchStations(query: string): RadioGardenStation[] {
    const searchTerm = query.toLowerCase();
    return this.allStations.filter(station =>
      station.title.toLowerCase().includes(searchTerm) ||
      station.country.toLowerCase().includes(searchTerm) ||
      station.place.toLowerCase().includes(searchTerm) ||
      (station.subtitle && station.subtitle.toLowerCase().includes(searchTerm))
    );
  }

  getStationsByGeoRadius(center: [number, number], radiusKm: number): RadioGardenStation[] {
    return this.allStations.filter(station => {
      const distance = this.calculateDistance(center, station.geo);
      return distance <= radiusKm;
    });
  }

  private calculateDistance([lat1, lon1]: [number, number], [lat2, lon2]: [number, number]): number {
    const R = 6371; // Earth's radius in km
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  private toRadians(degrees: number): number {
    return degrees * (Math.PI/180);
  }

  getPopularStations(limit: number = 20): RadioGardenStation[] {
    return this.allStations
      .sort((a, b) => (b.size || 0) - (a.size || 0))
      .slice(0, limit);
  }

  getNearbyStations(userLocation: [number, number], limit: number = 10): RadioGardenStation[] {
    return this.getStationsByGeoRadius(userLocation, 1000) // 1000km radius
      .sort((a, b) => {
        const distA = this.calculateDistance(userLocation, a.geo);
        const distB = this.calculateDistance(userLocation, b.geo);
        return distA - distB;
      })
      .slice(0, limit);
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

  getFavoriteStations(): RadioGardenStation[] {
    return this.allStations.filter(station => this.favoriteStations.includes(station.id));
  }

  private async loadFavorites(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('radio_garden_favorites');
      if (stored) {
        this.favoriteStations = JSON.parse(stored);
      }
    } catch (error) {
      console.log('Error loading Radio Garden favorites:', error);
    }
  }

  private async saveFavorites(): Promise<void> {
    try {
      await AsyncStorage.setItem('radio_garden_favorites', JSON.stringify(this.favoriteStations));
    } catch (error) {
      console.log('Error saving Radio Garden favorites:', error);
    }
  }

  getTotalStationsCount(): number {
    return this.allStations.length;
  }

  getStatsummary() {
    return {
      totalStations: this.allStations.length,
      totalCountries: this.countries.length,
      totalPlaces: this.countries.reduce((total, country) => total + country.places.length, 0),
      favoriteCount: this.favoriteStations.length
    };
  }
}

export const radioGardenService = RadioGardenService.getInstance();