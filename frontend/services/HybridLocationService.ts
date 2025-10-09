import * as Location from 'expo-location';
import { Platform } from 'react-native';
import WebCompatibleStorage from '../utils/WebCompatibleStorage';

interface LocationCoords {
  latitude: number;
  longitude: number;
  accuracy?: number;
  altitude?: number;
  altitudeAccuracy?: number;
  heading?: number;
  speed?: number;
}

interface LocationData {
  coords: LocationCoords;
  timestamp: number;
}

interface LocationInfo {
  city: string;
  region: string;
  country: string;
  country_code?: string;
  timezone?: string;
  formatted_address?: string;
  accuracy: 'gps' | 'gps_enhanced' | 'city' | 'region' | 'fallback';
  source: 'hybrid_gps_ip' | 'ip_geolocation' | 'gps_only' | 'fallback';
  provider?: string;
  gps_available?: boolean;
}

interface LocationSuggestions {
  country: string;
  city: string;
  radio_suggestions: string[];
  language_suggestions: string[];
}

interface HybridLocationState {
  location: LocationData | null;
  locationInfo: LocationInfo | null;
  ipLocation: LocationInfo | null;
  suggestions: LocationSuggestions | null;
  loading: boolean;
  error: string | null;
  gpsPermissionGranted: boolean;
  lastUpdateTime: number;
}

/**
 * Hybrid Location Service
 * 
 * Combines client-side GPS geolocation with server-side IP-based geolocation
 * following best practices:
 * 1. IP-based geolocation as immediate default (no permission required)
 * 2. GPS enhancement when permission granted (high accuracy)
 * 3. Graceful fallback mechanisms
 * 4. Clear user experience without blocking
 */
class HybridLocationService {
  private state: HybridLocationState = {
    location: null,
    locationInfo: null,
    ipLocation: null,
    suggestions: null,
    loading: false,
    error: null,
    gpsPermissionGranted: false,
    lastUpdateTime: 0
  };

  private listeners: Set<(state: HybridLocationState) => void> = new Set();
  private backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || '';
  private watchSubscription: Location.LocationSubscription | null = null;

  constructor() {
    this.initializeHybridLocation();
  }

  /**
   * Web-compatible storage helper methods
   */
  private async getStorageItem(key: string): Promise<string | null> {
    return await WebCompatibleStorage.getItem(key);
  }

  private async setStorageItem(key: string, value: string): Promise<void> {
    await WebCompatibleStorage.setItem(key, value);
  }

  /**
   * Initialize hybrid location service
   * Step 1: Get IP location immediately (no permission required)
   * Step 2: Try to get GPS location if possible (requires permission)
   */
  private async initializeHybridLocation(): Promise<void> {
    try {
      console.log('🌍 Initializing Hybrid Location Service...');
      this.setState({ loading: true, error: null });

      // Step 1: Get IP-based location immediately (no permission needed)
      await this.getIPLocation();

      // Step 2: Try to enhance with GPS (permission-based)
      if (Platform.OS !== 'web') {
        await this.enhanceWithGPS();
      }

      console.log('✅ Hybrid Location Service initialized');
    } catch (error) {
      console.error('❌ Error initializing Hybrid Location Service:', error);
      this.setState({ error: error instanceof Error ? error.message : 'Location initialization failed' });
    } finally {
      this.setState({ loading: false });
    }
  }

