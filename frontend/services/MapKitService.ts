import { Platform } from 'react-native';

// MapKit interfaces
export interface PlaceDescriptor {
  id: string;
  name: string;
  coordinate: {
    latitude: number;
    longitude: number;
  };
  category: string;
  address?: string;
  phoneNumber?: string;
  website?: string;
  region?: string;
  country?: string;
}

export interface RadioStationPlace extends PlaceDescriptor {
  frequency?: string;
  genre?: string;
  broadcastRadius?: number; // in kilometers
  streamUrl?: string;
  isActive: boolean;
  stationType: 'fm' | 'am' | 'digital' | 'internet';
  networkAffiliation?: string;
}

export interface GeocodingResult {
  placemark: {
    name?: string;
    thoroughfare?: string;
    locality?: string;
    administrativeArea?: string;
    country?: string;
    postalCode?: string;
    coordinate: {
      latitude: number;
      longitude: number;
    };
  };
  formattedAddress: string;
  region: string;
}

export interface DirectionsRequest {
  origin: {
    latitude: number;
    longitude: number;
  };
  destination: PlaceDescriptor;
  transportType: 'automobile' | 'walking' | 'transit';
}

export interface DirectionsResult {
  distance: number; // in meters
  expectedTravelTime: number; // in seconds
  route: {
    coordinates: Array<{
      latitude: number;
      longitude: number;
    }>;
  };
  instructions: Array<{
    instruction: string;
    distance: number;
    coordinate: {
      latitude: number;
      longitude: number;
    };
  }>;
}

export interface LookAroundScene {
  coordinate: {
    latitude: number;
    longitude: number;
  };
  heading: number;
  pitch: number;
  isAvailable: boolean;
  previewImage?: string;
}

class MapKitService {
  private isInitialized = false;
  private radioStations: RadioStationPlace[] = [];

  constructor() {
    this.initializeMapKit();
  }

  private async initializeMapKit(): Promise<void> {
    try {
      console.log('🗺️ Initializing MapKit service...');
      
      // Load radio station data
      await this.loadRadioStations();
      
      this.isInitialized = true;
      console.log('✅ MapKit service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize MapKit service:', error);
    }
  }

  private async loadRadioStations(): Promise<void> {
    // Mock radio station data - in production, this would come from a backend API
    this.radioStations = [
      {
        id: 'kfm-nairobi',
        name: 'Capital FM Kenya',
        coordinate: { latitude: -1.2921, longitude: 36.8219 },
        category: 'Radio Station',
        address: 'Lonrho House, Standard St, Nairobi',
        phoneNumber: '+254 20 329 4000',
        website: 'https://www.capitalfm.co.ke',
        region: 'Nairobi',
        country: 'Kenya',
        frequency: '98.4 FM',
        genre: 'Contemporary Music',
        broadcastRadius: 50,
        isActive: true,
        stationType: 'fm',
        networkAffiliation: 'Kenya Radio Network'
      },
      {
        id: 'bbc-london',
        name: 'BBC Radio London',
        coordinate: { latitude: 51.5074, longitude: -0.1278 },
        category: 'Radio Station',
        address: 'Broadcasting House, Portland Pl, London',
        phoneNumber: '+44 20 7580 4468',
        website: 'https://www.bbc.co.uk/radiolondon',
        region: 'London',
        country: 'United Kingdom',
        frequency: '94.9 FM',
        genre: 'Talk & Music',
        broadcastRadius: 80,
        isActive: true,
        stationType: 'fm',
        networkAffiliation: 'BBC Network'
      },
      {
        id: 'kiis-fm-la',
        name: 'KIIS FM Los Angeles',
        coordinate: { latitude: 34.0522, longitude: -118.2437 },
        category: 'Radio Station',
        address: '3400 W Olive Ave, Burbank, CA',
        phoneNumber: '+1 818 559 2252',
        website: 'https://www.kiisfm.com',
        region: 'Los Angeles',
        country: 'United States',
        frequency: '102.7 FM',
        genre: 'Top 40/Pop',
        broadcastRadius: 100,
        isActive: true,
        stationType: 'fm',
        networkAffiliation: 'iHeartRadio'
      },
      {
        id: 'radio-france-paris',
        name: 'Radio France Paris',
        coordinate: { latitude: 48.8566, longitude: 2.3522 },
        category: 'Radio Station',
        address: '116 Avenue du Président Kennedy, Paris',
        phoneNumber: '+33 1 56 40 15 16',
        website: 'https://www.radiofrance.fr',
        region: 'Île-de-France',
        country: 'France',
        frequency: '105.5 FM',
        genre: 'Public Radio',
        broadcastRadius: 75,
        isActive: true,
        stationType: 'fm',
        networkAffiliation: 'Radio France Network'
      }
    ];
  }

