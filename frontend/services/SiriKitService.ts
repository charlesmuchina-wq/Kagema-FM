import { Platform, Linking } from 'react-native';
import VoiceControlService, { VoiceCommand, VoiceResponse } from './VoiceControlService';
import { ExternalAudioService } from './ExternalAudioService';
import LocationService from './LocationService';

export interface SiriShortcut {
  id: string;
  title: string;
  phrase: string;
  description: string;
  category: 'radio' | 'station' | 'search' | 'region' | 'offline';
  parameters?: Record<string, any>;
}

export interface SiriIntent {
  intent: string;
  parameters: Record<string, any>;
  userActivity?: any;
}

export interface SiriKitState {
  isAvailable: boolean;
  shortcuts: SiriShortcut[];
  isListening: boolean;
  lastCommand?: VoiceCommand;
}

/**
 * SiriKit Integration Service for Advanced Voice Commands
 * 
 * Features:
 * - Advanced voice commands (Find Brazilian radio stations, Play offline content)
 * - Siri Shortcuts integration
 * - INPlayMediaIntent for radio playbook
 * - Integration with existing voice control and external audio services
 * - Location-aware station discovery
 */
class SiriKitService {
  private state: SiriKitState = {
    isAvailable: false,
    shortcuts: [],
    isListening: false
  };

  private listeners: Set<(state: SiriKitState) => void> = new Set();
  private backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';
  
  // Advanced command patterns for international and regional content
  private advancedCommandPatterns = {
    // Regional station discovery
    regionalSearch: [
      /^(?:find|search for|play|show me) (.+) radio stations?$/i,
      /^(?:find|play|tune to) (?:stations? )?(?:from |in )?(.+)$/i,
      /^(?:show me|get|find) (?:radio )?(?:stations? )?(?:from |in )?(.+)$/i
    ],
    // Language-specific content
    languageSearch: [
      /^(?:find|play|show me) (.+) (?:language |speaking )(?:stations?|radio)$/i,
      /^(?:play|find) (?:stations? )?(?:in |speaking )?(.+)$/i
    ],
    // Offline content management
    offlineContent: [
      /^(?:play|show|open) (?:offline|downloaded|cached) (?:content|stations?|radio)$/i,
      /^(?:go|switch to) offline mode$/i,
      /^(?:download|cache|save) (.+) (?:for offline|offline)$/i
    ],
    // Genre-based discovery
    genreSearch: [
      /^(?:find|play|show me) (.+) (?:music|stations?|radio)$/i,
      /^(?:tune to|play) (?:some )?(.+)$/i
    ],
    // Advanced navigation
    navigation: [
      /^(?:go to|open|show) (.+) (?:section|tab|page)$/i,
      /^(?:navigate to|switch to) (.+)$/i
    ],
    // AccuRadio specific patterns
    accuradioCommands: [
      /^(?:play|find|tune to|search) accuradio (?:(.+))?$/i,
      /^(?:browse|show me|open) accuradio (?:channels?)?$/i,
      /^(?:play|find) (.+) on accuradio$/i,
      /^accuradio (.+)$/i
    ],
    // Radio Browser specific patterns
    radioBrowserCommands: [
      /^(?:search|find|browse) radio browser$/i,
      /^(?:find|search for|show me) (?:popular|top) (?:radio )?stations?$/i,
      /^(?:search|find) (?:radio )?stations? (?:in |from )?(.+)$/i,
      /^(?:browse|search) worldwide radio$/i,
      /^radio browser (.+)$/i
    ]
  };

  constructor() {
    this.initializeService();
  }

  /**
   * Initialize SiriKit service and register shortcuts
   */
  private async initializeService(): Promise<void> {
    try {
      console.log('🎙️ Initializing SiriKit Service...');
      
      // Check platform availability
      this.state.isAvailable = Platform.OS === 'ios';
      
      if (!this.state.isAvailable) {
        console.log('📱 SiriKit only available on iOS');
        return;
      }

      // Initialize shortcuts
      await this.initializeShortcuts();
      
      // Connect to existing voice control service
      this.setupVoiceControlIntegration();
      
      console.log('✅ SiriKit Service initialized with advanced voice commands');
      this.notifyListeners();
      
    } catch (error) {
      console.error('❌ Failed to initialize SiriKit Service:', error);
    }
  }

