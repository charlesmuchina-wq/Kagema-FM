import AsyncStorage from '@react-native-async-storage/async-storage';

export interface SatelliteChannel {
  id: string;
  number: number;
  name: string;
  description: string;
  genre: string;
  provider: 'sirius' | 'xm' | 'global' | 'emergency';
  streamUrl: string;
  quality: 'standard' | 'hd' | 'premium';
  bitrate: string;
  isEncrypted: boolean;
  subscriptionRequired: boolean;
  emergencyBroadcast: boolean;
  coverage: {
    regions: string[];
    satellites: string[];
  };
}

export interface SatelliteProvider {
  id: string;
  name: string;
  description: string;
  channels: SatelliteChannel[];
  subscriptionRequired: boolean;
  coverage: 'global' | 'regional' | 'national';
  emergencyCapable: boolean;
}

export interface SatelliteConnection {
  isConnected: boolean;
  signalStrength: number; // 0-100
  provider: string;
  satelliteName: string;
  lastUpdate: number;
  coordinates?: [number, number];
}

export class SatelliteRadioService {
  private static instance: SatelliteRadioService;
  private providers: SatelliteProvider[] = [];
  private connection: SatelliteConnection | null = null;
  private isInitialized = false;
  private emergencyChannels: SatelliteChannel[] = [];

  static getInstance(): SatelliteRadioService {
    if (!SatelliteRadioService.instance) {
      SatelliteRadioService.instance = new SatelliteRadioService();
    }
    return SatelliteRadioService.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    console.log('🛰️ Initializing Satellite Radio Service...');
    
    try {
      await this.loadSatelliteProviders();
      await this.loadEmergencyChannels();
      await this.checkSatelliteAvailability();
      
      this.isInitialized = true;
      console.log('✅ Satellite Radio Service initialized');
    } catch (error) {
      console.error('❌ Satellite Radio Service initialization error:', error);
      this.isInitialized = true; // Initialize with fallback data
    }
  }

  private async loadSatelliteProviders(): Promise<void> {
    this.providers = [
      {
        id: 'sirius_xm',
        name: 'SiriusXM',
        description: 'Premier satellite radio with 300+ channels',
        subscriptionRequired: true,
        coverage: 'regional',
        emergencyCapable: true,
        channels: [
          {
            id: 'sirius_hits1',
            number: 2,
            name: 'SiriusXM Hits 1',
            description: 'Today\'s hits and yesterday\'s favorites',
            genre: 'Pop',
            provider: 'sirius',
            streamUrl: 'satellite://sirius/hits1',
            quality: 'hd',
            bitrate: '320kbps',
            isEncrypted: true,
            subscriptionRequired: true,
            emergencyBroadcast: false,
            coverage: {
              regions: ['north_america', 'canada'],
              satellites: ['SXM-7', 'SXM-8']
            }
          },
          {
            id: 'sirius_howard100',
            number: 100,
            name: 'Howard 100',
            description: 'Howard Stern uncensored',
            genre: 'Talk',
            provider: 'sirius',
            streamUrl: 'satellite://sirius/howard100',
            quality: 'hd',
            bitrate: '320kbps',
            isEncrypted: true,
            subscriptionRequired: true,
            emergencyBroadcast: false,
            coverage: {
              regions: ['north_america', 'canada'],
              satellites: ['SXM-7', 'SXM-8']
            }
          },
          {
            id: 'sirius_jazz',
            number: 67,
            name: 'Real Jazz',
            description: 'Pure jazz without commercials',
            genre: 'Jazz',
            provider: 'sirius',
            streamUrl: 'satellite://sirius/realjazz',
            quality: 'hd',
            bitrate: '256kbps',
            isEncrypted: true,
            subscriptionRequired: true,
            emergencyBroadcast: false,
            coverage: {
              regions: ['north_america', 'canada'],
              satellites: ['SXM-7', 'SXM-8']
            }
          }
        ]
      },
      {
        id: 'global_satellite',
        name: 'Global Satellite Network',
        description: 'Free satellite radio for remote areas',
        subscriptionRequired: false,
        coverage: 'global',
        emergencyCapable: true,
        channels: [
          {
            id: 'global_news',
            number: 901,
            name: 'Global News Network',
            description: 'International news and current events',
            genre: 'News',
            provider: 'global',
            streamUrl: 'satellite://global/news',
            quality: 'standard',
            bitrate: '128kbps',
            isEncrypted: false,
            subscriptionRequired: false,
            emergencyBroadcast: true,
            coverage: {
              regions: ['global', 'oceanic', 'polar'],
              satellites: ['GlobalSat-1', 'GlobalSat-2', 'GlobalSat-3']
            }
          },
          {
            id: 'global_world_music',
            number: 902,
            name: 'World Music Satellite',
            description: 'Music from around the globe',
            genre: 'World',
            provider: 'global',
            streamUrl: 'satellite://global/worldmusic',
            quality: 'standard',
            bitrate: '192kbps',
            isEncrypted: false,
            subscriptionRequired: false,
            emergencyBroadcast: false,
            coverage: {
              regions: ['global', 'remote_areas'],
              satellites: ['GlobalSat-1', 'GlobalSat-2']
            }
          }
        ]
      },
      {
        id: 'emergency_broadcast',
        name: 'Emergency Satellite Network',
        description: 'Emergency broadcasting for disaster areas',
        subscriptionRequired: false,
        coverage: 'global',
        emergencyCapable: true,
        channels: [
          {
            id: 'emergency_alert',
            number: 911,
            name: 'Emergency Alert System',
            description: 'Emergency alerts and disaster information',
            genre: 'Emergency',
            provider: 'emergency',
            streamUrl: 'satellite://emergency/alerts',
            quality: 'standard',
            bitrate: '64kbps',
            isEncrypted: false,
            subscriptionRequired: false,
            emergencyBroadcast: true,
            coverage: {
              regions: ['global', 'disaster_zones', 'remote_areas'],
              satellites: ['EmergencySat-1', 'EmergencySat-2']
            }
          }
        ]
      }
    ];
  }

