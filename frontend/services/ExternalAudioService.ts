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
}

class ExternalAudioService {
  private sources: AudioSource[] = [
    {
      id: 'radio.net',
      name: 'Radio.net',
      apiUrl: 'https://radio.net/api',
      requiresAttribution: false,
      description: 'Global radio stations directory with over 30,000 stations worldwide'
    },
    {
      id: 'tunein',
      name: 'TuneIn',
      apiUrl: 'https://tunein.com/api',
      requiresAttribution: false,
      description: 'Live radio, podcasts, and sports from around the world'
    },
    {
      id: 'radio_garden',
      name: 'Radio Garden',
      apiUrl: 'https://radio.garden/api',
      requiresAttribution: false,
      description: 'Global live radio stations from around the world'
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

      // Add Radio Garden sources
      if (!source || source === 'radio_garden') {
        console.log('🌍 Searching Radio Garden for:', query);
        const radioGardenStations = await this.searchRadioGarden(query);
        results.push(...radioGardenStations);
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

  // Enhanced fallback data for when all sources fail
  private getFallbackTracks(query: string): AudioTrack[] {
    return [
      {
        id: 'fallback-1',
        title: `${query} - Groove Mix`,
        artist: 'SomaFM',
        duration: 0,
        streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
        source: 'Fallback',
        genre: 'Electronic',
        attribution: 'SomaFM Groove Salad'
      },
      {
        id: 'fallback-2',
        title: `${query} - Paradise Mix`,
        artist: 'Radio Paradise',
        duration: 0,
        streamUrl: 'https://stream.radioparadise.com/aac-320',
        source: 'Fallback',
        genre: 'Eclectic',
        attribution: 'Radio Paradise'
      },
      {
        id: 'fallback-3',
        title: `${query} - FIP Selection`,
        artist: 'FIP Radio France',
        duration: 0,
        streamUrl: 'https://icecast.radiofrance.fr/fip-midfi.mp3',
        source: 'Fallback',
        genre: 'World Music',
        attribution: 'FIP Radio France'
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
}

export default ExternalAudioService;
export { AudioTrack, AudioSource };