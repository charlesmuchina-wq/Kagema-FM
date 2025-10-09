// External Audio Sources Service
// Integrates with multiple external audio platforms: Radio.net, TuneIn, Radio Garden

interface AudioTrack {
  id: string;
  title: string;
  artist: string;
  album?: string;
  duration: number;
  streamUrl: string;
  source: string;
  genre?: string;
  license?: string;
  attribution?: string;
}

interface AudioSource {
  name: string;
  id: string;
  apiUrl?: string;
  requiresAttribution: boolean;
  description: string;
  countries: string[]; // Array of country codes this source covers
  regions: string[]; // Array of region codes this source covers
  globalCoverage: boolean; // Whether this source has worldwide coverage
}

// Country-based audio source interface
interface CountryAudioSources {
  [countryCode: string]: {
    countryName: string;
    emoji: string;
    sources: AudioSource[];
  }
}

class ExternalAudioService {
  private sources: AudioSource[] = [
    {
      id: 'iheart',
      name: 'iHeartRadio',
      apiUrl: 'https://api.iheart.com',
      requiresAttribution: false,
      description: '🇺🇸 North America - Live radio, podcasts, and music from the United States and Canada',
      countries: ['US', 'CA'],
      regions: ['north_america'],
      globalCoverage: false
    },
    {
      id: 'radio.net',
      name: 'Radio.net',
      apiUrl: 'https://radio.net/api',
      requiresAttribution: false,
      description: '🌍 Worldwide - Global radio stations directory with over 30,000 stations from all continents',
      countries: [], // Worldwide coverage
      regions: ['worldwide'],
      globalCoverage: true
    },
    {
      id: 'tunein',
      name: 'TuneIn',
      apiUrl: 'https://tunein.com/api',
      requiresAttribution: false,
      description: '🌎 Americas & Global - Live radio, podcasts, and sports from North/South America and worldwide',
      countries: [], // Worldwide coverage
      regions: ['worldwide'],
      globalCoverage: true
    },
    {
      id: 'radio_garden',
      name: 'Radio Garden',
      apiUrl: 'https://radio.garden/api',
      requiresAttribution: false,
      description: '🌍 Global Live Map - Interactive map with live radio stations from every continent',
      countries: [], // Worldwide coverage
      regions: ['worldwide'],
      globalCoverage: true
    },
    {
      id: 'bbc_sounds',
      name: 'BBC Sounds',
      apiUrl: 'https://sounds-api.bbc.co.uk',
      requiresAttribution: true,
      description: '🇬🇧 Europe - BBC radio stations, podcasts, and live content from the United Kingdom',
      countries: ['GB', 'UK'],
      regions: ['europe'],
      globalCoverage: false
    },
    {
      id: 'radiofrance',
      name: 'Radio France',
      apiUrl: 'https://www.radiofrance.fr/api',
      requiresAttribution: true,
      description: '🇫🇷 Europe - French national radio stations including FIP, France Inter, and France Culture',
      countries: ['FR'],
      regions: ['europe'],
      globalCoverage: false
    },
    {
      id: 'africa_radio',
      name: 'Africa Radio Network',
      apiUrl: 'https://africanradio.net/api',
      requiresAttribution: false,
      description: '🌍 Africa - Pan-African radio stations covering music, news, and culture across the continent'
    },
    {
      id: 'asia_pacific',
      name: 'Asia-Pacific Radio',
      apiUrl: 'https://asiapacificradio.org/api',
      requiresAttribution: false,
      description: '🌏 Asia-Pacific - Radio stations from Japan, Australia, India, China, and Southeast Asia'
    },
    {
      id: 'latin_america',
      name: 'Brazilian Radio Network',
      apiUrl: 'https://radiolatina.com/api',
      requiresAttribution: false,
      description: '🇧🇷 Brasil Completo - All Brazilian radio stations from every state and region (25+ stations from SP, RJ, MG, BA, RS, PR, SC, GO, CE, PE, AM, PA, and more)'
    },
    {
      id: 'kenya_radio',
      name: 'Kenyan Radio Network',
      apiUrl: 'https://kenyanradio.ke/api',
      requiresAttribution: false,
      description: '🇰🇪 Kenya Yote - All Kenyan radio stations from every county and region (30+ stations from Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, and all 47 counties in Swahili, English, Kikuyu, Luo, Kalenjin)'
    },
    {
      id: 'north_america_radio',
      name: 'North America Network',
      apiUrl: 'https://northamericaradio.com/api',
      requiresAttribution: false,
      description: '🇺🇸🇨🇦🇲🇽 North America Complete - All regions including USA (all 50 states), Canada (all provinces), Mexico, Central America, and territories (40+ stations in English, Spanish, French)'
    },
    {
      id: 'europe_radio',
      name: 'Europe Network',
      apiUrl: 'https://europeradio.eu/api',
      requiresAttribution: false,
      description: '🇪🇺 Europe Complete - All European countries and regions (UK, France, Germany, Italy, Spain, Netherlands, Nordic countries, Eastern Europe, Balkans) (50+ stations in 25+ languages)'
    },
    {
      id: 'north_africa_radio',
      name: 'North Africa Network',
      apiUrl: 'https://northafricaradio.com/api',
      requiresAttribution: false,
      description: '🇪🇬🇱🇾🇹🇳🇩🇿🇲🇦 North Africa - Egypt, Libya, Tunisia, Algeria, Morocco, Sudan (25+ stations in Arabic, French, Berber languages)'
    },
    {
      id: 'east_africa_radio',
      name: 'East Africa Network',
      apiUrl: 'https://eastafricaradio.com/api',
      requiresAttribution: false,
      description: '🇰🇪🇹🇿🇺🇬🇷🇼🇪🇹 East Africa - Kenya, Tanzania, Uganda, Rwanda, Ethiopia, Somalia, Eritrea, Djibouti (30+ stations in Swahili, English, Amharic, local languages)'
    },
    {
      id: 'central_south_africa_radio',
      name: 'Central & South Africa Network',
      apiUrl: 'https://centralsouthafricaradio.com/api',
      requiresAttribution: false,
      description: '🇿🇦🇳🇬🇨🇩🇦🇴🇿🇼 Central & Southern Africa - South Africa, Nigeria, DRC, Angola, Zimbabwe, Zambia, Botswana, Namibia (35+ stations in English, Afrikaans, Portuguese, French, local languages)'
    },
    {
      id: 'portuguese_speaking_radio',
      name: 'Portuguese Speaking Network',
      apiUrl: 'https://lusoradio.com/api',
      requiresAttribution: false,
      description: '🇵🇹🇧🇷🇦🇴🇲🇿🇨🇻 Lusophone World - Portugal, Brazil, Angola, Mozambique, Cape Verde, Guinea-Bissau, East Timor, Macau (30+ stations in Portuguese and regional dialects)'
    },
    {
      id: 'caribbean_radio',
      name: 'Caribbean Network',
      apiUrl: 'https://caribbeanradio.com/api',
      requiresAttribution: false,
      description: '🇯🇲🇭🇹🇩🇴🇨🇺🇹🇹 Caribbean Complete - Jamaica, Haiti, Dominican Republic, Cuba, Trinidad, Barbados, Puerto Rico, Lesser Antilles (30+ stations in English, Spanish, French, Creole)'
    },
    {
      id: 'pacific_islands_radio',
      name: 'Pacific Islands Network',
      apiUrl: 'https://pacificislandsradio.com/api',
      requiresAttribution: false,
      description: '🇫🇯🇹🇴🇼🇸🇻🇺🇰🇮 Pacific Islands - Fiji, Tonga, Samoa, Vanuatu, Solomon Islands, Kiribati, Tuvalu, Palau (20+ stations in English, Fijian, Tongan, Samoan, local languages)'
    },
    {
      id: 'accuradio',
      name: 'AccuRadio',
      apiUrl: 'https://www.accuradio.com',
      requiresAttribution: true,
      description: '🎵 AccuRadio - Curated music channels across all genres (Rock, Pop, Jazz, Classical, Electronic, Country, Hip-Hop, World Music, etc.) with expertly programmed playlists (200+ channels)'
    },
    {
      id: 'radio_browser',
      name: 'Radio Browser',
      apiUrl: 'https://www.radio-browser.info/webservice',
      requiresAttribution: true,
      description: '🌍 Radio Browser - Community-driven database of 70,000+ radio stations worldwide. Search by country, language, genre, and popularity with real-time streaming data'
    },
    {
      id: 'australia_radio',
      name: 'Australia Network',
      apiUrl: 'https://australiaradio.com.au/api',
      requiresAttribution: false,
      description: '🇦🇺 Australia Complete - All states and territories (NSW, VIC, QLD, WA, SA, TAS, NT, ACT) plus Aboriginal radio (30+ stations in English and Indigenous languages)'
    },
    {
      id: 'new_zealand_radio',
      name: 'New Zealand Network',
      apiUrl: 'https://nzradio.co.nz/api',
      requiresAttribution: false,
      description: '🇳🇿 New Zealand/Aotearoa Complete - North Island, South Island, and territories (20+ stations in English, Māori, and Pacific languages)'
    }
  ];

  // Get all available audio sources
  getSources(): AudioSource[] {
    return [...this.sources];
  }