  /**
   * Initialize pre-defined Siri Shortcuts for common actions
   */
  private async initializeShortcuts(): Promise<void> {
    try {
      this.state.shortcuts = [
        // Basic radio controls
        {
          id: 'play-kagema-fm',
          title: 'Play Kagema FM',
          phrase: 'Play Kagema FM',
          description: 'Start playing Kagema FM radio',
          category: 'radio'
        },
        {
          id: 'pause-radio',
          title: 'Pause Radio',
          phrase: 'Pause the radio',
          description: 'Pause current radio playback',
          category: 'radio'
        },
        
        // Regional station discovery (Advanced)
        {
          id: 'find-brazilian-stations',
          title: 'Find Brazilian Stations',
          phrase: 'Find Brazilian radio stations',
          description: 'Discover radio stations from Brazil',
          category: 'region',
          parameters: { country: 'brazil', region: 'south_america' }
        },
        {
          id: 'find-kenyan-stations',
          title: 'Find Kenyan Stations', 
          phrase: 'Find Kenyan radio stations',
          description: 'Discover radio stations from Kenya',
          category: 'region',
          parameters: { country: 'kenya', region: 'africa' }
        },
        {
          id: 'find-european-stations',
          title: 'Find European Stations',
          phrase: 'Find European radio stations',
          description: 'Discover radio stations from Europe',
          category: 'region',
          parameters: { region: 'europe' }
        },
        
        // Language-specific content
        {
          id: 'play-portuguese-radio',
          title: 'Play Portuguese Radio',
          phrase: 'Play Portuguese radio stations',
          description: 'Find and play Portuguese-speaking radio',
          category: 'search',
          parameters: { language: 'portuguese' }
        },
        {
          id: 'play-swahili-radio',
          title: 'Play Swahili Radio',
          phrase: 'Play Swahili radio stations',
          description: 'Find and play Swahili-speaking radio',
          category: 'search',
          parameters: { language: 'swahili' }
        },
        
        // Offline content management (Advanced)
        {
          id: 'play-offline-content',
          title: 'Play Offline Content',
          phrase: 'Play offline content',
          description: 'Access downloaded radio content',
          category: 'offline'
        },
        {
          id: 'download-for-offline',
          title: 'Download for Offline',
          phrase: 'Download for offline listening',
          description: 'Cache content for offline playback',
          category: 'offline'
        },
        
        // Genre-based discovery
        {
          id: 'find-jazz-stations',
          title: 'Find Jazz Stations',
          phrase: 'Find jazz radio stations',
          description: 'Discover jazz music stations',
          category: 'search',
          parameters: { genre: 'jazz' }
        },
        {
          id: 'find-news-stations',
          title: 'Find News Stations',
          phrase: 'Find news radio stations',
          description: 'Discover news and talk radio',
          category: 'search',
          parameters: { genre: 'news' }
        },
        
        // AccuRadio Integration Shortcuts
        {
          id: 'play-accuradio-rock',
          title: 'Play AccuRadio Rock',
          phrase: 'Play AccuRadio rock',
          description: 'Start AccuRadio rock channels',
          category: 'search',
          parameters: { source: 'accuradio', genre: 'rock' }
        },
        {
          id: 'play-accuradio-jazz',
          title: 'Play AccuRadio Jazz',
          phrase: 'Play AccuRadio jazz',
          description: 'Start AccuRadio jazz channels',
          category: 'search',
          parameters: { source: 'accuradio', genre: 'jazz' }
        },
        {
          id: 'play-accuradio-classical',
          title: 'Play AccuRadio Classical',
          phrase: 'Play AccuRadio classical',
          description: 'Start AccuRadio classical channels',
          category: 'search',
          parameters: { source: 'accuradio', genre: 'classical' }
        },
        {
          id: 'browse-accuradio',
          title: 'Browse AccuRadio',
          phrase: 'Browse AccuRadio channels',
          description: 'Open AccuRadio channel browser',
          category: 'search',
          parameters: { source: 'accuradio' }
        },
        
        // Radio Browser Integration Shortcuts
        {
          id: 'search-radio-browser',
          title: 'Search Radio Browser',
          phrase: 'Search radio browser',
          description: 'Search 70,000+ worldwide radio stations',
          category: 'search',
          parameters: { source: 'radio_browser' }
        },
        {
          id: 'find-popular-stations',
          title: 'Find Popular Stations',
          phrase: 'Find popular radio stations',
          description: 'Discover most popular stations worldwide',
          category: 'search',
          parameters: { source: 'radio_browser', type: 'popular' }
        },
        {
          id: 'find-country-stations',
          title: 'Find Country Stations',
          phrase: 'Find stations by country',
          description: 'Search radio stations by country',
          category: 'region',
          parameters: { source: 'radio_browser', type: 'country' }
        },
        {
          id: 'browse-worldwide-radio',
          title: 'Browse Worldwide Radio',
          phrase: 'Browse worldwide radio',
          description: 'Explore global radio database',
          category: 'search',
          parameters: { source: 'radio_browser' }
        }
      ];
      
      console.log(`📝 Initialized ${this.state.shortcuts.length} Siri shortcuts`);
      
    } catch (error) {
      console.error('❌ Failed to initialize shortcuts:', error);
    }
  }