  /**
   * Create PlaceDescriptor for radio stations
   */
  async createPlaceDescriptor(stationId: string): Promise<PlaceDescriptor | null> {
    try {
      const station = this.radioStations.find(s => s.id === stationId);
      if (!station) {
        console.log('📍 Radio station not found:', stationId);
        return null;
      }

      return {
        id: station.id,
        name: station.name,
        coordinate: station.coordinate,
        category: station.category,
        address: station.address,
        phoneNumber: station.phoneNumber,
        website: station.website,
        region: station.region,
        country: station.country
      };
    } catch (error) {
      console.error('❌ Failed to create place descriptor:', error);
      return null;
    }
  }

  /**
   * Enhanced geocoding with MapKit
   */
  async geocodeLocation(latitude: number, longitude: number): Promise<GeocodingResult | null> {
    try {
      console.log('🗺️ Geocoding with MapKit:', { latitude, longitude });

      // Mock MapKit geocoding - in production would use actual MapKit API
      const mockResult: GeocodingResult = {
        placemark: {
          name: 'Sample Location',
          thoroughfare: 'Main Street',
          locality: this.getLocalityFromCoordinate(latitude, longitude),
          administrativeArea: this.getRegionFromCoordinate(latitude, longitude),
          country: this.getCountryFromCoordinate(latitude, longitude),
          postalCode: '12345',
          coordinate: { latitude, longitude }
        },
        formattedAddress: `${this.getLocalityFromCoordinate(latitude, longitude)}, ${this.getCountryFromCoordinate(latitude, longitude)}`,
        region: this.getRegionFromCoordinate(latitude, longitude)
      };

      console.log('✅ MapKit geocoding successful');
      return mockResult;
    } catch (error) {
      console.error('❌ MapKit geocoding failed:', error);
      return null;
    }
  }

  /**
   * Find radio stations near a location
   */
  async findNearbyRadioStations(
    latitude: number, 
    longitude: number, 
    radius: number = 50
  ): Promise<RadioStationPlace[]> {
    try {
      console.log('📡 Finding nearby radio stations...');

      const nearbyStations = this.radioStations.filter(station => {
        const distance = this.calculateDistance(
          latitude, longitude,
          station.coordinate.latitude, station.coordinate.longitude
        );
        return distance <= radius;
      });

      // Sort by distance
      nearbyStations.sort((a, b) => {
        const distA = this.calculateDistance(latitude, longitude, a.coordinate.latitude, a.coordinate.longitude);
        const distB = this.calculateDistance(latitude, longitude, b.coordinate.latitude, b.coordinate.longitude);
        return distA - distB;
      });

      console.log(`📡 Found ${nearbyStations.length} nearby stations`);
      return nearbyStations;
    } catch (error) {
      console.error('❌ Failed to find nearby stations:', error);
      return [];
    }
  }

  /**
   * Get directions to radio station
   */
  async getDirections(request: DirectionsRequest): Promise<DirectionsResult | null> {
    try {
      console.log('🧭 Getting directions to:', request.destination.name);

      // Mock directions result - in production would use MapKit Directions API
      const distance = this.calculateDistance(
        request.origin.latitude, request.origin.longitude,
        request.destination.coordinate.latitude, request.destination.coordinate.longitude
      ) * 1000; // Convert to meters

      const mockResult: DirectionsResult = {
        distance,
        expectedTravelTime: this.estimateTravelTime(distance, request.transportType),
        route: {
          coordinates: [
            request.origin,
            {
              latitude: (request.origin.latitude + request.destination.coordinate.latitude) / 2,
              longitude: (request.origin.longitude + request.destination.coordinate.longitude) / 2
            },
            request.destination.coordinate
          ]
        },
        instructions: [
          {
            instruction: 'Head northwest',
            distance: distance * 0.3,
            coordinate: request.origin
          },
          {
            instruction: 'Continue straight',
            distance: distance * 0.4,
            coordinate: {
              latitude: (request.origin.latitude + request.destination.coordinate.latitude) / 2,
              longitude: (request.origin.longitude + request.destination.coordinate.longitude) / 2
            }
          },
          {
            instruction: `Arrive at ${request.destination.name}`,
            distance: distance * 0.3,
            coordinate: request.destination.coordinate
          }
        ]
      };

      console.log('✅ Directions calculated');
      return mockResult;
    } catch (error) {
      console.error('❌ Failed to get directions:', error);
      return null;
    }
  }