  private async loadEmergencyChannels(): Promise<void> {
    this.emergencyChannels = this.providers
      .flatMap(provider => provider.channels)
      .filter(channel => channel.emergencyBroadcast);
    
    console.log(`🚨 Loaded ${this.emergencyChannels.length} emergency channels`);
  }

  async checkSatelliteAvailability(): Promise<SatelliteConnection | null> {
    console.log('🛰️ Checking satellite availability...');
    
    try {
      // Simulate satellite connection check
      // In real implementation, this would check for actual satellite hardware/connection
      
      const mockConnection: SatelliteConnection = {
        isConnected: true,
        signalStrength: 85,
        provider: 'Global Satellite Network',
        satelliteName: 'GlobalSat-1',
        lastUpdate: Date.now()
      };
      
      this.connection = mockConnection;
      
      // Save connection status
      await AsyncStorage.setItem('satellite_connection', JSON.stringify(mockConnection));
      
      console.log('✅ Satellite connection established:', mockConnection.signalStrength + '% strength');
      return mockConnection;
      
    } catch (error) {
      console.error('❌ Satellite connection failed:', error);
      this.connection = null;
      return null;
    }
  }

  async connectToSatellite(coordinates?: [number, number]): Promise<boolean> {
    console.log('🛰️ Attempting satellite connection...');
    
    if (coordinates) {
      console.log(`📍 Using coordinates: ${coordinates[0]}, ${coordinates[1]}`);
    }
    
    try {
      // Simulate connection process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const connection = await this.checkSatelliteAvailability();
      
      if (connection) {
        if (coordinates) {
          connection.coordinates = coordinates;
          this.connection = connection;
        }
        return true;
      }
      
      return false;
      
    } catch (error) {
      console.error('❌ Failed to connect to satellite:', error);
      return false;
    }
  }

  getAvailableChannels(includeSubscription = true): SatelliteChannel[] {
    const allChannels = this.providers.flatMap(provider => provider.channels);
    
    if (includeSubscription) {
      return allChannels;
    }
    
    // Return only free channels
    return allChannels.filter(channel => !channel.subscriptionRequired);
  }