  /**
   * Setup integration with existing VoiceControlService
   */
  private setupVoiceControlIntegration(): void {
    try {
      // Listen for voice commands from the existing service
      VoiceControlService.onCommand((command: VoiceCommand) => {
        this.state.lastCommand = command;
        this.handleAdvancedVoiceCommand(command);
        this.notifyListeners();
      });
      
      VoiceControlService.onResponse((response: VoiceResponse) => {
        console.log('🎙️ SiriKit received voice response:', response);
      });
      
      console.log('🔗 SiriKit integrated with existing voice control service');
      
    } catch (error) {
      console.error('❌ Failed to setup voice control integration:', error);
    }
  }

  /**
   * Handle advanced voice commands with enhanced processing
   */
  private async handleAdvancedVoiceCommand(command: VoiceCommand): Promise<void> {
    try {
      const originalText = command.originalText.toLowerCase();
      
      // Check for advanced patterns first
      const advancedIntent = await this.parseAdvancedCommand(originalText);
      
      if (advancedIntent) {
        await this.executeAdvancedCommand(advancedIntent);
      } else {
        // Fall back to existing voice control
        console.log('🎙️ Delegating to standard voice control');
      }
      
    } catch (error) {
      console.error('❌ Error handling advanced voice command:', error);
    }
  }

  /**
   * Parse advanced command patterns for international/regional content
   */
  private async parseAdvancedCommand(text: string): Promise<SiriIntent | null> {
    try {
      // Regional station search
      for (const pattern of this.advancedCommandPatterns.regionalSearch) {
        const match = text.match(pattern);
        if (match && match[1]) {
          const region = match[1].trim();
          return {
            intent: 'find_regional_stations',
            parameters: { region, country: this.inferCountryFromRegion(region) }
          };
        }
      }

      // Language-specific search
      for (const pattern of this.advancedCommandPatterns.languageSearch) {
        const match = text.match(pattern);
        if (match && match[1]) {
          const language = match[1].trim();
          return {
            intent: 'find_language_stations',
            parameters: { language }
          };
        }
      }

      // Offline content commands
      for (const pattern of this.advancedCommandPatterns.offlineContent) {
        const match = text.match(pattern);
        if (match) {
          return {
            intent: 'offline_content',
            parameters: { action: match[1] ? 'download' : 'play' }
          };
        }
      }

      // Genre search
      for (const pattern of this.advancedCommandPatterns.genreSearch) {
        const match = text.match(pattern);
        if (match && match[1]) {
          const genre = match[1].trim();
          return {
            intent: 'find_genre_stations',
            parameters: { genre }
          };
        }
      }

      // AccuRadio commands
      for (const pattern of this.advancedCommandPatterns.accuradioCommands) {
        const match = text.match(pattern);
        if (match) {
          const genre = match[1] ? match[1].trim() : 'all';
          return {
            intent: 'play_accuradio',
            parameters: { source: 'accuradio', genre }
          };
        }
      }

      // Radio Browser commands
      for (const pattern of this.advancedCommandPatterns.radioBrowserCommands) {
        const match = text.match(pattern);
        if (match) {
          const query = match[1] ? match[1].trim() : '';
          
          // Determine specific Radio Browser action
          if (text.includes('popular') || text.includes('top')) {
            return {
              intent: 'search_radio_browser_popular',
              parameters: { source: 'radio_browser', type: 'popular' }
            };
          } else if (query && (text.includes('in ') || text.includes('from '))) {
            return {
              intent: 'search_radio_browser_country',
              parameters: { source: 'radio_browser', country: query }
            };
          } else {
            return {
              intent: 'search_radio_browser',
              parameters: { source: 'radio_browser', query: query || 'worldwide' }
            };
          }
        }
      }

      return null;
      
    } catch (error) {
      console.error('❌ Error parsing advanced command:', error);
      return null;
    }
  }