  /**
   * Get Look Around scene for radio station
   */
  async getLookAroundScene(coordinate: { latitude: number; longitude: number }): Promise<LookAroundScene | null> {
    try {
      console.log('👁️ Getting Look Around scene...');

      // Mock Look Around availability check
      const isAvailable = this.isLookAroundAvailable(coordinate);

      if (!isAvailable) {
        console.log('📍 Look Around not available at this location');
        return null;
      }

      const mockScene: LookAroundScene = {
        coordinate,
        heading: 0,
        pitch: 0,
        isAvailable: true,
        previewImage: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==' // 1x1 transparent PNG
      };

      console.log('✅ Look Around scene retrieved');
      return mockScene;
    } catch (error) {
      console.error('❌ Failed to get Look Around scene:', error);
      return null;
    }
  }

  /**
   * Search for places near radio stations
   */
  async searchNearbyPlaces(
    stationId: string, 
    category: string = 'restaurant', 
    radius: number = 1000
  ): Promise<PlaceDescriptor[]> {
    try {
      const station = this.radioStations.find(s => s.id === stationId);
      if (!station) {
        console.log('📍 Station not found for nearby search');
        return [];
      }

      console.log(`🔍 Searching for ${category} near ${station.name}...`);

      // Mock nearby places - in production would use MapKit search API
      const mockPlaces: PlaceDescriptor[] = [
        {
          id: 'place-1',
          name: `${category} near ${station.name}`,
          coordinate: {
            latitude: station.coordinate.latitude + 0.001,
            longitude: station.coordinate.longitude + 0.001
          },
          category,
          address: 'Sample Address'
        }
      ];

      console.log(`✅ Found ${mockPlaces.length} nearby places`);
      return mockPlaces;
    } catch (error) {
      console.error('❌ Failed to search nearby places:', error);
      return [];
    }
  }

  // Helper methods
  private calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Radius of Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  private estimateTravelTime(distance: number, transportType: string): number {
    // Estimate travel time in seconds based on transport type
    const speeds = {
      automobile: 50, // km/h
      walking: 5,     // km/h
      transit: 30     // km/h
    };
    
    const speed = speeds[transportType as keyof typeof speeds] || 30;
    const distanceInKm = distance / 1000;
    return (distanceInKm / speed) * 3600; // Convert to seconds
  }

  private isLookAroundAvailable(coordinate: { latitude: number; longitude: number }): boolean {
    // Mock availability - typically available in major cities
    const majorCities = [
      { lat: 37.7749, lon: -122.4194 }, // San Francisco
      { lat: 40.7128, lon: -74.0060 },  // New York
      { lat: 51.5074, lon: -0.1278 },   // London
      { lat: 48.8566, lon: 2.3522 },    // Paris
    ];

    return majorCities.some(city => 
      this.calculateDistance(coordinate.latitude, coordinate.longitude, city.lat, city.lon) < 20
    );
  }

  private getLocalityFromCoordinate(latitude: number, longitude: number): string {
    // Simple mock geocoding - in production would use actual service
    if (latitude > 40 && latitude < 41 && longitude > -75 && longitude < -73) return 'New York';
    if (latitude > 51 && latitude < 52 && longitude > -1 && longitude < 1) return 'London';
    if (latitude > -2 && latitude < 0 && longitude > 36 && longitude < 37) return 'Nairobi';
    return 'Unknown City';
  }

  private getRegionFromCoordinate(latitude: number, longitude: number): string {
    if (latitude > 40 && latitude < 41 && longitude > -75 && longitude < -73) return 'New York';
    if (latitude > 51 && latitude < 52 && longitude > -1 && longitude < 1) return 'England';
    if (latitude > -2 && latitude < 0 && longitude > 36 && longitude < 37) return 'Nairobi County';
    return 'Unknown Region';
  }

  private getCountryFromCoordinate(latitude: number, longitude: number): string {
    if (latitude > 24 && latitude < 49 && longitude > -125 && longitude < -66) return 'United States';
    if (latitude > 49 && latitude < 61 && longitude > -11 && longitude < 2) return 'United Kingdom';
    if (latitude > -5 && latitude < 5 && longitude > 33 && longitude < 42) return 'Kenya';
    if (latitude > 42 && latitude < 52 && longitude > -5 && longitude < 9) return 'France';
    return 'Unknown Country';
  }

  /**
   * Get all radio stations
   */
  getAllRadioStations(): RadioStationPlace[] {
    return [...this.radioStations];
  }

  /**
   * Get radio station by ID
   */
  getRadioStation(stationId: string): RadioStationPlace | null {
    return this.radioStations.find(s => s.id === stationId) || null;
  }

  /**
   * Check if MapKit is available on current platform
   */
  isMapKitAvailable(): boolean {
    return Platform.OS === 'ios' || Platform.OS === 'web';
  }

  /**
   * Get service status
   */
  getServiceStatus(): { initialized: boolean; stationsLoaded: number } {
    return {
      initialized: this.isInitialized,
      stationsLoaded: this.radioStations.length
    };
  }
}

// Export singleton instance
export const mapKitService = new MapKitService();
export default MapKitService;