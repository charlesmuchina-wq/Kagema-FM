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

  // Removed duplicate private method - now public method is available

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
    console.log('📻 Loading comprehensive fallback Radio Garden data...');
    
    // Comprehensive fallback data with global coverage
    const fallbackData: RadioGardenCountry[] = [
      {
        title: 'United States',
        code: 'US',
        stationCount: 8,
        places: [
          {
            id: 'new_york_us',
            title: 'New York',
            country: 'United States',
            size: 3,
            geo: [40.7128, -74.0060],
            stations: [
              {
                id: 'wnyc_93_9',
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
                id: 'wcbs_880',
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
            id: 'los_angeles_us',
            title: 'Los Angeles',
            country: 'United States',
            size: 2,
            geo: [34.0522, -118.2437],
            stations: [
              {
                id: 'kcrw_89_9',
                title: 'KCRW 89.9 FM',
                url: 'https://kcrw.streamguys1.com/kcrw_192k_mp3_on_air',
                country: 'United States',
                countryCode: 'US',
                place: 'Los Angeles',
                geo: [34.0522, -118.2437],
                secure: true,
                subtitle: 'Music, News & Culture from Santa Monica',
                size: 87000
              },
              {
                id: 'kpcc_89_3',
                title: 'KPCC 89.3 FM',
                url: 'https://kpcc.streamguys1.com/kpcc_live',
                country: 'United States',
                countryCode: 'US',
                place: 'Los Angeles',
                geo: [34.0522, -118.2437],
                secure: true,
                subtitle: 'NPR News for Southern California',
                size: 72000
              }
            ]
          },
          {
            id: 'chicago_us',
            title: 'Chicago',
            country: 'United States',
            size: 2,
            geo: [41.8781, -87.6298],
            stations: [
              {
                id: 'wbez_91_5',
                title: 'WBEZ 91.5 FM',
                url: 'https://stream.wbez.org/wbez128.mp3',
                country: 'United States',
                countryCode: 'US',
                place: 'Chicago',
                geo: [41.8781, -87.6298],
                secure: true,
                subtitle: 'Chicago Public Media',
                size: 68000
              }
            ]
          }
        ]
      },
      {
        title: 'United Kingdom',
        code: 'GB',
        stationCount: 6,
        places: [
          {
            id: 'london_gb',
            title: 'London',
            country: 'United Kingdom',
            size: 4,
            geo: [51.5074, -0.1278],
            stations: [
              {
                id: 'bbc_radio1_gb',
                title: 'BBC Radio 1',
                url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: 'New Music & Entertainment',
                size: 850000
              },
              {
                id: 'bbc_radio4_gb',
                title: 'BBC Radio 4',
                url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_four',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: 'Intelligent Speech & Drama',
                size: 920000
              },
              {
                id: 'bbc_world_service_gb',
                title: 'BBC World Service',
                url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_world_service',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: 'Global News & Current Affairs',
                size: 2500000
              },
              {
                id: 'lbc_gb',
                title: 'LBC 97.3',
                url: 'https://icecast.thisisdax.com/LBCLondonMP3',
                country: 'United Kingdom',
                countryCode: 'GB',
                place: 'London',
                geo: [51.5074, -0.1278],
                secure: true,
                subtitle: 'Leading Britain\'s Conversation',
                size: 425000
              }
            ]
          }
        ]
      },
      {
        title: 'Germany',
        code: 'DE',
        stationCount: 4,
        places: [
          {
            id: 'berlin_de',
            title: 'Berlin',
            country: 'Germany',
            size: 2,
            geo: [52.5200, 13.4050],
            stations: [
              {
                id: 'deutschlandfunk',
                title: 'Deutschlandfunk',
                url: 'https://st01.sslstream.dlf.de/dlf/01/128/mp3/stream.mp3',
                country: 'Germany',
                countryCode: 'DE',
                place: 'Berlin',
                geo: [52.5200, 13.4050],
                secure: true,
                subtitle: 'Information, Bildung, Kultur',
                size: 285000
              },
              {
                id: 'rbb_info_radio',
                title: 'rbb Inforadio',
                url: 'https://dispatcher.rndfnk.com/rbb/inforadio/live/mp3/128/stream.mp3',
                country: 'Germany',
                countryCode: 'DE',
                place: 'Berlin',
                geo: [52.5200, 13.4050],
                secure: true,
                subtitle: 'Nachrichten und Information',
                size: 195000
              }
            ]
          }
        ]
      },
      {
        title: 'France',
        code: 'FR',
        stationCount: 3,
        places: [
          {
            id: 'paris_fr',
            title: 'Paris',
            country: 'France',
            size: 3,
            geo: [48.8566, 2.3522],
            stations: [
              {
                id: 'france_inter_fr',
                title: 'France Inter',
                url: 'https://icecast.radiofrance.fr/franceinter-midfi.mp3',
                country: 'France',
                countryCode: 'FR',
                place: 'Paris',
                geo: [48.8566, 2.3522],
                secure: true,
                subtitle: 'Radio généraliste de service public',
                size: 295000
              },
              {
                id: 'rtl_fr',
                title: 'RTL',
                url: 'https://streaming.radio.rtl.fr/rtl-1-48-192',
                country: 'France',
                countryCode: 'FR',
                place: 'Paris',
                geo: [48.8566, 2.3522],
                secure: true,
                subtitle: 'Toujours avec vous',
                size: 385000
              },
              {
                id: 'fip_fr',
                title: 'FIP',
                url: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
                country: 'France',
                countryCode: 'FR',
                place: 'Paris',
                geo: [48.8566, 2.3522],
                secure: true,
                subtitle: 'Musique éclectique',
                size: 125000
              }
            ]
          }
        ]
      },
      {
        title: 'Japan',
        code: 'JP',
        stationCount: 2,
        places: [
          {
            id: 'tokyo_jp',
            title: 'Tokyo',
            country: 'Japan',
            size: 2,
            geo: [35.6762, 139.6503],
            stations: [
              {
                id: 'nhk_world_radio',
                title: 'NHK World Radio Japan',
                url: 'https://nhkworld.webcdn.stream.ne.jp/www11/radiojapan/all/263942/live.m3u8',
                country: 'Japan',
                countryCode: 'JP',
                place: 'Tokyo',
                geo: [35.6762, 139.6503],
                secure: true,
                subtitle: 'NHK\'s International Broadcasting Service',
                size: 185000
              },
              {
                id: 'j_wave_jp',
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
        title: 'Brazil',
        code: 'BR',
        stationCount: 3,
        places: [
          {
            id: 'sao_paulo_br',
            title: 'São Paulo',
            country: 'Brazil',
            size: 2,
            geo: [-23.5505, -46.6333],
            stations: [
              {
                id: 'jovem_pan_br',
                title: 'Jovem Pan FM 100.9',
                url: 'https://r4.ciclano.io:15045/stream',
                country: 'Brazil',
                countryCode: 'BR',
                place: 'São Paulo',
                geo: [-23.5505, -46.6333],
                secure: true,
                subtitle: 'A rádio líder de audiência',
                size: 385000
              },
              {
                id: 'bandnews_fm',
                title: 'BandNews FM',
                url: 'https://evpp.mm.uol.com.br/radio/bandnews_fm_sp',
                country: 'Brazil',
                countryCode: 'BR',
                place: 'São Paulo',
                geo: [-23.5505, -46.6333],
                secure: true,
                subtitle: 'Rádio de notícias',
                size: 245000
              }
            ]
          },
          {
            id: 'rio_de_janeiro_br',
            title: 'Rio de Janeiro',
            country: 'Brazil',
            size: 1,
            geo: [-22.9068, -43.1729],
            stations: [
              {
                id: 'radio_globo_br',
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
        title: 'Australia',
        code: 'AU',
        stationCount: 3,
        places: [
          {
            id: 'sydney_au',
            title: 'Sydney',
            country: 'Australia',
            size: 2,
            geo: [-33.8688, 151.2093],
            stations: [
              {
                id: 'abc_sydney',
                title: 'ABC Sydney 702',
                url: 'https://live-radio02.mediahubaustralia.com/2SYW/mp3/',
                country: 'Australia',
                countryCode: 'AU',
                place: 'Sydney',
                geo: [-33.8688, 151.2093],
                secure: true,
                subtitle: 'Conversations and talkback',
                size: 185000
              },
              {
                id: 'triple_j',
                title: 'triple j',
                url: 'https://live-radio01.mediahubaustralia.com/2TJW/mp3/',
                country: 'Australia',
                countryCode: 'AU',
                place: 'Sydney',
                geo: [-33.8688, 151.2093],
                secure: true,
                subtitle: 'We Love Music',
                size: 295000
              }
            ]
          },
          {
            id: 'melbourne_au',
            title: 'Melbourne',
            country: 'Australia',
            size: 1,
            geo: [-37.8136, 144.9631],
            stations: [
              {
                id: 'abc_melbourne',
                title: 'ABC Melbourne 774',
                url: 'https://live-radio02.mediahubaustralia.com/3LNW/mp3/',
                country: 'Australia',
                countryCode: 'AU',
                place: 'Melbourne',
                geo: [-37.8136, 144.9631],
                secure: true,
                subtitle: 'Melbourne conversations',
                size: 165000
              }
            ]
          }
        ]
      },
      {
        title: 'Canada',
        code: 'CA',
        stationCount: 2,
        places: [
          {
            id: 'toronto_ca',
            title: 'Toronto',
            country: 'Canada',
            size: 2,
            geo: [43.6532, -79.3832],
            stations: [
              {
                id: 'cbc_radio_one_toronto',
                title: 'CBC Radio One Toronto',
                url: 'https://cbc_r1_tor.akacast.akamaistream.net/7/750/451661/v1/rc.akacast.akamaistream.net/cbc_r1_tor',
                country: 'Canada',
                countryCode: 'CA',
                place: 'Toronto',
                geo: [43.6532, -79.3832],
                secure: true,
                subtitle: 'CBC\'s flagship news and information service',
                size: 225000
              },
              {
                id: 'q107_toronto',
                title: 'Q107 Toronto',
                url: 'https://live.leanstream.co/CILQFM',
                country: 'Canada',
                countryCode: 'CA',
                place: 'Toronto',
                geo: [43.6532, -79.3832],
                secure: true,
                subtitle: 'Classic Rock',
                size: 185000
              }
            ]
          }
        ]
      },
      {
        title: 'South Africa',
        code: 'ZA',
        stationCount: 2,
        places: [
          {
            id: 'johannesburg_za',
            title: 'Johannesburg',
            country: 'South Africa',
            size: 2,
            geo: [-26.2041, 28.0473],
            stations: [
              {
                id: 'radio_702',
                title: '702 Talk Radio',
                url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO702AAC.aac',
                country: 'South Africa',
                countryCode: 'ZA',
                place: 'Johannesburg',
                geo: [-26.2041, 28.0473],
                secure: true,
                subtitle: 'Where Johannesburg Talks',
                size: 295000
              },
              {
                id: 'metro_fm_za',
                title: 'Metro FM',
                url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/METROFMAAC.aac',
                country: 'South Africa',
                countryCode: 'ZA',
                place: 'Johannesburg',
                geo: [-26.2041, 28.0473],
                secure: true,
                subtitle: 'Urban Contemporary',
                size: 385000
              }
            ]
          }
        ]
      },
      {
        title: 'India',
        code: 'IN',
        stationCount: 2,
        places: [
          {
            id: 'mumbai_in',
            title: 'Mumbai',
            country: 'India',
            size: 2,
            geo: [19.0760, 72.8777],
            stations: [
              {
                id: 'all_india_radio_mumbai',
                title: 'All India Radio Mumbai',
                url: 'https://air.pc.cdn.bitgravity.com/air/live/pbaudio056/playlist.m3u8',
                country: 'India',
                countryCode: 'IN',
                place: 'Mumbai',
                geo: [19.0760, 72.8777],
                secure: true,
                subtitle: 'AIR Mumbai FM Rainbow',
                size: 425000
              },
              {
                id: 'radio_mirchi_mumbai',
                title: 'Radio Mirchi 98.3 FM',
                url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/RADIOMIRCHI983AAC.aac',
                country: 'India',
                countryCode: 'IN',
                place: 'Mumbai',
                geo: [19.0760, 72.8777],
                secure: true,
                subtitle: 'It\'s Hot!',
                size: 685000
              }
            ]
          }
        ]
      }
    ];

    this.countries = fallbackData;
    
    // Flatten all stations for quick access
    this.allStations = [];
    for (const country of this.countries) {
      for (const place of country.places) {
        this.allStations.push(...place.stations);
      }
    }
    
    console.log('✅ Loaded comprehensive fallback data with', this.allStations.length, 'stations from', this.countries.length, 'countries');
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

  // Methods needed by RadioGardenMap component
  async getPopularPlaces(): Promise<RadioGardenPlace[]> {
    const allPlaces: RadioGardenPlace[] = [];
    
    // Collect all places from all countries
    for (const country of this.countries) {
      allPlaces.push(...country.places);
    }
    
    // Sort by size (number of stations) and return top places
    return allPlaces
      .sort((a, b) => b.size - a.size)
      .slice(0, 50); // Return top 50 places
  }

  async getNearbyPlaces(latitude: number, longitude: number, limit: number = 10): Promise<RadioGardenPlace[]> {
    const userLocation: [number, number] = [latitude, longitude];
    const allPlaces: RadioGardenPlace[] = [];
    
    // Collect all places from all countries
    for (const country of this.countries) {
      allPlaces.push(...country.places);
    }
    
    // Calculate distances and sort by proximity
    const placesWithDistance = allPlaces.map(place => ({
      ...place,
      distance: this.calculateDistance(userLocation, place.geo)
    }));
    
    return placesWithDistance
      .sort((a, b) => a.distance - b.distance)
      .slice(0, limit)
      .map(({ distance, ...place }) => place); // Remove distance property
  }

  // Make getStationsForPlace public (it was private)
  async getStationsForPlace(placeId: string): Promise<RadioGardenStation[]> {
    // First check if we have local data for this place
    for (const country of this.countries) {
      for (const place of country.places) {
        if (place.id === placeId) {
          return place.stations;
        }
      }
    }
    
    // If not found in local data, try to fetch from API
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
      console.warn(`Failed to fetch stations for place ${placeId}:`, error);
      return [];
    }
  }
}

export const radioGardenService = RadioGardenService.getInstance();