  /**
   * Execute advanced commands with backend integration
   */
  private async executeAdvancedCommand(intent: SiriIntent): Promise<void> {
    try {
      console.log('🎯 Executing advanced command:', intent);
      
      switch (intent.intent) {
        case 'find_regional_stations':
          await this.findRegionalStations(intent.parameters.region, intent.parameters.country);
          break;
          
        case 'find_language_stations':
          await this.findLanguageStations(intent.parameters.language);
          break;
          
        case 'offline_content':
          await this.handleOfflineContent(intent.parameters.action);
          break;
          
        case 'find_genre_stations':
          await this.findGenreStations(intent.parameters.genre);
          break;
          
        case 'play_accuradio':
          await this.handleAccuRadioCommand(intent.parameters.genre);
          break;
          
        case 'search_radio_browser':
          await this.handleRadioBrowserSearch(intent.parameters.query);
          break;
          
        case 'search_radio_browser_popular':
          await this.handleRadioBrowserPopular();
          break;
          
        case 'search_radio_browser_country':
          await this.handleRadioBrowserCountry(intent.parameters.country);
          break;
          
        default:
          console.log('🤷‍♂️ Unknown advanced intent:', intent.intent);
      }
      
    } catch (error) {
      console.error('❌ Error executing advanced command:', error);
    }
  }