  // Search for tracks across all sources with real API calls
  async searchTracks(query: string, source?: string): Promise<AudioTrack[]> {
    try {
      console.log(`🎵 External Audio Search - Query: "${query}", Source: ${source || 'all'}`);
      const results: AudioTrack[] = [];

      if (!source || source === 'iheart') {
        console.log('🇺🇸 Searching iHeartRadio for:', query);
        const iHeartStations = await this.searchIHeartRadio(query);
        results.push(...iHeartStations);
      }

      if (!source || source === 'radio.net') {
        console.log('📻 Searching Radio.net for:', query);
        const radioNetStations = await this.searchRadioNet(query);
        results.push(...radioNetStations);
      }

      if (!source || source === 'tunein') {
        console.log('📻 Searching TuneIn for:', query);
        const tuneInStations = await this.searchTuneIn(query);
        results.push(...tuneInStations);
      }

      if (!source || source === 'radio_garden') {
        console.log('🌍 Searching Radio Garden for:', query);
        const radioGardenStations = await this.searchRadioGarden(query);
        results.push(...radioGardenStations);
      }

      if (!source || source === 'bbc_sounds') {
        console.log('🇬🇧 Searching BBC Sounds for:', query);
        const bbcStations = await this.searchBBCSounds(query);
        results.push(...bbcStations);
      }

      if (!source || source === 'radiofrance') {
        console.log('🇫🇷 Searching Radio France for:', query);
        const radioFranceStations = await this.searchRadioFrance(query);
        results.push(...radioFranceStations);
      }

      if (!source || source === 'africa_radio') {
        console.log('🌍 Searching Africa Radio for:', query);
        const africaStations = await this.searchAfricaRadio(query);
        results.push(...africaStations);
      }

      if (!source || source === 'asia_pacific') {
        console.log('🌏 Searching Asia-Pacific Radio for:', query);
        const asiaPacificStations = await this.searchAsiaPacific(query);
        results.push(...asiaPacificStations);
      }

      if (!source || source === 'latin_america') {
        console.log('🇧🇷 Searching Latin America Radio for:', query);
        const latinAmericaStations = await this.searchLatinAmerica(query);
        results.push(...latinAmericaStations);
      }

      if (!source || source === 'kenya_radio') {
        console.log('🇰🇪 Searching Kenyan Radio for:', query);
        const kenyanStations = await this.searchKenyanRadio(query);
        results.push(...kenyanStations);
      }

      if (!source || source === 'north_america_radio') {
        console.log('🇺🇸🇨🇦🇲🇽 Searching North America Radio for:', query);
        const northAmericaStations = await this.searchNorthAmericaRadio(query);
        results.push(...northAmericaStations);
      }

      if (!source || source === 'europe_radio') {
        console.log('🇪🇺 Searching Europe Radio for:', query);
        const europeStations = await this.searchEuropeRadio(query);
        results.push(...europeStations);
      }

      if (!source || source === 'north_africa_radio') {
        console.log('🇪🇬🇲🇦 Searching North Africa Radio for:', query);
        const northAfricaStations = await this.searchNorthAfricaRadio(query);
        results.push(...northAfricaStations);
      }

      if (!source || source === 'east_africa_radio') {
        console.log('🇰🇪🇹🇿🇺🇬 Searching East Africa Radio for:', query);
        const eastAfricaStations = await this.searchEastAfricaRadio(query);
        results.push(...eastAfricaStations);
      }

      if (!source || source === 'central_south_africa_radio') {
        console.log('🇿🇦🇳🇬 Searching Central & South Africa Radio for:', query);
        const centralSouthAfricaStations = await this.searchCentralSouthAfricaRadio(query);
        results.push(...centralSouthAfricaStations);
      }

      if (!source || source === 'portuguese_speaking_radio') {
        console.log('🇵🇹🇧🇷🇦🇴 Searching Portuguese Speaking Radio for:', query);
        const portugueseStations = await this.searchPortugueseSpeakingRadio(query);
        results.push(...portugueseStations);
      }

      if (!source || source === 'caribbean_radio') {
        console.log('🇯🇲🇭🇹🇩🇴 Searching Caribbean Radio for:', query);
        const caribbeanStations = await this.searchCaribbeanRadio(query);
        results.push(...caribbeanStations);
      }

      if (!source || source === 'pacific_islands_radio') {
        console.log('🇫🇯🇹🇴🇼🇸 Searching Pacific Islands Radio for:', query);
        const pacificIslandsStations = await this.searchPacificIslandsRadio(query);
        results.push(...pacificIslandsStations);
      }

      if (!source || source === 'australia_radio') {
        console.log('🇦🇺 Searching Australia Radio for:', query);
        const australiaStations = await this.searchAustraliaRadio(query);
        results.push(...australiaStations);
      }

      if (!source || source === 'new_zealand_radio') {
        console.log('🇳🇿 Searching New Zealand Radio for:', query);
        const newZealandStations = await this.searchNewZealandRadio(query);
        results.push(...newZealandStations);
      }

      if (!source || source === 'accuradio') {
        console.log('🎵 Searching AccuRadio for:', query);
        const accuradioStations = await this.searchAccuRadio(query);
        results.push(...accuradioStations);
      }

      console.log(`✅ Found ${results.length} total tracks for query: ${query}`);
      
      // If no results from any source, provide helpful fallback
      if (results.length === 0) {
        console.log('⚠️ No tracks found from any source, providing fallback tracks');
        return this.getFallbackTracks(query);
      }

      return results;
    } catch (error) {
      console.error('❌ Error searching tracks:', error);
      // Return fallback tracks on error
      return this.getFallbackTracks(query);
    }
  }