  /**
   * Get IP-based location (immediate, no permission required)
   */
  async getIPLocation(): Promise<LocationInfo | null> {
    try {
      console.log('📍 Getting IP-based location...');

      // Check cache first (with web compatibility)
      const cachedIpLocation = await this.getStorageItem('cached_ip_location');
      if (cachedIpLocation) {
        const { location, timestamp } = JSON.parse(cachedIpLocation);
        if (Date.now() - timestamp < 3600000) { // 1 hour cache
          console.log('📍 Using cached IP location');
          this.setState({ ipLocation: location });
          return location;
        }
      }

      // Get IP location from backend
      const response = await fetch(`${this.backendUrl}/api/geolocation/ip`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        const ipLocation: LocationInfo = data.location;
        
        console.log(`✅ IP location: ${ipLocation.city}, ${ipLocation.country} (${ipLocation.accuracy})`);
        
        // Cache IP location (with web compatibility)
        await this.setStorageItem('cached_ip_location', JSON.stringify({
          location: ipLocation,
          timestamp: Date.now()
        }));

        // Also get location suggestions
        await this.getLocationSuggestions();

        this.setState({ 
          ipLocation,
          locationInfo: ipLocation // Use as primary until GPS is available
        });
        
        return ipLocation;
      } else {
        throw new Error('Failed to get IP location');
      }
    } catch (error) {
      console.error('❌ Error getting IP location:', error);
      
      // Use system fallback
      const fallbackLocation: LocationInfo = {
        city: 'New York',
        region: 'New York',
        country: 'United States',
        country_code: 'US',
        accuracy: 'fallback',
        source: 'fallback'
      };
      
      this.setState({ ipLocation: fallbackLocation, locationInfo: fallbackLocation });
      return fallbackLocation;
    }
  }

  /**
   * Enhance with GPS location (high accuracy, requires permission)
   */
  async enhanceWithGPS(): Promise<LocationData | null> {
    try {
      console.log('📱 Attempting GPS enhancement...');

      // Check permission
      const hasPermission = await this.requestGPSPermission();
      if (!hasPermission) {
        console.log('📍 GPS permission denied, using IP location only');
        return null;
      }

      // Get GPS location
      const gpsLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        timeout: 10000,
        maximumAge: 60000, // Accept 1-minute old location
      });

      console.log(`📱 GPS location acquired: ${gpsLocation.coords.latitude}, ${gpsLocation.coords.longitude}`);

      // Send GPS data to backend for hybrid processing
      const hybridLocation = await this.getHybridLocation(gpsLocation);

      this.setState({ 
        location: gpsLocation,
        locationInfo: hybridLocation,
        gpsPermissionGranted: true,
        lastUpdateTime: Date.now()
      });

      // Cache the GPS location (with web compatibility)
      await this.setStorageItem('cached_gps_location', JSON.stringify({
        location: gpsLocation,
        locationInfo: hybridLocation,
        timestamp: Date.now()
      }));