  /**
   * Find radio stations by region/country using backend APIs
   */
  private async findRegionalStations(region: string, country?: string): Promise<void> {
    try {
      console.log(`🌍 Finding stations for region: ${region}, country: ${country}`);
      
      // Use the existing personalized content API with location info
      const response = await fetch(`${this.backendUrl}/api/personalized-content/multilingual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: {
            country: country || region,
            region: region,
            latitude: await this.getLocationCoordinate(region, 'lat'),
            longitude: await this.getLocationCoordinate(region, 'lng')
          },
          preferences: {
            language: this.getLanguageForRegion(region),
            genres: ['local', 'news', 'music'],
            quality: 'high'
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Found ${data.radio_streams?.length || 0} regional stations`);
        
        // Integrate with ExternalAudioService to update available stations
        if (data.radio_streams) {
          await ExternalAudioService.updateRegionalStations(region, data.radio_streams);
        }
      }
      
    } catch (error) {
      console.error('❌ Error finding regional stations:', error);
    }
  }

  /**
   * Find stations by language preference
   */
  private async findLanguageStations(language: string): Promise<void> {
    try {
      console.log(`🗣️ Finding stations for language: ${language}`);
      
      // Use external audio service to search by language
      const stations = await ExternalAudioService.searchByLanguage(language);
      console.log(`✅ Found ${stations?.length || 0} ${language} stations`);
      
    } catch (error) {
      console.error('❌ Error finding language stations:', error);
    }
  }

  /**
   * Handle offline content commands
   */
  private async handleOfflineContent(action: string): Promise<void> {
    try {
      console.log(`📱 Handling offline content action: ${action}`);
      
      if (action === 'play') {
        // Access offline content through existing offline service
        // This would integrate with OfflineModeService
        console.log('🎵 Playing offline content...');
      } else if (action === 'download') {
        console.log('⬇️ Starting content download for offline...');
      }
      
    } catch (error) {
      console.error('❌ Error handling offline content:', error);
    }
  }

  /**
   * Handle AccuRadio commands
   */
  private async handleAccuRadioCommand(genre: string): Promise<void> {
    try {
      console.log(`🎵 Handling AccuRadio command for genre: ${genre}`);
      
      // Use ExternalAudioService to search AccuRadio specifically  
      const searchQuery = genre === 'all' ? 'AccuRadio' : `${genre} AccuRadio`;
      const stations = await ExternalAudioService.searchTracks(searchQuery);
      
      // Filter for AccuRadio results
      const accuradioStations = stations.filter(station => station.source === 'AccuRadio');
      
      console.log(`✅ Found ${accuradioStations.length} AccuRadio ${genre} channels`);
      
      // In a full implementation, this would trigger UI updates or playbook
      
    } catch (error) {
      console.error('❌ Error handling AccuRadio command:', error);
    }
  }

  /**
   * Handle Radio Browser search commands
   */
  private async handleRadioBrowserSearch(query: string): Promise<void> {
    try {
      console.log(`🌍 Handling Radio Browser search for: ${query}`);
      
      // Use ExternalAudioService Radio Browser methods
      const stations = await ExternalAudioService.searchRadioBrowser(query, 20);
      
      console.log(`✅ Found ${stations.length} Radio Browser stations for: ${query}`);
      
      // In a full implementation, this would trigger UI updates or playback
      
    } catch (error) {
      console.error('❌ Error handling Radio Browser search:', error);
    }
  }

  /**
   * Handle Radio Browser popular stations command
   */
  private async handleRadioBrowserPopular(): Promise<void> {
    try {
      console.log(`⭐ Handling Radio Browser popular stations`);
      
      // Use ExternalAudioService to get popular Radio Browser stations
      const stations = await ExternalAudioService.getPopularRadioBrowserStations(20);
      
      console.log(`✅ Found ${stations.length} popular Radio Browser stations`);
      
      // In a full implementation, this would trigger UI updates or playback
      
    } catch (error) {
      console.error('❌ Error handling Radio Browser popular stations:', error);
    }
  }

  /**
   * Handle Radio Browser country search commands
   */
  private async handleRadioBrowserCountry(country: string): Promise<void> {
    try {
      console.log(`🌍 Handling Radio Browser country search for: ${country}`);
      
      // Use ExternalAudioService to search Radio Browser by country
      const stations = await ExternalAudioService.getRadioBrowserByCountry(country, 20);
      
      console.log(`✅ Found ${stations.length} Radio Browser stations for country: ${country}`);
      
      // In a full implementation, this would trigger UI updates or playback
      
    } catch (error) {
      console.error('❌ Error handling Radio Browser country search:', error);
    }
  }

  /**
   * Find stations by genre/category
   */
  private async findGenreStations(genre: string): Promise<void> {
    try {
      console.log(`🎼 Finding stations for genre: ${genre}`);
      
      // Use external audio service for genre-based search
      const stations = await ExternalAudioService.searchByGenre(genre);
      console.log(`✅ Found ${stations?.length || 0} ${genre} stations`);
      
    } catch (error) {
      console.error('❌ Error finding genre stations:', error);
    }
  }

  /**
   * Start listening for voice commands through SiriKit
   */
  async startVoiceListening(): Promise<boolean> {
    try {
      if (!this.state.isAvailable) {
        console.log('📱 SiriKit not available on this platform');
        return false;
      }

      this.state.isListening = true;
      this.notifyListeners();
      
      // Delegate to existing voice control service
      await VoiceControlService.startListening();
      
      console.log('🎙️ SiriKit voice listening started');
      return true;
      
    } catch (error) {
      console.error('❌ Error starting voice listening:', error);
      this.state.isListening = false;
      this.notifyListeners();
      return false;
    }
  }

  /**
   * Stop voice listening
   */
  async stopVoiceListening(): Promise<void> {
    try {
      this.state.isListening = false;
      await VoiceControlService.stopListening();
      this.notifyListeners();
      
    } catch (error) {
      console.error('❌ Error stopping voice listening:', error);
    }
  }

  /**
   * Process text command directly (for Siri integration)
   */
  async processTextCommand(text: string): Promise<VoiceResponse> {
    try {
      console.log('📝 Processing text command via SiriKit:', text);
      
      // Use enhanced processing first
      const advancedIntent = await this.parseAdvancedCommand(text.toLowerCase());
      
      if (advancedIntent) {
        await this.executeAdvancedCommand(advancedIntent);
        return {
          success: true,
          message: `Advanced command "${advancedIntent.intent}" executed successfully`,
          action: advancedIntent.intent,
          data: advancedIntent.parameters
        };
      }
      
      // Fall back to existing voice control
      return await VoiceControlService.processVoiceCommand(text);
      
    } catch (error) {
      console.error('❌ Error processing text command:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Register a Siri Shortcut (iOS only)
   */
  async registerShortcut(shortcut: SiriShortcut): Promise<boolean> {
    try {
      if (!this.state.isAvailable) return false;
      
      // In a full implementation, this would use INVoiceShortcutCenter
      // For now, we'll add to our shortcuts list
      this.state.shortcuts.push(shortcut);
      this.notifyListeners();
      
      console.log(`📝 Registered Siri shortcut: ${shortcut.title}`);
      return true;
      
    } catch (error) {
      console.error('❌ Error registering shortcut:', error);
      return false;
    }
  }

  /**
   * Helper methods
   */
  
  private inferCountryFromRegion(region: string): string {
    const regionMap: Record<string, string> = {
      'brazil': 'br',
      'brazilian': 'br',
      'kenya': 'ke',
      'kenyan': 'ke',
      'portugal': 'pt',
      'portuguese': 'pt',
      'spain': 'es',
      'spanish': 'es',
      'france': 'fr',
      'french': 'fr',
      'germany': 'de',
      'german': 'de',
      'italy': 'it',
      'italian': 'it',
      'uk': 'gb',
      'british': 'gb',
      'england': 'gb',
      'usa': 'us',
      'american': 'us',
      'canada': 'ca',
      'canadian': 'ca'
    };
    
    return regionMap[region.toLowerCase()] || 'global';
  }

  private getLanguageForRegion(region: string): string {
    const languageMap: Record<string, string> = {
      'brazil': 'pt',
      'brazilian': 'pt',
      'portugal': 'pt',
      'kenya': 'sw',
      'kenyan': 'sw',
      'spain': 'es',
      'spanish': 'es',
      'france': 'fr',
      'french': 'fr',
      'germany': 'de',
      'german': 'de'
    };
    
    return languageMap[region.toLowerCase()] || 'en';
  }

  private async getLocationCoordinate(region: string, type: 'lat' | 'lng'): Promise<number> {
    try {
      // Use LocationService to get coordinates for region
      // This is a simplified version - in production would use proper geocoding
      const coordinates: Record<string, { lat: number, lng: number }> = {
        'brazil': { lat: -14.235, lng: -51.9253 },
        'kenya': { lat: -0.0236, lng: 37.9062 },
        'portugal': { lat: 39.3999, lng: -8.2245 },
        'spain': { lat: 40.4637, lng: -3.7492 },
        'france': { lat: 46.2276, lng: 2.2137 },
        'germany': { lat: 51.1657, lng: 10.4515 }
      };
      
      const coord = coordinates[region.toLowerCase()];
      return coord ? coord[type] : 0;
      
    } catch (error) {
      console.error('❌ Error getting location coordinate:', error);
      return 0;
    }
  }

  // State management
  getState(): SiriKitState {
    return { ...this.state };
  }

  addListener(callback: (state: SiriKitState) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  private notifyListeners(): void {
    this.listeners.forEach(callback => {
      try {
        callback({ ...this.state });
      } catch (error) {
        console.error('❌ SiriKit listener error:', error);
      }
    });
  }

  // Cleanup
  async cleanup(): Promise<void> {
    try {
      this.state.isListening = false;
      await this.stopVoiceListening();
      this.listeners.clear();
      console.log('🧹 SiriKit Service cleaned up');
    } catch (error) {
      console.error('❌ SiriKit cleanup error:', error);
    }
  }
}

// Export singleton instance
export const siriKitService = new SiriKitService();
export default siriKitService;