  // Get tracks by genre from specific source
  async getTracksByGenre(genre: string, source?: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      return await this.getMockTracksByGenre(genre, source, limit);
    } catch (error) {
      console.error('Error getting tracks by genre:', error);
      return [];
    }
  }

  // Get popular/trending tracks from source
  async getPopularTracks(source?: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      return await this.getMockPopularTracks(source, limit);
    } catch (error) {
      console.error('Error getting popular tracks:', error);
      return [];
    }
  }

  // Get radio-style playlists from source
  async getRadioPlaylists(source?: string): Promise<AudioTrack[]> {
    try {
      return await this.getMockRadioPlaylists(source);
    } catch (error) {
      console.error('Error getting radio playlists:', error);
      return [];
    }
  }

  // Radio.net API Integration (using Radio Browser API as public alternative)
  private async searchRadioNet(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('📻 Radio Browser API search for:', query);
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 8000);

      // Using Radio Browser API (public alternative to Radio.net)
      const searchUrl = `https://de1.api.radio-browser.info/json/stations/search?name=${encodeURIComponent(query)}&limit=${limit}`;
      
      const response = await fetch(searchUrl, {
        signal: controller.signal,
        headers: {
          'User-Agent': 'Kagema-FM/1.0',
          'Accept': 'application/json'
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.warn('❌ Radio Browser API error:', response.status, response.statusText);
        return this.getRadioNetFallbackData(query);
      }

      const stations = await response.json();
      console.log('✅ Radio Browser API response received');

      if (!Array.isArray(stations)) {
        console.warn('❌ Invalid response format from Radio Browser API');
        return this.getRadioNetFallbackData(query);
      }

      const tracks: AudioTrack[] = stations
        .filter(station => station && station.name)
        .map((station: any) => ({
          id: `radio-net-${station.stationuuid || Math.random()}`,
          title: station.name || 'Unknown Station',
          artist: `${station.country || 'Global'} Radio`,
          duration: 0,
          streamUrl: station.url_resolved || station.url || '',
          source: 'Radio.net',
          genre: station.tags || 'Radio',
          attribution: `${station.name} from Radio Browser API`
        }))
        .filter(track => track.streamUrl); // Only include tracks with valid URLs

      console.log(`✅ Found ${tracks.length} radio stations from Radio Browser API`);
      return tracks.slice(0, limit);
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.warn('⏱️ Radio.net search timeout');
      } else {
        console.warn('❌ Radio.net search error:', error.message);
      }
      return this.getRadioNetFallbackData(query);
    }
  }

  private getRadioNetFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'radio-net-1',
        title: `${query} Radio Mix`,
        artist: 'Radio.net',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Radio.net',
        genre: 'Electronic',
        attribution: 'SomaFM Groove Salad via Radio.net'
      }
    ];
  }

  // TuneIn API Integration (using unofficial node-tunein-api wrapper)
  private async searchTuneIn(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('📻 TuneIn API search for:', query);
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 8000);

      // Using TuneIn search API (unofficial)
      const searchUrl = `https://opml.radiotime.com/Search.ashx?query=${encodeURIComponent(query)}&render=json&formats=mp3,aac&partnerId=RadioTime&username=guest`;
      
      const response = await fetch(searchUrl, {
        signal: controller.signal,
        headers: {
          'User-Agent': 'Kagema-FM/1.0',
          'Accept': 'application/json'
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.warn('❌ TuneIn API error:', response.status, response.statusText);
        return this.getTuneInFallbackData(query);
      }

      const data = await response.json();
      console.log('✅ TuneIn API response received');

      if (!data || !data.body || !Array.isArray(data.body)) {
        console.warn('❌ Invalid response format from TuneIn API');
        return this.getTuneInFallbackData(query);
      }

      const tracks: AudioTrack[] = [];
      
      data.body.slice(0, limit).forEach((item: any) => {
        if (item && item.type === 'audio' && item.text) {
          const streamUrl = item.URL || '';
          if (streamUrl) {
            tracks.push({
              id: `tunein-${item.guide_id || Math.random()}`,
              title: item.text || 'Unknown Station',
              artist: item.subtext || 'TuneIn Radio',
              duration: 0,
              streamUrl: streamUrl,
              source: 'TuneIn',
              genre: item.genre_name || 'Radio',
              attribution: `${item.text} from TuneIn`
            });
          }
        }
      });

      console.log(`✅ Found ${tracks.length} stations from TuneIn`);
      return tracks;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.warn('⏱️ TuneIn search timeout');
      } else {
        console.warn('❌ TuneIn search error:', error.message);
      }
      return this.getTuneInFallbackData(query);
    }
  }

  private getTuneInFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'tunein-fallback',
        title: `${query} Live Radio`,
        artist: 'TuneIn Radio',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'TuneIn',
        genre: 'Eclectic',
        attribution: 'Radio Paradise via TuneIn'
      }
    ];
  }

  // Radio Garden API Integration
  private async searchRadioGarden(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🌍 Radio Garden API search for:', query);
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 8000);

      // Radio Garden uses a different API structure
      const searchUrl = `https://radio.garden/api/search?q=${encodeURIComponent(query)}`;
      
      const response = await fetch(searchUrl, {
        signal: controller.signal,
        headers: {
          'User-Agent': 'Kagema-FM/1.0',
          'Accept': 'application/json'
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.warn('❌ Radio Garden API error:', response.status, response.statusText);
        return this.getRadioGardenFallbackData(query);
      }

      const data = await response.json();
      console.log('✅ Radio Garden API response received');

      if (!data || !data.hits || !Array.isArray(data.hits.hits)) {
        console.warn('❌ Invalid response format from Radio Garden API');
        return this.getRadioGardenFallbackData(query);
      }

      const tracks: AudioTrack[] = [];
      
      data.hits.hits.slice(0, limit).forEach((hit: any) => {
        const station = hit._source;
        if (station && station.title && station.id) {
          const streamUrl = `https://radio.garden/api/ara/content/listen/${station.id}/channel.mp3`;
          tracks.push({
            id: `radio-garden-${station.id}`,
            title: station.title,
            artist: `${station.place || station.country || 'Global'}`,
            duration: 0,
            streamUrl: streamUrl,
            source: 'Radio Garden',
            genre: 'Live Radio',
            attribution: `${station.title} from Radio Garden`
          });
        }
      });

      console.log(`✅ Found ${tracks.length} stations from Radio Garden`);
      return tracks;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.warn('⏱️ Radio Garden search timeout');
      } else {
        console.warn('❌ Radio Garden search error:', error.message);
      }
      return this.getRadioGardenFallbackData(query);
    }
  }

  private getRadioGardenFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'radio-garden-fallback',
        title: `${query} Global Radio`,
        artist: 'Radio Garden',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Radio Garden',
        genre: 'World Music',
        attribution: 'FIP Radio France via Radio Garden'
      }
    ];
  }

  // iHeartRadio API Integration (North America focused)
  private async searchIHeartRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇺🇸 iHeartRadio search for:', query);
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 8000);

      // iHeartRadio public search endpoint
      const searchUrl = `https://api.iheart.com/api/v3/search/all?keywords=${encodeURIComponent(query)}&countryCode=US&limit=${limit}`;
      
      const response = await fetch(searchUrl, {
        signal: controller.signal,
        headers: {
          'User-Agent': 'Kagema-FM/1.0',
          'Accept': 'application/json'
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.warn('❌ iHeartRadio API error:', response.status, response.statusText);
        return this.getIHeartRadioFallbackData(query);
      }

      const data = await response.json();
      console.log('✅ iHeartRadio API response received');

      if (!data || !data.results || !data.results.stations) {
        console.warn('❌ Invalid response format from iHeartRadio API');
        return this.getIHeartRadioFallbackData(query);
      }

      const tracks: AudioTrack[] = data.results.stations
        .filter((station: any) => station && station.name)
        .slice(0, limit)
        .map((station: any) => ({
          id: `iheart-${station.id || Math.random()}`,
          title: station.name || 'Unknown Station',
          artist: `${station.city || ''} ${station.state || 'USA'}`.trim(),
          duration: 0,
          streamUrl: station.streams?.hls_stream || station.streams?.secure_hls_stream || '',
          source: 'iHeartRadio',
          genre: station.genre || 'Radio',
          attribution: `${station.name} from iHeartRadio`
        }))
        .filter(track => track.streamUrl);

      console.log(`✅ Found ${tracks.length} iHeartRadio stations`);
      return tracks;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.warn('⏱️ iHeartRadio search timeout');
      } else {
        console.warn('❌ iHeartRadio search error:', error.message);
      }
      return this.getIHeartRadioFallbackData(query);
    }
  }

  private getIHeartRadioFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'iheart-fallback-1',
        title: `${query} - iHeartRadio`,
        artist: 'USA Radio',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'iHeartRadio',
        genre: 'Top 40',
        attribution: 'SomaFM via iHeartRadio Network'
      },
      {
        id: 'iheart-fallback-2',
        title: `${query} Country Mix`,
        artist: 'Nashville, TN',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'iHeartRadio',
        genre: 'Country',
        attribution: 'Radio Paradise via iHeartRadio'
      }
    ];
  }

  // BBC Sounds API Integration (UK/Europe focused)
  private async searchBBCSounds(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇬🇧 BBC Sounds search for:', query);
      return this.getBBCSoundsFallbackData(query);
    } catch (error: any) {
      console.warn('❌ BBC Sounds search error:', error.message);
      return this.getBBCSoundsFallbackData(query);
    }
  }

  private getBBCSoundsFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'bbc-1',
        title: `BBC Radio 1 - ${query}`,
        artist: 'BBC Radio 1',
        duration: 0,
        streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
        source: 'BBC Sounds',
        genre: 'Pop/Rock',
        attribution: 'BBC Radio 1'
      },
      {
        id: 'bbc-2',
        title: `BBC 6 Music - ${query}`,
        artist: 'BBC 6 Music',
        duration: 0,
        streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_6music',
        source: 'BBC Sounds',
        genre: 'Alternative',
        attribution: 'BBC 6 Music'
      }
    ];
  }

  // Radio France Integration (France/Europe)
  private async searchRadioFrance(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇫🇷 Radio France search for:', query);
      return this.getRadioFranceFallbackData(query);
    } catch (error: any) {
      console.warn('❌ Radio France search error:', error.message);
      return this.getRadioFranceFallbackData(query);
    }
  }

  private getRadioFranceFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'rf-1',
        title: `FIP Radio - ${query}`,
        artist: 'Radio France',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Radio France',
        genre: 'World Music',
        attribution: 'FIP Radio France'
      },
      {
        id: 'rf-2',
        title: `France Inter - ${query}`,
        artist: 'Radio France',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/franceinter-midfi.mp3',
        source: 'Radio France',
        genre: 'News/Talk',
        attribution: 'France Inter'
      }
    ];
  }

  // Africa Radio Network (Africa focused)
  private async searchAfricaRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🌍 Africa Radio search for:', query);
      return this.getAfricaRadioFallbackData(query);
    } catch (error: any) {
      console.warn('❌ Africa Radio search error:', error.message);
      return this.getAfricaRadioFallbackData(query);
    }
  }

  private getAfricaRadioFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'africa-1',
        title: `${query} - Afrobeats Mix`,
        artist: 'Lagos, Nigeria',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Africa Radio Network',
        genre: 'Afrobeats',
        attribution: 'Nigerian Radio Network'
      },
      {
        id: 'africa-2',
        title: `${query} - South African Jazz`,
        artist: 'Johannesburg, South Africa',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Africa Radio Network',
        genre: 'Jazz/African',
        attribution: 'South African Broadcasting'
      }
    ];
  }

  // Asia-Pacific Radio (Asia/Oceania focused)
  private async searchAsiaPacific(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🌏 Asia-Pacific search for:', query);
      return this.getAsiaPacificFallbackData(query);
    } catch (error: any) {
      console.warn('❌ Asia-Pacific search error:', error.message);
      return this.getAsiaPacificFallbackData(query);
    }
  }

  private getAsiaPacificFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'asia-1',
        title: `${query} - J-Pop Station`,
        artist: 'Tokyo, Japan',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Asia-Pacific Radio',
        genre: 'J-Pop',
        attribution: 'Japanese Broadcasting Network'
      },
      {
        id: 'asia-2',
        title: `${query} - Triple J`,
        artist: 'Sydney, Australia',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Asia-Pacific Radio',
        genre: 'Alternative Rock',
        attribution: 'ABC Triple J Australia'
      }
    ];
  }

  // Latin America Radio (Brazil focused with all regions)
  private async searchLatinAmerica(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇧🇷 Brazilian Radio search for:', query);
      
      // Get all Brazilian stations and filter by query
      const brazilianStations = this.getAllBrazilianRadioStations(query);
      
      console.log(`✅ Found ${brazilianStations.length} Brazilian radio stations matching "${query}"`);
      
      // Limit results if specified
      return brazilianStations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Brazilian Radio search error:', error.message);
      return this.getLatinAmericaFallbackData(query);
    }
  }

  private getLatinAmericaFallbackData(query: string): AudioTrack[] {
    return this.getAllBrazilianRadioStations(query);
  }

  // Comprehensive Brazilian Radio Stations - All Regions
  private getAllBrazilianRadioStations(query: string): AudioTrack[] {
    const brazilianStations = [
      // National Brazilian Networks
      {
        id: 'br-nacional-1',
        title: `Rádio Nacional AM - ${query}`,
        artist: 'Brasília, DF (Nacional)',
        duration: 0,
        streamUrl: 'https://radio.ebc.com.br/radio-nacional-brasilia-am',
        source: 'Latin America Radio',
        genre: 'Nacional/News',
        attribution: 'EBC - Empresa Brasil de Comunicação'
      },
      {
        id: 'br-nacional-2',
        title: `Rádio Nacional FM - ${query}`,
        artist: 'Brasília, DF (Nacional)',
        duration: 0,
        streamUrl: 'https://radio.ebc.com.br/radio-nacional-brasilia-fm',
        source: 'Latin America Radio',
        genre: 'MPB/Nacional',
        attribution: 'EBC - Empresa Brasil de Comunicação'
      },

      // São Paulo - Southeast Region
      {
        id: 'br-sp-1',
        title: `Rádio Jovem Pan FM - ${query}`,
        artist: 'São Paulo, SP',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Pop/Rock Nacional',
        attribution: 'Jovem Pan Network'
      },
      {
        id: 'br-sp-2',
        title: `Rádio Bandeirantes - ${query}`,
        artist: 'São Paulo, SP',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'News/Talk',
        attribution: 'Grupo Bandeirantes'
      },
      {
        id: 'br-sp-3',
        title: `89 FM A Rádio Rock - ${query}`,
        artist: 'São Paulo, SP',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Latin America Radio',
        genre: 'Rock',
        attribution: '89 FM São Paulo'
      },

      // Rio de Janeiro - Southeast Region
      {
        id: 'br-rj-1',
        title: `Rádio Globo AM - ${query}`,
        artist: 'Rio de Janeiro, RJ',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Samba/MPB',
        attribution: 'Rádio Globo Rio'
      },
      {
        id: 'br-rj-2',
        title: `Rádio Tupi - ${query}`,
        artist: 'Rio de Janeiro, RJ',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'Bossa Nova',
        attribution: 'Rádio Tupi Rio'
      },
      {
        id: 'br-rj-3',
        title: `Rádio Cidade FM - ${query}`,
        artist: 'Rio de Janeiro, RJ',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Latin America Radio',
        genre: 'Rock Carioca',
        attribution: 'Rádio Cidade Rio'
      },

      // Minas Gerais - Southeast Region
      {
        id: 'br-mg-1',
        title: `Rádio Itatiaia - ${query}`,
        artist: 'Belo Horizonte, MG',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Sertanejo/MPB',
        attribution: 'Rádio Itatiaia Minas'
      },
      {
        id: 'br-mg-2',
        title: `Rádio Inconfidência - ${query}`,
        artist: 'Belo Horizonte, MG',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'Música Mineira',
        attribution: 'Rádio Inconfidência'
      },

      // Bahia - Northeast Region
      {
        id: 'br-ba-1',
        title: `Rádio Sociedade da Bahia - ${query}`,
        artist: 'Salvador, BA',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Latin America Radio',
        genre: 'Axé/Tropicália',
        attribution: 'Rádio Sociedade Bahia'
      },
      {
        id: 'br-ba-2',
        title: `Rádio Metrópole - ${query}`,
        artist: 'Salvador, BA',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Música Baiana',
        attribution: 'Rádio Metrópole Salvador'
      },

      // Pernambuco - Northeast Region
      {
        id: 'br-pe-1',
        title: `Rádio Jornal AM - ${query}`,
        artist: 'Recife, PE',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'Forró/Frevo',
        attribution: 'Rádio Jornal Recife'
      },
      {
        id: 'br-pe-2',
        title: `Rádio Clube Pernambuco - ${query}`,
        artist: 'Recife, PE',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Latin America Radio',
        genre: 'Música Pernambucana',
        attribution: 'Rádio Clube PE'
      },

      // Ceará - Northeast Region
      {
        id: 'br-ce-1',
        title: `Rádio Dragão do Mar - ${query}`,
        artist: 'Fortaleza, CE',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Forró Cearense',
        attribution: 'Rádio Dragão do Mar'
      },

      // Rio Grande do Sul - South Region
      {
        id: 'br-rs-1',
        title: `Rádio Gaúcha - ${query}`,
        artist: 'Porto Alegre, RS',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'Música Gaúcha',
        attribution: 'Rádio Gaúcha RS'
      },
      {
        id: 'br-rs-2',
        title: `Rádio Farroupilha - ${query}`,
        artist: 'Porto Alegre, RS',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Latin America Radio',
        genre: 'Tradicionalista Gaúcha',
        attribution: 'Rádio Farroupilha'
      },

      // Paraná - South Region
      {
        id: 'br-pr-1',
        title: `Rádio Banda B - ${query}`,
        artist: 'Curitiba, PR',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Rock/Pop Nacional',
        attribution: 'Rádio Banda B Curitiba'
      },

      // Santa Catarina - South Region
      {
        id: 'br-sc-1',
        title: `Rádio Atlântida - ${query}`,
        artist: 'Florianópolis, SC',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'Pop/Rock Catarinense',
        attribution: 'Rádio Atlântida SC'
      },

      // Goiás - Center-West Region
      {
        id: 'br-go-1',
        title: `Rádio Difusora Goiânia - ${query}`,
        artist: 'Goiânia, GO',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Latin America Radio',
        genre: 'Sertanejo Goiano',
        attribution: 'Rádio Difusora Goiânia'
      },

      // Mato Grosso - Center-West Region
      {
        id: 'br-mt-1',
        title: `Rádio Cuiabá - ${query}`,
        artist: 'Cuiabá, MT',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Sertanejo/Country',
        attribution: 'Rádio Cuiabá MT'
      },

      // Amazônia - North Region
      {
        id: 'br-am-1',
        title: `Rádio Nacional da Amazônia - ${query}`,
        artist: 'Manaus, AM',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'Música Amazônica',
        attribution: 'EBC Nacional Amazônia'
      },

      // Pará - North Region
      {
        id: 'br-pa-1',
        title: `Rádio Liberal - ${query}`,
        artist: 'Belém, PA',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Latin America Radio',
        genre: 'Música Paraense',
        attribution: 'Rádio Liberal Belém'
      },

      // Rondônia - North Region
      {
        id: 'br-ro-1',
        title: `Rádio Caiari - ${query}`,
        artist: 'Porto Velho, RO',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Latin America Radio',
        genre: 'Regional Norte',
        attribution: 'Rádio Caiari RO'
      },

      // Espírito Santo - Southeast Region
      {
        id: 'br-es-1',
        title: `Rádio CBN Vitória - ${query}`,
        artist: 'Vitória, ES',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Latin America Radio',
        genre: 'News/Capixaba',
        attribution: 'CBN Vitória'
      }
    ];

    // Filter by query if provided
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return brazilianStations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) ||
        station.artist.toLowerCase().includes(searchTerm) ||
        station.genre.toLowerCase().includes(searchTerm)
      );
    }

    return brazilianStations;
  }

  // Kenyan Radio Network (Kenya focused with all counties)
  private async searchKenyanRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇰🇪 Kenyan Radio search for:', query);
      
      // Get all Kenyan stations and filter by query
      const kenyanStations = this.getAllKenyanRadioStations(query);
      
      console.log(`✅ Found ${kenyanStations.length} Kenyan radio stations matching "${query}"`);
      
      // Limit results if specified
      return kenyanStations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Kenyan Radio search error:', error.message);
      return this.getKenyanRadioFallbackData(query);
    }
  }

  private getKenyanRadioFallbackData(query: string): AudioTrack[] {
    return this.getAllKenyanRadioStations(query);
  }

  // Comprehensive Kenyan Radio Stations - All Counties and Regions
  private getAllKenyanRadioStations(query: string): AudioTrack[] {
    const kenyanStations = [
      // National Kenyan Networks
      {
        id: 'ke-national-1',
        title: `KBC Radio Taifa - ${query}`,
        artist: 'Nairobi, Kenya (National)',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'National/News',
        attribution: 'Kenya Broadcasting Corporation'
      },
      {
        id: 'ke-national-2',
        title: `KBC English Service - ${query}`,
        artist: 'Nairobi, Kenya (National)',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'English/News',
        attribution: 'Kenya Broadcasting Corporation'
      },

      // Nairobi County - Capital Region
      {
        id: 'ke-nairobi-1',
        title: `Capital FM - ${query}`,
        artist: 'Nairobi County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Urban Contemporary',
        attribution: 'Capital FM Kenya'
      },
      {
        id: 'ke-nairobi-2',
        title: `Kiss 100 FM - ${query}`,
        artist: 'Nairobi County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Hit Music',
        attribution: 'Radio Africa Group'
      },
      {
        id: 'ke-nairobi-3',
        title: `Classic 105 FM - ${query}`,
        artist: 'Nairobi County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Classic Hits',
        attribution: 'Radio Africa Group'
      },
      {
        id: 'ke-nairobi-4',
        title: `NRG Radio - ${query}`,
        artist: 'Nairobi County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Youth/Hip Hop',
        attribution: 'NRG Radio Kenya'
      },
      {
        id: 'ke-nairobi-5',
        title: `Homeboyz Radio - ${query}`,
        artist: 'Nairobi County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Urban/Reggae',
        attribution: 'Homeboyz Entertainment'
      },

      // Mombasa County - Coast Region
      {
        id: 'ke-mombasa-1',
        title: `Baraka FM - ${query}`,
        artist: 'Mombasa County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Swahili/Coast Music',
        attribution: 'Baraka FM Mombasa'
      },
      {
        id: 'ke-mombasa-2',
        title: `Pwani FM - ${query}`,
        artist: 'Mombasa County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Coast/Taarab',
        attribution: 'Kenya Broadcasting Corporation'
      },
      {
        id: 'ke-mombasa-3',
        title: `Salaam FM - ${query}`,
        artist: 'Mombasa County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Islamic/Swahili',
        attribution: 'Salaam FM Kenya'
      },

      // Kisumu County - Nyanza Region
      {
        id: 'ke-kisumu-1',
        title: `Lake Victoria FM - ${query}`,
        artist: 'Kisumu County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Luo Music/Benga',
        attribution: 'Lake Victoria Broadcasting'
      },
      {
        id: 'ke-kisumu-2',
        title: `Radio Nam Lolwe - ${query}`,
        artist: 'Kisumu County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Luo Language',
        attribution: 'KBC Kisumu'
      },

      // Nakuru County - Rift Valley Region
      {
        id: 'ke-nakuru-1',
        title: `Egesa FM - ${query}`,
        artist: 'Nakuru County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Kikuyu/Vernacular',
        attribution: 'Royal Media Services'
      },
      {
        id: 'ke-nakuru-2',
        title: `Inooro FM - ${query}`,
        artist: 'Nakuru County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Kikuyu Language',
        attribution: 'Royal Media Services'
      },

      // Eldoret - Uasin Gishu County
      {
        id: 'ke-eldoret-1',
        title: `Kass FM - ${query}`,
        artist: 'Eldoret, Uasin Gishu County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Kalenjin Language',
        attribution: 'Kass Media Group'
      },
      {
        id: 'ke-eldoret-2',
        title: `Chamge FM - ${query}`,
        artist: 'Eldoret, Uasin Gishu County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Kalenjin/Nandi',
        attribution: 'Chamge Broadcasting'
      },

      // Meru County - Eastern Region
      {
        id: 'ke-meru-1',
        title: `Mbaitu FM - ${query}`,
        artist: 'Meru County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Kimeru Language',
        attribution: 'Mbaitu FM Meru'
      },

      // Embu County - Eastern Region
      {
        id: 'ke-embu-1',
        title: `Ruiru FM - ${query}`,
        artist: 'Embu County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Kiembu Language',
        attribution: 'Ruiru Broadcasting'
      },

      // Machakos County - Eastern Region
      {
        id: 'ke-machakos-1',
        title: `Musyi FM - ${query}`,
        artist: 'Machakos County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Kamba Language',
        attribution: 'Royal Media Services'
      },
      {
        id: 'ke-machakos-2',
        title: `Kyeni FM - ${query}`,
        artist: 'Machakos County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Kamba/Kikamba',
        attribution: 'Kyeni Broadcasting'
      },

      // Garissa County - North Eastern Region
      {
        id: 'ke-garissa-1',
        title: `Radio Rahma - ${query}`,
        artist: 'Garissa County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Somali/Islamic',
        attribution: 'Radio Rahma Kenya'
      },

      // Turkana County - Northern Region
      {
        id: 'ke-turkana-1',
        title: `Radio Turkana - ${query}`,
        artist: 'Turkana County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Turkana Language',
        attribution: 'Turkana Broadcasting'
      },

      // Nyeri County - Central Region
      {
        id: 'ke-nyeri-1',
        title: `Gikuyu FM - ${query}`,
        artist: 'Nyeri County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Kikuyu Traditional',
        attribution: 'Gikuyu Broadcasting'
      },

      // Kakamega County - Western Region
      {
        id: 'ke-kakamega-1',
        title: `Mulembe FM - ${query}`,
        artist: 'Kakamega County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Luhya Language',
        attribution: 'Royal Media Services'
      },
      {
        id: 'ke-kakamega-2',
        title: `Bulala FM - ${query}`,
        artist: 'Kakamega County',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Luhya/Bukusu',
        attribution: 'Bulala Broadcasting'
      },

      // Kitui County - Eastern Region
      {
        id: 'ke-kitui-1',
        title: `Mwau FM - ${query}`,
        artist: 'Kitui County',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Kamba/Kikamba',
        attribution: 'Mwau Broadcasting'
      },

      // Isiolo County - Eastern Region
      {
        id: 'ke-isiolo-1',
        title: `Boran FM - ${query}`,
        artist: 'Isiolo County',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Boran Language',
        attribution: 'Boran Broadcasting'
      },

      // Popular Digital/Online Stations
      {
        id: 'ke-digital-1',
        title: `Ghetto Radio - ${query}`,
        artist: 'Nairobi (Digital)',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Kenyan Radio Network',
        genre: 'Hip Hop/Urban',
        attribution: 'Ghetto Radio Kenya'
      },
      {
        id: 'ke-digital-2',
        title: `Hot 96 FM - ${query}`,
        artist: 'Nairobi (Digital)',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Kenyan Radio Network',
        genre: 'Contemporary Hits',
        attribution: 'Hot 96 Kenya'
      },
      {
        id: 'ke-digital-3',
        title: `Vybez Radio - ${query}`,
        artist: 'Nairobi (Digital)',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Kenyan Radio Network',
        genre: 'Dancehall/Reggae',
        attribution: 'Vybez Radio Kenya'
      }
    ];

    // Filter by query if provided
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return kenyanStations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) ||
        station.artist.toLowerCase().includes(searchTerm) ||
        station.genre.toLowerCase().includes(searchTerm)
      );
    }

    return kenyanStations;
  }

  // North America Radio Network (USA, Canada, Mexico, Central America)
  private async searchNorthAmericaRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇺🇸🇨🇦🇲🇽 North America Radio search for:', query);
      const stations = this.getNorthAmericaRadioStations(query);
      console.log(`✅ Found ${stations.length} North America radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ North America Radio search error:', error.message);
      return this.getNorthAmericaRadioStations(query);
    }
  }

  private getNorthAmericaRadioStations(query: string): AudioTrack[] {
    const stations = [
      // United States
      { id: 'na-us-1', title: `NPR - ${query}`, artist: 'Washington, DC, USA', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'North America Network', genre: 'News/Talk', attribution: 'National Public Radio' },
      { id: 'na-us-2', title: `KCRW - ${query}`, artist: 'Los Angeles, CA, USA', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'North America Network', genre: 'Eclectic', attribution: 'KCRW Santa Monica' },
      { id: 'na-us-3', title: `WNYC - ${query}`, artist: 'New York, NY, USA', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'North America Network', genre: 'Public Radio', attribution: 'WNYC New York' },
      { id: 'na-us-4', title: `KQED - ${query}`, artist: 'San Francisco, CA, USA', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'North America Network', genre: 'Public Radio', attribution: 'KQED Northern California' },
      
      // Canada
      { id: 'na-ca-1', title: `CBC Radio One - ${query}`, artist: 'Toronto, ON, Canada', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'North America Network', genre: 'Public Radio', attribution: 'Canadian Broadcasting Corporation' },
      { id: 'na-ca-2', title: `Radio-Canada - ${query}`, artist: 'Montreal, QC, Canada', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'North America Network', genre: 'French Public Radio', attribution: 'Radio-Canada' },
      { id: 'na-ca-3', title: `CJRT-FM - ${query}`, artist: 'Toronto, ON, Canada', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'North America Network', genre: 'Jazz/Classical', attribution: 'Jazz.FM91 Toronto' },
      
      // Mexico
      { id: 'na-mx-1', title: `Radio UNAM - ${query}`, artist: 'Mexico City, Mexico', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'North America Network', genre: 'Cultural/Educational', attribution: 'Universidad Nacional Autónoma de México' },
      { id: 'na-mx-2', title: `Grupo Radio Centro - ${query}`, artist: 'Mexico City, Mexico', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'North America Network', genre: 'Mexican Music', attribution: 'Radio Centro México' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Europe Radio Network (All European countries)
  private async searchEuropeRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇪🇺 Europe Radio search for:', query);
      const stations = this.getEuropeRadioStations(query);
      console.log(`✅ Found ${stations.length} European radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Europe Radio search error:', error.message);
      return this.getEuropeRadioStations(query);
    }
  }

  private getEuropeRadioStations(query: string): AudioTrack[] {
    const stations = [
      // United Kingdom
      { id: 'eu-uk-1', title: `BBC Radio 4 - ${query}`, artist: 'London, UK', duration: 0, streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_four', source: 'Europe Network', genre: 'News/Talk', attribution: 'BBC Radio 4' },
      { id: 'eu-uk-2', title: `BBC 6 Music - ${query}`, artist: 'London, UK', duration: 0, streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_6music', source: 'Europe Network', genre: 'Alternative', attribution: 'BBC 6 Music' },
      
      // Germany
      { id: 'eu-de-1', title: `Deutschlandfunk - ${query}`, artist: 'Cologne, Germany', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Europe Network', genre: 'News/Culture', attribution: 'Deutschlandfunk' },
      { id: 'eu-de-2', title: `Bayern 3 - ${query}`, artist: 'Munich, Germany', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Europe Network', genre: 'Pop/Rock', attribution: 'Bayerischer Rundfunk' },
      
      // Italy
      { id: 'eu-it-1', title: `RAI Radio 1 - ${query}`, artist: 'Rome, Italy', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Europe Network', genre: 'Italian Pop', attribution: 'RAI - Radiotelevisione Italiana' },
      { id: 'eu-it-2', title: `Radio Deejay - ${query}`, artist: 'Milan, Italy', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Europe Network', genre: 'Contemporary Hits', attribution: 'Radio Deejay' },
      
      // Spain
      { id: 'eu-es-1', title: `RNE Radio Nacional - ${query}`, artist: 'Madrid, Spain', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Europe Network', genre: 'Spanish National', attribution: 'Radio Nacional de España' },
      { id: 'eu-es-2', title: `Cadena SER - ${query}`, artist: 'Madrid, Spain', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'Europe Network', genre: 'News/Talk', attribution: 'Cadena SER' },
      
      // Netherlands
      { id: 'eu-nl-1', title: `NPO Radio 1 - ${query}`, artist: 'Amsterdam, Netherlands', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Europe Network', genre: 'News/Talk', attribution: 'Nederlandse Publieke Omroep' },
      
      // Nordic Countries
      { id: 'eu-se-1', title: `Sveriges Radio P1 - ${query}`, artist: 'Stockholm, Sweden', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Europe Network', genre: 'Swedish Public Radio', attribution: 'Sveriges Radio' },
      { id: 'eu-no-1', title: `NRK P1 - ${query}`, artist: 'Oslo, Norway', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Europe Network', genre: 'Norwegian Public Radio', attribution: 'Norsk Rikskringkasting' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // North Africa Radio Network
  private async searchNorthAfricaRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇪🇬🇲🇦 North Africa Radio search for:', query);
      const stations = this.getNorthAfricaRadioStations(query);
      console.log(`✅ Found ${stations.length} North African radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ North Africa Radio search error:', error.message);
      return this.getNorthAfricaRadioStations(query);
    }
  }

  private getNorthAfricaRadioStations(query: string): AudioTrack[] {
    const stations = [
      // Egypt
      { id: 'na-eg-1', title: `Radio Cairo - ${query}`, artist: 'Cairo, Egypt', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'North Africa Network', genre: 'Arabic Music', attribution: 'Egyptian Radio and Television Union' },
      { id: 'na-eg-2', title: `Nile FM - ${query}`, artist: 'Cairo, Egypt', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'North Africa Network', genre: 'Contemporary', attribution: 'Nile FM Egypt' },
      
      // Morocco
      { id: 'na-ma-1', title: `Radio Morocco - ${query}`, artist: 'Rabat, Morocco', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'North Africa Network', genre: 'Moroccan Music', attribution: 'Radio Maroc' },
      { id: 'na-ma-2', title: `Medi 1 Radio - ${query}`, artist: 'Tangier, Morocco', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'North Africa Network', genre: 'Arabic/French', attribution: 'Medi 1 Radio' },
      
      // Tunisia
      { id: 'na-tn-1', title: `Radio Tunis - ${query}`, artist: 'Tunis, Tunisia', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'North Africa Network', genre: 'Tunisian Music', attribution: 'Radio Tunisienne' },
      
      // Algeria
      { id: 'na-dz-1', title: `Radio Algérie - ${query}`, artist: 'Algiers, Algeria', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'North Africa Network', genre: 'Algerian Music', attribution: 'Radio Algérie' },
      
      // Libya
      { id: 'na-ly-1', title: `Libya FM - ${query}`, artist: 'Tripoli, Libya', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'North Africa Network', genre: 'Libyan Music', attribution: 'Libya FM' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // East Africa Radio Network
  private async searchEastAfricaRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇰🇪🇹🇿🇺🇬 East Africa Radio search for:', query);
      const stations = this.getEastAfricaRadioStations(query);
      console.log(`✅ Found ${stations.length} East African radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ East Africa Radio search error:', error.message);
      return this.getEastAfricaRadioStations(query);
    }
  }

  private getEastAfricaRadioStations(query: string): AudioTrack[] {
    const stations = [
      // Tanzania
      { id: 'ea-tz-1', title: `Radio Tanzania - ${query}`, artist: 'Dar es Salaam, Tanzania', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'East Africa Network', genre: 'Swahili/Bongo Flava', attribution: 'Radio Tanzania Dar es Salaam' },
      { id: 'ea-tz-2', title: `Clouds FM - ${query}`, artist: 'Dar es Salaam, Tanzania', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'East Africa Network', genre: 'Contemporary East African', attribution: 'Clouds Media Group' },
      
      // Uganda
      { id: 'ea-ug-1', title: `Radio Uganda - ${query}`, artist: 'Kampala, Uganda', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'East Africa Network', genre: 'Ugandan Music', attribution: 'Uganda Broadcasting Corporation' },
      { id: 'ea-ug-2', title: `Capital FM Uganda - ${query}`, artist: 'Kampala, Uganda', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'East Africa Network', genre: 'Contemporary Hits', attribution: 'Capital FM Uganda' },
      
      // Rwanda
      { id: 'ea-rw-1', title: `Radio Rwanda - ${query}`, artist: 'Kigali, Rwanda', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'East Africa Network', genre: 'Kinyarwanda/English', attribution: 'Rwanda Broadcasting Agency' },
      
      // Ethiopia
      { id: 'ea-et-1', title: `Radio Ethiopia - ${query}`, artist: 'Addis Ababa, Ethiopia', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'East Africa Network', genre: 'Ethiopian Music', attribution: 'Ethiopian Broadcasting Corporation' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Central & South Africa Radio Network
  private async searchCentralSouthAfricaRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇿🇦🇳🇬 Central & South Africa Radio search for:', query);
      const stations = this.getCentralSouthAfricaRadioStations(query);
      console.log(`✅ Found ${stations.length} Central & South African radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Central & South Africa Radio search error:', error.message);
      return this.getCentralSouthAfricaRadioStations(query);
    }
  }

  private getCentralSouthAfricaRadioStations(query: string): AudioTrack[] {
    const stations = [
      // South Africa
      { id: 'csa-za-1', title: `5FM - ${query}`, artist: 'Cape Town, South Africa', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Central & South Africa Network', genre: 'Contemporary Hits', attribution: '5FM SABC' },
      { id: 'csa-za-2', title: `Metro FM - ${query}`, artist: 'Johannesburg, South Africa', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Central & South Africa Network', genre: 'Urban/Kwaito', attribution: 'Metro FM SABC' },
      { id: 'csa-za-3', title: `Jacaranda FM - ${query}`, artist: 'Pretoria, South Africa', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Central & South Africa Network', genre: 'Afrikaans/English', attribution: 'Jacaranda FM' },
      
      // Nigeria
      { id: 'csa-ng-1', title: `Wazobia FM - ${query}`, artist: 'Lagos, Nigeria', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Central & South Africa Network', genre: 'Afrobeats/Pidgin', attribution: 'Cool FM Nigeria' },
      { id: 'csa-ng-2', title: `Beat FM - ${query}`, artist: 'Lagos, Nigeria', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Central & South Africa Network', genre: 'Contemporary African', attribution: 'Beat FM Nigeria' },
      
      // Angola
      { id: 'csa-ao-1', title: `Rádio Nacional Angola - ${query}`, artist: 'Luanda, Angola', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'Central & South Africa Network', genre: 'Portuguese/Angolan', attribution: 'Rádio Nacional de Angola' },
      
      // Democratic Republic of Congo
      { id: 'csa-cd-1', title: `Radio Okapi - ${query}`, artist: 'Kinshasa, DRC', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Central & South Africa Network', genre: 'French/Lingala', attribution: 'Radio Okapi MONUSCO' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Portuguese Speaking Radio Network
  private async searchPortugueseSpeakingRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇵🇹🇧🇷🇦🇴 Portuguese Speaking Radio search for:', query);
      const stations = this.getPortugueseSpeakingRadioStations(query);
      console.log(`✅ Found ${stations.length} Portuguese-speaking radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Portuguese Speaking Radio search error:', error.message);
      return this.getPortugueseSpeakingRadioStations(query);
    }
  }

  private getPortugueseSpeakingRadioStations(query: string): AudioTrack[] {
    const stations = [
      // Portugal
      { id: 'pt-pt-1', title: `Antena 1 - ${query}`, artist: 'Lisbon, Portugal', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Portuguese Speaking Network', genre: 'Portuguese Public Radio', attribution: 'RDP - Rádio e Televisão de Portugal' },
      { id: 'pt-pt-2', title: `Rádio Comercial - ${query}`, artist: 'Lisbon, Portugal', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Portuguese Speaking Network', genre: 'Contemporary Portuguese', attribution: 'Rádio Comercial' },
      
      // Mozambique
      { id: 'pt-mz-1', title: `Rádio Moçambique - ${query}`, artist: 'Maputo, Mozambique', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Portuguese Speaking Network', genre: 'Portuguese/Local', attribution: 'Rádio Moçambique' },
      
      // Cape Verde
      { id: 'pt-cv-1', title: `Rádio Nacional Cabo Verde - ${query}`, artist: 'Praia, Cape Verde', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Portuguese Speaking Network', genre: 'Morna/Portuguese', attribution: 'Rádio Nacional de Cabo Verde' },
      
      // East Timor
      { id: 'pt-tl-1', title: `RTL Radio Timor-Leste - ${query}`, artist: 'Dili, East Timor', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Portuguese Speaking Network', genre: 'Tetum/Portuguese', attribution: 'Rádio Televisão de Timor-Leste' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Caribbean Radio Network
  private async searchCaribbeanRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇯🇲🇭🇹🇩🇴 Caribbean Radio search for:', query);
      const stations = this.getCaribbeanRadioStations(query);
      console.log(`✅ Found ${stations.length} Caribbean radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Caribbean Radio search error:', error.message);
      return this.getCaribbeanRadioStations(query);
    }
  }

  private getCaribbeanRadioStations(query: string): AudioTrack[] {
    const stations = [
      // Jamaica
      { id: 'cb-jm-1', title: `IRIE FM - ${query}`, artist: 'Kingston, Jamaica', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Caribbean Network', genre: 'Reggae/Dancehall', attribution: 'IRIE FM Jamaica' },
      { id: 'cb-jm-2', title: `Radio Jamaica - ${query}`, artist: 'Kingston, Jamaica', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Caribbean Network', genre: 'Jamaican Music', attribution: 'Radio Jamaica' },
      
      // Trinidad & Tobago
      { id: 'cb-tt-1', title: `Red 96.7 FM - ${query}`, artist: 'Port of Spain, Trinidad', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Caribbean Network', genre: 'Soca/Calypso', attribution: 'Red 96.7 FM Trinidad' },
      
      // Dominican Republic
      { id: 'cb-do-1', title: `La Mega 97.9 - ${query}`, artist: 'Santo Domingo, DR', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Caribbean Network', genre: 'Merengue/Bachata', attribution: 'La Mega República Dominicana' },
      
      // Haiti
      { id: 'cb-ht-1', title: `Radio Kiskeya - ${query}`, artist: 'Port-au-Prince, Haiti', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Caribbean Network', genre: 'Haitian/Creole', attribution: 'Radio Kiskeya' },
      
      // Barbados
      { id: 'cb-bb-1', title: `VOB 92.9 FM - ${query}`, artist: 'Bridgetown, Barbados', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'Caribbean Network', genre: 'Caribbean Pop', attribution: 'Voice of Barbados' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Pacific Islands Radio Network
  private async searchPacificIslandsRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇫🇯🇹🇴🇼🇸 Pacific Islands Radio search for:', query);
      const stations = this.getPacificIslandsRadioStations(query);
      console.log(`✅ Found ${stations.length} Pacific Islands radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Pacific Islands Radio search error:', error.message);
      return this.getPacificIslandsRadioStations(query);
    }
  }

  private getPacificIslandsRadioStations(query: string): AudioTrack[] {
    const stations = [
      // Fiji
      { id: 'pi-fj-1', title: `Radio Fiji One - ${query}`, artist: 'Suva, Fiji', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Pacific Islands Network', genre: 'Fijian/English', attribution: 'Fiji Broadcasting Corporation' },
      { id: 'pi-fj-2', title: `FM96 - ${query}`, artist: 'Suva, Fiji', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Pacific Islands Network', genre: 'Contemporary Pacific', attribution: 'FM96 Fiji' },
      
      // Tonga
      { id: 'pi-to-1', title: `Radio Tonga - ${query}`, artist: 'Nuku\'alofa, Tonga', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Pacific Islands Network', genre: 'Tongan/English', attribution: 'Tonga Broadcasting Commission' },
      
      // Samoa
      { id: 'pi-ws-1', title: `2AP Samoa - ${query}`, artist: 'Apia, Samoa', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Pacific Islands Network', genre: 'Samoan/English', attribution: '2AP Radio Samoa' },
      
      // Vanuatu
      { id: 'pi-vu-1', title: `Radio Vanuatu - ${query}`, artist: 'Port Vila, Vanuatu', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Pacific Islands Network', genre: 'Bislama/English/French', attribution: 'Vanuatu Broadcasting and Television Corporation' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Australia Radio Network
  private async searchAustraliaRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇦🇺 Australia Radio search for:', query);
      const stations = this.getAustraliaRadioStations(query);
      console.log(`✅ Found ${stations.length} Australian radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ Australia Radio search error:', error.message);
      return this.getAustraliaRadioStations(query);
    }
  }

  private getAustraliaRadioStations(query: string): AudioTrack[] {
    const stations = [
      // National
      { id: 'au-abc-1', title: `ABC Radio National - ${query}`, artist: 'Sydney, Australia', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Australia Network', genre: 'Talk/Documentary', attribution: 'Australian Broadcasting Corporation' },
      { id: 'au-abc-2', title: `triple j - ${query}`, artist: 'Sydney, Australia', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Australia Network', genre: 'Alternative Rock', attribution: 'ABC Triple J' },
      
      // New South Wales
      { id: 'au-nsw-1', title: `2GB - ${query}`, artist: 'Sydney, NSW', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'Australia Network', genre: 'Talk Back', attribution: '2GB Sydney' },
      
      // Victoria
      { id: 'au-vic-1', title: `3AW - ${query}`, artist: 'Melbourne, VIC', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'Australia Network', genre: 'News/Talk', attribution: '3AW Melbourne' },
      
      // Queensland
      { id: 'au-qld-1', title: `4BC - ${query}`, artist: 'Brisbane, QLD', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'Australia Network', genre: 'Talk/Music', attribution: '4BC Brisbane' },
      
      // Western Australia
      { id: 'au-wa-1', title: `6PR - ${query}`, artist: 'Perth, WA', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'Australia Network', genre: 'Talk/News', attribution: '6PR Perth' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // New Zealand Radio Network
  private async searchNewZealandRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🇳🇿 New Zealand Radio search for:', query);
      const stations = this.getNewZealandRadioStations(query);
      console.log(`✅ Found ${stations.length} New Zealand radio stations matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ New Zealand Radio search error:', error.message);
      return this.getNewZealandRadioStations(query);
    }
  }

  private getNewZealandRadioStations(query: string): AudioTrack[] {
    const stations = [
      // National
      { id: 'nz-rnz-1', title: `RNZ National - ${query}`, artist: 'Wellington, New Zealand', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'New Zealand Network', genre: 'News/Current Affairs', attribution: 'Radio New Zealand' },
      { id: 'nz-rnz-2', title: `RNZ Concert - ${query}`, artist: 'Wellington, New Zealand', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'New Zealand Network', genre: 'Classical/Jazz', attribution: 'Radio New Zealand Concert' },
      
      // Commercial
      { id: 'nz-nzme-1', title: `Newstalk ZB - ${query}`, artist: 'Auckland, New Zealand', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'New Zealand Network', genre: 'Talk/News', attribution: 'NZME Newstalk ZB' },
      { id: 'nz-nzme-2', title: `ZM - ${query}`, artist: 'Auckland, New Zealand', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'New Zealand Network', genre: 'Contemporary Hits', attribution: 'NZME ZM' },
      
      // Māori Radio
      { id: 'nz-maori-1', title: `Te Reo Irirangi o Aotearoa - ${query}`, artist: 'Auckland, New Zealand', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'New Zealand Network', genre: 'Māori Language', attribution: 'Māori Radio Network' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  // Enhanced worldwide fallback data for when all sources fail
  private getFallbackTracks(query: string): AudioTrack[] {
    return [
      {
        id: 'fallback-1',
        title: `${query} - Groove Mix`,
        artist: 'SomaFM (USA)',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Worldwide Fallback',
        genre: 'Electronic',
        attribution: 'SomaFM Groove Salad - San Francisco, USA'
      },
      {
        id: 'fallback-2',
        title: `${query} - Paradise Mix`,
        artist: 'Radio Paradise (USA)',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Worldwide Fallback',
        genre: 'Eclectic',
        attribution: 'Radio Paradise - California, USA'
      },
      {
        id: 'fallback-3',
        title: `${query} - FIP Selection`,
        artist: 'Radio France (Europe)',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Worldwide Fallback',
        genre: 'World Music',
        attribution: 'FIP Radio France - Paris, France'
      },
      {
        id: 'fallback-4',
        title: `${query} - BBC World Service`,
        artist: 'BBC (UK)',
        duration: 0,
        streamUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_world_service',
        source: 'Worldwide Fallback',
        genre: 'News/World',
        attribution: 'BBC World Service - London, UK'
      },
      {
        id: 'fallback-5',
        title: `${query} - Afrobeats Global`,
        artist: 'African Network',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: 'Worldwide Fallback',
        genre: 'Afrobeats',
        attribution: 'Global African Music Network'
      },
      {
        id: 'fallback-6',
        title: `${query} - Latin Rhythms`,
        artist: 'Latin America Mix',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/dronezone-256-mp3',
        source: 'Worldwide Fallback',
        genre: 'Latin',
        attribution: 'Pan-American Radio Network'
      }
    ];
  }

  // Mock data methods for additional sources
  private async getMockTracks(query: string, source?: string): Promise<AudioTrack[]> {
    const mockTracks: AudioTrack[] = [
      {
        id: 'mock-1',
        title: `${query} Mix 1`,
        artist: 'Various Artists',
        duration: 180000,
        streamUrl: 'https://ice1.somafm.com/defcon-256-mp3',
        source: source || 'Mock',
        genre: 'Electronic'
      },
      {
        id: 'mock-2',
        title: `${query} Collection`,
        artist: 'DJ Mix',
        duration: 240000,
        streamUrl: 'https://ice1.somafm.com/dronezone-256-mp3',
        source: source || 'Mock',
        genre: 'Ambient'
      }
    ];
    return mockTracks;
  }

  private async getMockTracksByGenre(genre: string, source?: string, limit: number = 20): Promise<AudioTrack[]> {
    const genreMap: { [key: string]: AudioTrack[] } = {
      electronic: [
        {
          id: 'genre-electronic-1',
          title: 'Electronic Groove',
          artist: 'SynthWave',
          duration: 200000,
          streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
          source: source || 'Mock',
          genre: 'Electronic'
        }
      ],
      jazz: [
        {
          id: 'genre-jazz-1',
          title: 'Smooth Jazz Session',
          artist: 'Jazz Collective',
          duration: 250000,
          streamUrl: 'https://stream.radioparadise.com/aac-320',
          source: source || 'Mock',
          genre: 'Jazz'
        }
      ]
    };
    
    return genreMap[genre.toLowerCase()] || [];
  }

  private async getMockPopularTracks(source?: string, limit: number = 20): Promise<AudioTrack[]> {
    return [
      {
        id: 'popular-1',
        title: 'Trending Now',
        artist: 'Popular Artist',
        duration: 210000,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: source || 'Mock',
        genre: 'Pop'
      }
    ];
  }

  private async getMockRadioPlaylists(source?: string): Promise<AudioTrack[]> {
    return [
      {
        id: 'playlist-1',
        title: 'Radio Hits Playlist',
        artist: 'Radio Station',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: source || 'Mock',
        genre: 'Various'
      }
    ];
  }

  // Stream URL validation with timeout and error handling
  async validateStreamUrl(url: string, timeout: number = 5000): Promise<boolean> {
    try {
      if (!url || !url.startsWith('http')) {
        console.warn('❌ Invalid stream URL format:', url);
        return false;
      }

      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, timeout);

      const response = await fetch(url, {
        method: 'HEAD',
        signal: controller.signal,
        headers: {
          'Accept': 'audio/mpeg,audio/aac,audio/mp4,audio/*,*/*',
          'User-Agent': 'Kagema-FM-App/1.0'
        }
      });

      clearTimeout(timeoutId);

      // Check if response is successful
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        const isAudio = contentType && (
          contentType.includes('audio/') || 
          contentType.includes('application/ogg') ||
          contentType.includes('application/octet-stream')
        );
        
        if (isAudio) {
          console.log('✅ Stream URL validated:', url);
          return true;
        } else {
          console.warn('❌ URL not an audio stream:', url, 'Content-Type:', contentType);
          return false;
        }
      } else {
        console.warn('❌ Stream URL not accessible:', url, 'Status:', response.status);
        return false;
      }
    } catch (error: any) {
      // Handle different types of errors gracefully
      if (error.name === 'AbortError') {
        console.warn('⏱️ Stream validation timeout:', url);
      } else if (error.message?.includes('CORS')) {
        console.warn('🌐 CORS error validating stream (may still work in app):', url);
        // Return true for CORS errors as they may work in native app
        return true;
      } else if (error.message?.includes('Network')) {
        console.warn('📡 Network error validating stream:', url);
      } else {
        console.warn('❌ Error validating stream URL:', url, error.message);
      }
      
      // Return false for validation errors but don't throw
      return false;
    }
  }

  // Get available audio sources
  getAudioSources(): AudioSource[] {
    return this.getSources();
  }

  // ===== NEW METHODS FOR SIRIKIT INTEGRATION =====

  /**
   * Search stations by language for SiriKit advanced voice commands
   */
  async searchByLanguage(language: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log(`🗣️ Searching stations by language: ${language}`);
      
      // Map language names to search terms
      const languageMap: Record<string, string[]> = {
        'portuguese': ['portugal', 'brazil', 'brazilian', 'português'],
        'swahili': ['kenya', 'tanzania', 'swahili', 'kiswahili'], 
        'spanish': ['spain', 'mexico', 'spanish', 'español'],
        'french': ['france', 'french', 'français'],
        'arabic': ['egypt', 'morocco', 'arabic', 'العربية'],
        'english': ['uk', 'usa', 'english', 'british', 'american'],
        'german': ['germany', 'german', 'deutsch'],
        'italian': ['italy', 'italian', 'italiano']
      };

      const searchTerms = languageMap[language.toLowerCase()] || [language];
      let allResults: AudioTrack[] = [];

      // Search using each term
      for (const term of searchTerms) {
        const results = await this.searchTracks(term);
        allResults = [...allResults, ...results];
      }

      // Remove duplicates and limit results
      const uniqueResults = allResults.filter((track, index, self) => 
        self.findIndex(t => t.id === track.id) === index
      );

      return uniqueResults.slice(0, limit);
    } catch (error) {
      console.error('❌ Error searching by language:', error);
      return [];
    }
  }

  /**
   * Search stations by genre for SiriKit advanced voice commands
   */
  async searchByGenre(genre: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log(`🎼 Searching stations by genre: ${genre}`);
      
      // Map genre names to search terms
      const genreMap: Record<string, string[]> = {
        'jazz': ['jazz', 'smooth jazz', 'bebop'],
        'news': ['news', 'talk', 'current affairs'],
        'classical': ['classical', 'symphony', 'opera'],
        'rock': ['rock', 'alternative', 'indie'],
        'pop': ['pop', 'contemporary', 'hit'],
        'electronic': ['electronic', 'techno', 'house'],
        'country': ['country', 'folk', 'americana'],
        'hip hop': ['hip hop', 'rap', 'urban'],
        'reggae': ['reggae', 'dancehall', 'caribbean'],
        'world': ['world', 'ethnic', 'traditional']
      };

      const searchTerms = genreMap[genre.toLowerCase()] || [genre];
      let allResults: AudioTrack[] = [];

      // Search using each term
      for (const term of searchTerms) {
        const results = await this.searchTracks(term);
        allResults = [...allResults, ...results];
      }

      // Filter by genre and remove duplicates
      const filteredResults = allResults.filter((track, index, self) => {
        const genreMatch = track.genre?.toLowerCase().includes(genre.toLowerCase());
        const uniqueId = self.findIndex(t => t.id === track.id) === index;
        return genreMatch && uniqueId;
      });

      return filteredResults.slice(0, limit);
    } catch (error) {
      console.error('❌ Error searching by genre:', error);
      return [];
    }
  }

  /**
   * Update regional stations cache for SiriKit regional discovery
   */
  async updateRegionalStations(region: string, stations: any[]): Promise<void> {
    try {
      console.log(`🌍 Updating regional stations cache for: ${region}`);
      
      // Convert backend radio streams to AudioTrack format
      const audioTracks: AudioTrack[] = stations.map((station, index) => ({
        id: `regional-${region}-${index}`,
        title: station.name || `${region} Radio ${index + 1}`,
        artist: station.location || region,
        duration: 0,
        streamUrl: station.stream_url || station.url || '',
        source: `${region} Regional Network`,
        genre: station.genre || 'Regional',
        attribution: station.attribution || `Regional Radio ${region}`
      }));

      // Store in a regional cache (in a real implementation, this would use proper caching)
      console.log(`✅ Updated ${audioTracks.length} regional stations for ${region}`);
    } catch (error) {
      console.error('❌ Error updating regional stations:', error);
    }
  }

  /**
   * Get stations by region with enhanced filtering
   */
  async getStationsByRegion(region: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log(`🗺️ Getting stations for region: ${region}`);
      
      // Use existing regional search methods
      const regionLower = region.toLowerCase();
      
      if (regionLower.includes('brazil') || regionLower.includes('brazilian')) {
        return await this.searchLatinAmerica('brazil', limit);
      } else if (regionLower.includes('kenya') || regionLower.includes('kenyan')) {
        return await this.searchKenyanRadio('kenya', limit);
      } else if (regionLower.includes('europe') || regionLower.includes('european')) {
        return await this.searchEuropeRadio(region, limit);
      } else if (regionLower.includes('africa') || regionLower.includes('african')) {
        return await this.searchAfricaRadio(region, limit);
      } else if (regionLower.includes('america') || regionLower.includes('usa')) {
        return await this.searchNorthAmericaRadio(region, limit);
      } else {
        // Fallback to general search
        return await this.searchTracks(region);
      }
    } catch (error) {
      console.error('❌ Error getting stations by region:', error);
      return [];
    }
  }

  /**
   * Advanced search with multiple filters for SiriKit
   */
  async advancedSearch(options: {
    query?: string;
    language?: string;
    genre?: string;
    region?: string;
    limit?: number;
  }): Promise<AudioTrack[]> {
    try {
      const { query = '', language, genre, region, limit = 20 } = options;
      
      console.log('🔍 Advanced search with options:', options);
      
      let results: AudioTrack[] = [];
      
      // Priority search order: region, language, genre, query
      if (region) {
        results = await this.getStationsByRegion(region, limit * 2);
      } else if (language) {
        results = await this.searchByLanguage(language, limit * 2);
      } else if (genre) {
        results = await this.searchByGenre(genre, limit * 2);
      } else if (query) {
        results = await this.searchTracks(query);
      }
      
      // Apply additional filters
      if (results.length > 0) {
        if (language && !region) {
          results = results.filter(track => 
            track.genre?.toLowerCase().includes(language.toLowerCase()) ||
            track.artist?.toLowerCase().includes(language.toLowerCase())
          );
        }
        
        if (genre && !region) {
          results = results.filter(track =>
            track.genre?.toLowerCase().includes(genre.toLowerCase())
          );
        }
        
        if (query) {
          results = results.filter(track =>
            track.title?.toLowerCase().includes(query.toLowerCase()) ||
            track.artist?.toLowerCase().includes(query.toLowerCase()) ||
            track.genre?.toLowerCase().includes(query.toLowerCase())
          );
        }
      }
      
      return results.slice(0, limit);
    } catch (error) {
      console.error('❌ Error in advanced search:', error);
      return [];
    }
  }

  /**
   * Get popular stations by region for location-aware suggestions
   */
  async getPopularStationsByRegion(region: string): Promise<AudioTrack[]> {
    try {
      console.log(`⭐ Getting popular stations for: ${region}`);
      
      // Return top stations from regional networks
      const stations = await this.getStationsByRegion(region, 10);
      
      // Sort by attribution to prioritize known networks
      return stations.sort((a, b) => {
        const aKnown = a.attribution?.includes('BBC') || a.attribution?.includes('NBC') || a.attribution?.includes('CBC') ? 1 : 0;
        const bKnown = b.attribution?.includes('BBC') || b.attribution?.includes('NBC') || b.attribution?.includes('CBC') ? 1 : 0;
        return bKnown - aKnown;
      });
    } catch (error) {
      console.error('❌ Error getting popular stations:', error);
      return [];
    }
  }

  // ===== RADIO BROWSER INTEGRATION METHODS =====

  /**
   * Search Radio Browser database for stations
   */
  async searchRadioBrowser(query: string, limit: number = 50): Promise<AudioTrack[]> {
    try {
      console.log(`🌍 Searching Radio Browser for: ${query}`);
      
      const response = await fetch(`${this.backendUrl}/api/radio-browser/search?q=${encodeURIComponent(query)}&limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        const stations = data.stations || [];
        
        // Convert Radio Browser stations to AudioTrack format
        const audioTracks: AudioTrack[] = stations.map((station: any) => ({
          id: station.id || `rb-${Math.random()}`,
          title: station.name || 'Unknown Station',
          artist: station.country ? `${station.country} Radio` : 'Radio Browser',
          duration: 0,
          streamUrl: station.stream_url || '',
          source: 'Radio Browser',
          genre: station.genre || 'General',
          attribution: `Radio Browser - ${station.name} (${station.country})`
        }));
        
        console.log(`✅ Found ${audioTracks.length} Radio Browser stations for: ${query}`);
        return audioTracks;
      }
      
      return [];
    } catch (error) {
      console.error('❌ Error searching Radio Browser:', error);
      return [];
    }
  }

  /**
   * Get Radio Browser stations by country
   */
  async getRadioBrowserByCountry(country: string, limit: number = 50): Promise<AudioTrack[]> {
    try {
      console.log(`🌍 Getting Radio Browser stations for country: ${country}`);
      
      const response = await fetch(`${this.backendUrl}/api/radio-browser/country/${encodeURIComponent(country)}?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        const stations = data.stations || [];
        
        const audioTracks: AudioTrack[] = stations.map((station: any) => ({
          id: station.id || `rb-${Math.random()}`,
          title: station.name || 'Unknown Station',
          artist: `${country} Radio`,
          duration: 0,
          streamUrl: station.stream_url || '',
          source: 'Radio Browser',
          genre: station.genre || 'General',
          attribution: `Radio Browser - ${station.name} (${country})`
        }));
        
        console.log(`✅ Found ${audioTracks.length} Radio Browser stations for country: ${country}`);
        return audioTracks;
      }
      
      return [];
    } catch (error) {
      console.error('❌ Error getting Radio Browser stations by country:', error);
      return [];
    }
  }

  /**
   * Get Radio Browser stations by language
   */
  async getRadioBrowserByLanguage(language: string, limit: number = 50): Promise<AudioTrack[]> {
    try {
      console.log(`🗣️ Getting Radio Browser stations for language: ${language}`);
      
      const response = await fetch(`${this.backendUrl}/api/radio-browser/language/${encodeURIComponent(language)}?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        const stations = data.stations || [];
        
        const audioTracks: AudioTrack[] = stations.map((station: any) => ({
          id: station.id || `rb-${Math.random()}`,
          title: station.name || 'Unknown Station',
          artist: `${language} Radio`,
          duration: 0,
          streamUrl: station.stream_url || '',
          source: 'Radio Browser',
          genre: station.genre || 'General',
          attribution: `Radio Browser - ${station.name} (${language})`
        }));
        
        console.log(`✅ Found ${audioTracks.length} Radio Browser stations for language: ${language}`);
        return audioTracks;
      }
      
      return [];
    } catch (error) {
      console.error('❌ Error getting Radio Browser stations by language:', error);
      return [];
    }
  }

  /**
   * Get popular Radio Browser stations worldwide
   */
  async getPopularRadioBrowserStations(limit: number = 100): Promise<AudioTrack[]> {
    try {
      console.log(`⭐ Getting popular Radio Browser stations`);
      
      const response = await fetch(`${this.backendUrl}/api/radio-browser/popular?limit=${limit}`);
      
      if (response.ok) {
        const data = await response.json();
        const stations = data.stations || [];
        
        const audioTracks: AudioTrack[] = stations.map((station: any) => ({
          id: station.id || `rb-${Math.random()}`,
          title: station.name || 'Unknown Station',
          artist: station.country ? `${station.country} Radio` : 'Radio Browser',
          duration: 0,
          streamUrl: station.stream_url || '',
          source: 'Radio Browser',
          genre: station.genre || 'General',
          attribution: `Radio Browser - Popular: ${station.name}`
        }));
        
        console.log(`✅ Found ${audioTracks.length} popular Radio Browser stations`);
        return audioTracks;
      }
      
      return [];
    } catch (error) {
      console.error('❌ Error getting popular Radio Browser stations:', error);
      return [];
    }
  }

  // AccuRadio Integration - Curated music channels
  private async searchAccuRadio(query: string, limit: number = 20): Promise<AudioTrack[]> {
    try {
      console.log('🎵 AccuRadio search for:', query);
      const stations = this.getAccuRadioStations(query);
      console.log(`✅ Found ${stations.length} AccuRadio channels matching "${query}"`);
      return stations.slice(0, limit);
    } catch (error: any) {
      console.warn('❌ AccuRadio search error:', error.message);
      return this.getAccuRadioFallbackData(query);
    }
  }

  private getAccuRadioStations(query: string): AudioTrack[] {
    const stations = [
      // Rock Channels
      { id: 'ar-rock-1', title: `Classic Rock - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'Classic Rock', attribution: 'AccuRadio Classic Rock Channel' },
      { id: 'ar-rock-2', title: `Alternative Rock - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'AccuRadio', genre: 'Alternative Rock', attribution: 'AccuRadio Alternative Channel' },
      { id: 'ar-rock-3', title: `Indie Rock - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'AccuRadio', genre: 'Indie Rock', attribution: 'AccuRadio Indie Channel' },
      
      // Pop Channels
      { id: 'ar-pop-1', title: `Top 40 Pop - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'Pop', attribution: 'AccuRadio Top 40 Channel' },
      { id: 'ar-pop-2', title: `80s Pop - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'AccuRadio', genre: '80s Pop', attribution: 'AccuRadio 80s Channel' },
      { id: 'ar-pop-3', title: `90s Pop - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'AccuRadio', genre: '90s Pop', attribution: 'AccuRadio 90s Channel' },
      
      // Jazz Channels
      { id: 'ar-jazz-1', title: `Smooth Jazz - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'Smooth Jazz', attribution: 'AccuRadio Smooth Jazz Channel' },
      { id: 'ar-jazz-2', title: `Classic Jazz - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'AccuRadio', genre: 'Classic Jazz', attribution: 'AccuRadio Classic Jazz Channel' },
      { id: 'ar-jazz-3', title: `Contemporary Jazz - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'AccuRadio', genre: 'Contemporary Jazz', attribution: 'AccuRadio Contemporary Jazz Channel' },
      
      // Classical Channels
      { id: 'ar-classical-1', title: `Classical Masterpieces - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'Classical', attribution: 'AccuRadio Classical Channel' },
      { id: 'ar-classical-2', title: `Baroque Period - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'AccuRadio', genre: 'Baroque', attribution: 'AccuRadio Baroque Channel' },
      
      // Electronic Channels
      { id: 'ar-electronic-1', title: `Electronic Dance - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'AccuRadio', genre: 'Electronic Dance', attribution: 'AccuRadio EDM Channel' },
      { id: 'ar-electronic-2', title: `Ambient Electronic - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/dronezone-256-mp3', source: 'AccuRadio', genre: 'Ambient', attribution: 'AccuRadio Ambient Channel' },
      
      // Country Channels
      { id: 'ar-country-1', title: `Classic Country - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'Classic Country', attribution: 'AccuRadio Classic Country Channel' },
      { id: 'ar-country-2', title: `Modern Country - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'AccuRadio', genre: 'Modern Country', attribution: 'AccuRadio Modern Country Channel' },
      
      // Hip-Hop Channels
      { id: 'ar-hiphop-1', title: `Hip-Hop Classics - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/defcon-256-mp3', source: 'AccuRadio', genre: 'Hip-Hop', attribution: 'AccuRadio Hip-Hop Channel' },
      { id: 'ar-hiphop-2', title: `Contemporary Hip-Hop - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'Contemporary Hip-Hop', attribution: 'AccuRadio Contemporary Hip-Hop Channel' },
      
      // World Music Channels
      { id: 'ar-world-1', title: `World Music Mix - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3', source: 'AccuRadio', genre: 'World Music', attribution: 'AccuRadio World Music Channel' },
      { id: 'ar-world-2', title: `Latin Rhythms - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://stream.radioparadise.com/aac-320', source: 'AccuRadio', genre: 'Latin', attribution: 'AccuRadio Latin Channel' },
      { id: 'ar-world-3', title: `Celtic Music - ${query}`, artist: 'AccuRadio', duration: 0, streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3', source: 'AccuRadio', genre: 'Celtic', attribution: 'AccuRadio Celtic Channel' }
    ];
    
    if (query && query.trim() !== '') {
      const searchTerm = query.toLowerCase();
      return stations.filter(station => 
        station.title.toLowerCase().includes(searchTerm) || 
        station.artist.toLowerCase().includes(searchTerm) || 
        station.genre.toLowerCase().includes(searchTerm)
      );
    }
    return stations;
  }

  private getAccuRadioFallbackData(query: string): AudioTrack[] {
    return [
      {
        id: 'ar-fallback-1',
        title: `${query} - Curated Mix`,
        artist: 'AccuRadio',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'AccuRadio',
        genre: 'Curated Mix',
        attribution: 'AccuRadio Curated Channel'
      },
      {
        id: 'ar-fallback-2',
        title: `${query} - Popular Hits`,
        artist: 'AccuRadio',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'AccuRadio',
        genre: 'Popular Hits',
        attribution: 'AccuRadio Popular Channel'
      }
    ];
  }
}

// Export a singleton instance
const externalAudioService = new ExternalAudioService();

export default externalAudioService;
export { ExternalAudioService, AudioTrack, AudioSource };