  getChannelsByProvider(providerId: string): SatelliteChannel[] {
    const provider = this.providers.find(p => p.id === providerId);
    return provider ? provider.channels : [];
  }

  getEmergencyChannels(): SatelliteChannel[] {
    return this.emergencyChannels;
  }

  getChannelByNumber(number: number): SatelliteChannel | null {
    const allChannels = this.providers.flatMap(provider => provider.channels);
    return allChannels.find(channel => channel.number === number) || null;
  }

  async tuneTo(channel: SatelliteChannel): Promise<boolean> {
    if (!this.connection || !this.connection.isConnected) {
      console.error('❌ No satellite connection available');
      return false;
    }
    
    console.log(`📻 Tuning to channel ${channel.number}: ${channel.name}`);
    
    try {
      // In real implementation, this would communicate with satellite hardware
      // For now, simulate the tuning process
      
      if (channel.subscriptionRequired && !this.hasValidSubscription(channel.provider)) {
        console.error('❌ Subscription required for this channel');
        return false;
      }
      
      console.log(`✅ Now playing: ${channel.name} - ${channel.description}`);
      return true;
      
    } catch (error) {
      console.error('❌ Failed to tune to channel:', error);
      return false;
    }
  }

  getSatelliteConnection(): SatelliteConnection | null {
    return this.connection;
  }

  getProviders(): SatelliteProvider[] {
    return this.providers;
  }

  getCoverageForLocation(latitude: number, longitude: number): SatelliteChannel[] {
    // Determine region based on coordinates
    const region = this.determineRegionFromCoordinates(latitude, longitude);
    
    const availableChannels = this.getAvailableChannels(false) // Free channels only for demo
      .filter(channel => 
        channel.coverage.regions.includes(region) || 
        channel.coverage.regions.includes('global')
      );
    
    console.log(`🗺️ Found ${availableChannels.length} satellite channels for region: ${region}`);
    return availableChannels;
  }

  private hasValidSubscription(provider: 'sirius' | 'xm' | 'global' | 'emergency'): boolean {
    // In real implementation, check subscription status
    // For demo, return true for global/emergency, false for paid services
    return provider === 'global' || provider === 'emergency';
  }

  private determineRegionFromCoordinates(lat: number, lng: number): string {
    // Same logic as SoundCast service for consistency
    if (lat >= 14 && lat <= 84 && lng >= -168 && lng <= -52) {
      return 'north_america';
    }
    
    if (lat >= -56 && lat <= 14 && lng >= -82 && lng <= -34) {
      return 'south_america';
    }
    
    if (lat >= 10 && lat <= 27 && lng >= -85 && lng <= -55) {
      return 'caribbean';
    }
    
    // Remote/oceanic areas where satellite is most valuable
    if (lat > 84 || lat < -56) {
      return 'polar';
    }
    
    if ((lng >= -180 && lng <= -168) || (lng >= 160 && lng <= 180)) {
      return 'oceanic';
    }
    
    return 'global';
  }

  async enableEmergencyMode(): Promise<void> {
    console.log('🚨 Enabling emergency satellite mode...');
    
    try {
      // Prioritize emergency channels
      await AsyncStorage.setItem('emergency_mode', 'true');
      console.log('✅ Emergency mode enabled - prioritizing emergency broadcasts');
    } catch (error) {
      console.error('❌ Failed to enable emergency mode:', error);
    }
  }

  async disableEmergencyMode(): Promise<void> {
    console.log('🔄 Disabling emergency satellite mode...');
    
    try {
      await AsyncStorage.removeItem('emergency_mode');
      console.log('✅ Emergency mode disabled');
    } catch (error) {
      console.error('❌ Failed to disable emergency mode:', error);
    }
  }

  async isEmergencyModeEnabled(): Promise<boolean> {
    try {
      const emergencyMode = await AsyncStorage.getItem('emergency_mode');
      return emergencyMode === 'true';
    } catch (error) {
      return false;
    }
  }
}

// Export singleton instance
export const satelliteRadioService = SatelliteRadioService.getInstance();