      return gpsLocation;
    } catch (error) {
      console.error('❌ GPS enhancement failed:', error);
      // Continue with IP location only
      return null;
    }
  }

  /**
   * Request GPS permission with user-friendly approach
   */
  private async requestGPSPermission(): Promise<boolean> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('❌ Error requesting GPS permission:', error);
      return false;
    }
  }

  /**
   * Get hybrid location (combine IP + GPS via backend)
   */
  async getHybridLocation(gpsData: LocationData): Promise<LocationInfo> {
    try {
      const response = await fetch(`${this.backendUrl}/api/geolocation/hybrid`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gps_data: {
            latitude: gpsData.coords.latitude,
            longitude: gpsData.coords.longitude,
            accuracy: gpsData.coords.accuracy
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        const hybridLocation: LocationInfo = data.location;
        const suggestions: LocationSuggestions = data.suggestions;
        
        this.setState({ suggestions });
        
        console.log(`✅ Hybrid location: ${hybridLocation.city}, ${hybridLocation.country} (${hybridLocation.accuracy})`);
        return hybridLocation;
      } else {
        throw new Error('Failed to get hybrid location');
      }
    } catch (error) {
      console.error('❌ Error getting hybrid location:', error);
      // Return IP location as fallback
      return this.state.ipLocation || this.createFallbackLocation();
    }
  }

  /**
   * Get location-based suggestions for radio stations
   */
  async getLocationSuggestions(): Promise<LocationSuggestions | null> {
    try {
      const response = await fetch(`${this.backendUrl}/api/geolocation/suggestions?context=radio`);
      
      if (response.ok) {
        const data = await response.json();
        const suggestions: LocationSuggestions = data.suggestions;
        
        console.log(`✅ Location suggestions: ${suggestions.radio_suggestions?.length || 0} radio, ${suggestions.language_suggestions?.length || 0} language`);
        
        this.setState({ suggestions });
        return suggestions;
      }
    } catch (error) {
      console.error('❌ Error getting location suggestions:', error);
    }
    return null;
  }

  /**
   * Force refresh location (both IP and GPS)
   */
  async refreshLocation(): Promise<void> {
    try {
      this.setState({ loading: true, error: null });

      // Refresh IP location
      await this.getIPLocation();

      // Refresh GPS if permission granted
      if (this.state.gpsPermissionGranted || Platform.OS === 'web') {
        await this.enhanceWithGPS();
      }

      console.log('✅ Location refreshed successfully');
    } catch (error) {
      console.error('❌ Error refreshing location:', error);
      this.setState({ error: error instanceof Error ? error.message : 'Refresh failed' });
    } finally {
      this.setState({ loading: false, lastUpdateTime: Date.now() });
    }
  }

  /**
   * Start watching location changes (GPS only)
   */
  async startWatchingLocation(): Promise<boolean> {
    try {
      if (this.watchSubscription) {
        return true; // Already watching
      }

      if (!this.state.gpsPermissionGranted) {
        const hasPermission = await this.requestGPSPermission();
        if (!hasPermission) {
          console.log('📍 GPS permission required for location watching');
          return false;
        }
      }

      this.watchSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.Balanced,
          timeInterval: 60000, // Update every minute
          distanceInterval: 500, // Update when moved 500m
        },
        async (newLocation) => {
          console.log('📱 GPS location updated');
          const hybridLocation = await this.getHybridLocation(newLocation);
          
          this.setState({
            location: newLocation,
            locationInfo: hybridLocation,
            lastUpdateTime: Date.now()
          });
        }
      );

      console.log('✅ Started watching GPS location');
      return true;
    } catch (error) {
      console.error('❌ Error starting location watching:', error);
      return false;
    }
  }

  /**
   * Stop watching location changes
   */
  stopWatchingLocation(): void {
    if (this.watchSubscription) {
      this.watchSubscription.remove();
      this.watchSubscription = null;
      console.log('✅ Stopped watching GPS location');
    }
  }

  /**
   * Get current best available location
   */
  getBestLocation(): LocationInfo {
    // Prefer GPS-enhanced location, fallback to IP location
    return this.state.locationInfo || this.state.ipLocation || this.createFallbackLocation();
  }

  /**
   * Get location for radio station suggestions
   */
  getRadioLocationContext(): {
    country: string;
    city: string;
    suggestions: string[];
  } {
    const location = this.getBestLocation();
    const suggestions = this.state.suggestions;

    return {
      country: location.country,
      city: location.city,
      suggestions: suggestions?.radio_suggestions || []
    };
  }

  /**
   * Check if high accuracy GPS is available
   */
  isGPSAvailable(): boolean {
    return this.state.gpsPermissionGranted && this.state.location !== null;
  }

  /**
   * Get location accuracy level
   */
  getAccuracyLevel(): 'high' | 'medium' | 'low' {
    const location = this.getBestLocation();
    
    if (location.accuracy === 'gps' || location.accuracy === 'gps_enhanced') {
      return 'high';
    } else if (location.accuracy === 'city') {
      return 'medium';
    } else {
      return 'low';
    }
  }

  /**
   * Create fallback location
   */
  private createFallbackLocation(): LocationInfo {
    return {
      city: 'New York',
      region: 'New York',
      country: 'United States',
      country_code: 'US',
      accuracy: 'fallback',
      source: 'fallback'
    };
  }

  // State management
  private setState(updates: Partial<HybridLocationState>): void {
    this.state = { ...this.state, ...updates };
    this.notifyListeners();
  }

  getState(): HybridLocationState {
    return { ...this.state };
  }

  addListener(callback: (state: HybridLocationState) => void): () => void {
    this.listeners.add(callback);
    callback(this.state); // Call immediately with current state
    return () => this.listeners.delete(callback);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.state);
      } catch (error) {
        console.error('❌ Hybrid Location listener error:', error);
      }
    });
  }

  // Cleanup
  cleanup(): void {
    this.stopWatchingLocation();
    this.listeners.clear();
    console.log('🧹 Hybrid Location Service cleaned up');
  }
}

// Export singleton instance
export const hybridLocationService = new HybridLocationService();
export default hybridLocationService;

// Export types for use in components
export type { 
  LocationInfo, 
  LocationData, 
  LocationSuggestions, 
  HybridLocationState 
};