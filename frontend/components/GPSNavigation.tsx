import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  ActivityIndicator,
  Alert,
  Dimensions,
  TextInput,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width, height } = Dimensions.get('window');

interface NavigationWaypoint {
  id: string;
  name: string;
  address: string;
  coordinates: [number, number]; // [lat, lng]
  type: 'destination' | 'waypoint';
  estimatedTime?: number; // minutes
  distance?: number; // meters
}

interface NavigationRoute {
  id: string;
  name: string;
  destination: NavigationWaypoint;
  waypoints: NavigationWaypoint[];
  totalDistance: number;
  totalTime: number;
  isOffline: boolean;
}

interface NavigationStep {
  id: string;
  instruction: string;
  distance: number;
  direction: string;
  streetName: string;
  icon: string;
}

interface GPSNavigationProps {
  visible: boolean;
  onClose: () => void;
  currentLocation?: [number, number];
  offlineMode?: boolean;
}

export const GPSNavigation: React.FC<GPSNavigationProps> = ({
  visible,
  onClose,
  currentLocation = [-1.286389, 36.817223], // Default: Nairobi
  offlineMode = false,
}) => {
  const { colors, isDark } = useTheme();
  
  // State
  const [routes, setRoutes] = useState<NavigationRoute[]>([]);
  const [activeRoute, setActiveRoute] = useState<NavigationRoute | null>(null);
  const [navigationSteps, setNavigationSteps] = useState<NavigationStep[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isNavigating, setIsNavigating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<NavigationWaypoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentView, setCurrentView] = useState<'map' | 'search' | 'route' | 'navigate'>('map');
  const [gpsAccuracy, setGpsAccuracy] = useState(95);
  const [offlineMapsDownloaded, setOfflineMapsDownloaded] = useState(false);
  const [savedLocations, setSavedLocations] = useState<NavigationWaypoint[]>([]);
  
  // Popular destinations (for offline use)
  const popularDestinations: NavigationWaypoint[] = [
    {
      id: 'dest_001',
      name: 'KICC (Kenyatta International Convention Centre)',
      address: 'City Square, Nairobi, Kenya',
      coordinates: [-1.2884, 36.8233],
      type: 'destination',
      estimatedTime: 15,
      distance: 5200
    },
    {
      id: 'dest_002',
      name: 'Jomo Kenyatta International Airport',
      address: 'Airport North Rd, Nairobi, Kenya',
      coordinates: [-1.3192, 36.9278],
      type: 'destination',
      estimatedTime: 45,
      distance: 18500
    },
    {
      id: 'dest_003',
      name: 'University of Nairobi',
      address: 'University Way, Nairobi, Kenya',
      coordinates: [-1.2797, 36.8153],
      type: 'destination',
      estimatedTime: 12,
      distance: 3800
    },
    {
      id: 'dest_004',
      name: 'Westgate Shopping Mall',
      address: 'Mwanzi Rd, Nairobi, Kenya',
      coordinates: [-1.2674, 36.8062],
      type: 'destination',
      estimatedTime: 25,
      distance: 8900
    },
    {
      id: 'dest_005',
      name: 'Nairobi National Museum',
      address: 'Museum Hill Rd, Nairobi, Kenya',
      coordinates: [-1.2741, 36.8133],
      type: 'destination',
      estimatedTime: 18,
      distance: 6200
    }
  ];

  useEffect(() => {
    if (visible) {
      initializeNavigation();
    }
  }, [visible]);

  const initializeNavigation = async () => {
    setIsLoading(true);
    try {
      console.log('🧭 Initializing GPS Navigation...');
      
      // Check offline maps availability
      const mapsDownloaded = await checkOfflineMaps();
      setOfflineMapsDownloaded(mapsDownloaded);
      
      // Load saved locations
      const saved = await loadSavedLocations();
      setSavedLocations(saved);
      
      // Load cached routes
      const cachedRoutes = await loadCachedRoutes();
      setRoutes(cachedRoutes);
      
      // Simulate GPS accuracy
      setGpsAccuracy(Math.random() * 15 + 85); // 85-100%
      
      console.log('✅ GPS Navigation initialized');
    } catch (error) {
      console.error('❌ Error initializing navigation:', error);
      Alert.alert('GPS Error', 'Failed to initialize navigation system. Some features may be limited.');
    } finally {
      setIsLoading(false);
    }
  };

  const checkOfflineMaps = async (): Promise<boolean> => {
    try {
      const mapsData = await AsyncStorage.getItem('offline_maps');
      return !!mapsData;
    } catch (error) {
      return false;
    }
  };

  const loadSavedLocations = async (): Promise<NavigationWaypoint[]> => {
    try {
      const saved = await AsyncStorage.getItem('saved_locations');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (error) {
      console.error('Error loading saved locations:', error);
    }
    
    // Return default saved locations
    return [
      {
        id: 'home',
        name: 'Home',
        address: 'My Home Address',
        coordinates: currentLocation,
        type: 'destination'
      },
      {
        id: 'work',
        name: 'Work',
        address: 'My Work Address',
        coordinates: [-1.2921, 36.8219],
        type: 'destination'
      }
    ];
  };

  const loadCachedRoutes = async (): Promise<NavigationRoute[]> => {
    try {
      const cached = await AsyncStorage.getItem('navigation_routes');
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (error) {
      console.error('Error loading cached routes:', error);
    }
    
    return [];
  };

  const searchForLocation = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    try {
      // In offline mode, search only in popular destinations and saved locations
      if (offlineMode || !navigator.onLine) {
        const allLocations = [...popularDestinations, ...savedLocations];
        const results = allLocations.filter(location =>
          location.name.toLowerCase().includes(query.toLowerCase()) ||
          location.address.toLowerCase().includes(query.toLowerCase())
        );
        setSearchResults(results);
      } else {
        // Online search (simulated)
        const results = popularDestinations.filter(location =>
          location.name.toLowerCase().includes(query.toLowerCase()) ||
          location.address.toLowerCase().includes(query.toLowerCase())
        );
        setSearchResults(results);
      }
      
      setCurrentView('search');
    } catch (error) {
      console.error('Search error:', error);
      Alert.alert('Search Error', 'Failed to search for locations');
    } finally {
      setIsLoading(false);
    }
  };

  const calculateRoute = async (destination: NavigationWaypoint) => {
    setIsLoading(true);
    try {
      console.log('🗺️ Calculating route to:', destination.name);
      
      // Calculate distance and time (simplified)
      const distance = calculateDistance(
        currentLocation[0], currentLocation[1],
        destination.coordinates[0], destination.coordinates[1]
      );
      
      const estimatedTime = Math.ceil(distance / 40); // Assume 40 km/h average speed
      
      // Generate navigation steps
      const steps = generateNavigationSteps(currentLocation, destination.coordinates, destination.name);
      setNavigationSteps(steps);
      
      // Create route
      const route: NavigationRoute = {
        id: `route_${Date.now()}`,
        name: `Route to ${destination.name}`,
        destination,
        waypoints: [],
        totalDistance: distance * 1000, // Convert to meters
        totalTime: estimatedTime,
        isOffline: offlineMode
      };
      
      setActiveRoute(route);
      setCurrentView('route');
      
      console.log('✅ Route calculated:', route.totalDistance, 'meters', route.totalTime, 'minutes');
    } catch (error) {
      console.error('Route calculation error:', error);
      Alert.alert('Route Error', 'Failed to calculate route');
    } finally {
      setIsLoading(false);
    }
  };

  const startNavigation = () => {
    if (!activeRoute) return;
    
    setIsNavigating(true);
    setCurrentStep(0);
    setCurrentView('navigate');
    
    Alert.alert(
      'Navigation Started',
      `Navigate to ${activeRoute.destination.name}?\n\nDistance: ${(activeRoute.totalDistance / 1000).toFixed(1)} km\nEstimated time: ${activeRoute.totalTime} minutes`,
      [
        { text: 'Cancel', style: 'cancel', onPress: () => setIsNavigating(false) },
        { text: 'Start', onPress: () => console.log('🧭 Navigation started') }
      ]
    );
  };

  const stopNavigation = () => {
    setIsNavigating(false);
    setCurrentStep(0);
    setCurrentView('map');
    Alert.alert('Navigation Stopped', 'Navigation has been stopped');
  };

  const nextStep = () => {
    if (currentStep < navigationSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Arrived at destination
      setIsNavigating(false);
      Alert.alert('Destination Reached', 'You have arrived at your destination!');
      setCurrentView('map');
    }
  };

  const saveCurrentLocation = async (name: string) => {
    const newLocation: NavigationWaypoint = {
      id: `saved_${Date.now()}`,
      name,
      address: 'Current Location',
      coordinates: currentLocation,
      type: 'destination'
    };
    
    const updatedLocations = [...savedLocations, newLocation];
    setSavedLocations(updatedLocations);
    
    try {
      await AsyncStorage.setItem('saved_locations', JSON.stringify(updatedLocations));
      Alert.alert('Location Saved', `"${name}" has been saved to your locations`);
    } catch (error) {
      Alert.alert('Save Error', 'Failed to save location');
    }
  };

  // Helper functions
  const calculateDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  const generateNavigationSteps = (start: [number, number], end: [number, number], destinationName: string): NavigationStep[] => {
    // Simplified step generation
    const distance = calculateDistance(start[0], start[1], end[0], end[1]) * 1000;
    
    return [
      {
        id: 'step_001',
        instruction: 'Head north on current road',
        distance: Math.round(distance * 0.3),
        direction: 'north',
        streetName: 'Current Road',
        icon: 'arrow-up'
      },
      {
        id: 'step_002', 
        instruction: 'Turn right onto Main Street',
        distance: Math.round(distance * 0.4),
        direction: 'right',
        streetName: 'Main Street',
        icon: 'arrow-forward'
      },
      {
        id: 'step_003',
        instruction: 'Continue straight for 2.5 km',
        distance: Math.round(distance * 0.2),
        direction: 'straight',
        streetName: 'Main Street',
        icon: 'arrow-up'
      },
      {
        id: 'step_004',
        instruction: `Destination will be on your right: ${destinationName}`,
        distance: Math.round(distance * 0.1),
        direction: 'destination',
        streetName: destinationName,
        icon: 'location'
      }
    ];
  };

  // Render functions
  const renderMapView = () => (
    <View style={styles.mapContainer}>
      <View style={styles.mapHeader}>
        <Text style={[styles.mapTitle, { color: colors.text }]}>GPS Navigation</Text>
        <View style={styles.gpsStatus}>
          <Ionicons
            name={gpsAccuracy > 90 ? 'location' : 'location-outline'}
            size={16}
            color={gpsAccuracy > 90 ? '#4CAF50' : colors.primary}
          />
          <Text style={[styles.gpsText, { color: colors.textSecondary }]}>
            GPS: {gpsAccuracy.toFixed(0)}%
          </Text>
        </View>
      </View>

      {/* Simulated Map */}
      <View style={styles.mapView}>
        <Text style={[styles.mapPlaceholder, { color: colors.textSecondary }]}>
          🗺️ Interactive Map View
        </Text>
        <Text style={[styles.currentLocationText, { color: colors.text }]}>
          📍 Current Location: Nairobi, Kenya
        </Text>
        
        {offlineMode && (
          <View style={styles.offlineIndicator}>
            <Ionicons name="cloud-offline" size={20} color={colors.error} />
            <Text style={[styles.offlineText, { color: colors.error }]}>
              Offline Mode - {offlineMapsDownloaded ? 'Maps Available' : 'Limited Maps'}
            </Text>
          </View>
        )}
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Popular Destinations</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {popularDestinations.slice(0, 4).map((destination) => (
            <TouchableOpacity
              key={destination.id}
              style={[styles.destinationCard, { backgroundColor: colors.card }]}
              onPress={() => calculateRoute(destination)}
            >
              <Text style={[styles.destinationName, { color: colors.text }]}>
                {destination.name}
              </Text>
              <Text style={[styles.destinationDistance, { color: colors.textSecondary }]}>
                {destination.distance ? `${(destination.distance / 1000).toFixed(1)} km` : 'Calculate route'}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Saved Locations */}
      {savedLocations.length > 0 && (
        <View style={styles.savedLocations}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Saved Locations</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {savedLocations.map((location) => (
              <TouchableOpacity
                key={location.id}
                style={[styles.savedLocationCard, { backgroundColor: colors.surface }]}
                onPress={() => calculateRoute(location)}
              >
                <Ionicons name="bookmark" size={16} color={colors.primary} />
                <Text style={[styles.savedLocationName, { color: colors.text }]}>
                  {location.name}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );

  const renderSearchView = () => (
    <View style={styles.searchContainer}>
      <Text style={[styles.searchTitle, { color: colors.text }]}>Search Results</Text>
      <Text style={[styles.searchSubtitle, { color: colors.textSecondary }]}>
        {searchResults.length} locations found for "{searchQuery}"
      </Text>
      
      <ScrollView style={styles.searchResults}>
        {searchResults.map((location) => (
          <TouchableOpacity
            key={location.id}
            style={[styles.locationCard, { backgroundColor: colors.card }]}
            onPress={() => calculateRoute(location)}
          >
            <View style={styles.locationInfo}>
              <Text style={[styles.locationName, { color: colors.text }]}>
                {location.name}
              </Text>
              <Text style={[styles.locationAddress, { color: colors.textSecondary }]}>
                {location.address}
              </Text>
              {location.distance && (
                <Text style={[styles.locationDistance, { color: colors.primary }]}>
                  {(location.distance / 1000).toFixed(1)} km away
                </Text>
              )}
            </View>
            <Ionicons name="navigate" size={24} color={colors.primary} />
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  const renderRouteView = () => (
    <View style={styles.routeContainer}>
      {activeRoute && (
        <>
          <View style={styles.routeHeader}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => setCurrentView('map')}
            >
              <Ionicons name="arrow-back" size={24} color={colors.text} />
            </TouchableOpacity>
            <View style={styles.routeInfo}>
              <Text style={[styles.routeTitle, { color: colors.text }]}>
                Route to {activeRoute.destination.name}
              </Text>
              <Text style={[styles.routeStats, { color: colors.textSecondary }]}>
                {(activeRoute.totalDistance / 1000).toFixed(1)} km • {activeRoute.totalTime} min
              </Text>
            </View>
          </View>

          <View style={styles.routeActions}>
            <TouchableOpacity
              style={[styles.startButton, { backgroundColor: colors.primary }]}
              onPress={startNavigation}
            >
              <Ionicons name="navigate" size={20} color="#fff" />
              <Text style={styles.startButtonText}>Start Navigation</Text>
            </TouchableOpacity>
          </View>

          {/* Route Steps */}
          <ScrollView style={styles.routeSteps}>
            <Text style={[styles.stepsTitle, { color: colors.text }]}>Route Details</Text>
            {navigationSteps.map((step, index) => (
              <View key={step.id} style={[styles.stepCard, { backgroundColor: colors.card }]}>
                <View style={styles.stepIcon}>
                  <Ionicons name={step.icon as any} size={20} color={colors.primary} />
                </View>
                <View style={styles.stepInfo}>
                  <Text style={[styles.stepInstruction, { color: colors.text }]}>
                    {step.instruction}
                  </Text>
                  <Text style={[styles.stepDistance, { color: colors.textSecondary }]}>
                    {step.distance}m • {step.streetName}
                  </Text>
                </View>
              </View>
            ))}
          </ScrollView>
        </>
      )}
    </View>
  );

  const renderNavigationView = () => (
    <View style={styles.navigationContainer}>
      {navigationSteps[currentStep] && (
        <>
          <View style={styles.navigationHeader}>
            <TouchableOpacity style={styles.stopButton} onPress={stopNavigation}>
              <Ionicons name="stop" size={24} color={colors.error} />
            </TouchableOpacity>
            <Text style={[styles.navigationTitle, { color: colors.text }]}>
              Navigation
            </Text>
            <View style={styles.stepCounter}>
              <Text style={[styles.stepCounterText, { color: colors.textSecondary }]}>
                {currentStep + 1}/{navigationSteps.length}
              </Text>
            </View>
          </View>

          <View style={styles.currentInstruction}>
            <View style={styles.instructionIcon}>
              <Ionicons
                name={navigationSteps[currentStep].icon as any}
                size={48}
                color={colors.primary}
              />
            </View>
            <Text style={[styles.instructionText, { color: colors.text }]}>
              {navigationSteps[currentStep].instruction}
            </Text>
            <Text style={[styles.instructionDistance, { color: colors.textSecondary }]}>
              In {navigationSteps[currentStep].distance}m
            </Text>
          </View>

          <View style={styles.navigationControls}>
            <TouchableOpacity
              style={[styles.nextStepButton, { backgroundColor: colors.primary }]}
              onPress={nextStep}
            >
              <Text style={styles.nextStepText}>Next Step</Text>
              <Ionicons name="arrow-forward" size={20} color="#fff" />
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
  );

  const styles = StyleSheet.create({
    modalOverlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.8)',
      justifyContent: 'center',
    },
    container: {
      backgroundColor: colors.background,
      margin: 10,
      borderRadius: 16,
      maxHeight: height * 0.9,
      flex: 1,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
    },
    closeButton: {
      padding: 8,
    },
    searchContainer: {
      flexDirection: 'row',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    searchInput: {
      flex: 1,
      height: 44,
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 8,
      paddingHorizontal: 16,
      backgroundColor: colors.surface,
      color: colors.text,
      marginRight: 8,
    },
    searchButton: {
      width: 44,
      height: 44,
      borderRadius: 8,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    mapContainer: {
      flex: 1,
      padding: 16,
    },
    mapHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 16,
    },
    mapTitle: {
      fontSize: 18,
      fontWeight: '600',
    },
    gpsStatus: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 4,
    },
    gpsText: {
      fontSize: 12,
    },
    mapView: {
      height: 200,
      backgroundColor: colors.surface,
      borderRadius: 12,
      padding: 20,
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: 20,
    },
    mapPlaceholder: {
      fontSize: 24,
      marginBottom: 8,
    },
    currentLocationText: {
      fontSize: 14,
      textAlign: 'center',
    },
    offlineIndicator: {
      flexDirection: 'row',
      alignItems: 'center',
      marginTop: 12,
      gap: 8,
    },
    offlineText: {
      fontSize: 12,
    },
    quickActions: {
      marginBottom: 20,
    },
    savedLocations: {
      marginBottom: 20,
    },
    sectionTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 12,
    },
    destinationCard: {
      width: 140,
      padding: 12,
      borderRadius: 8,
      marginRight: 12,
    },
    destinationName: {
      fontSize: 14,
      fontWeight: '600',
      marginBottom: 4,
    },
    destinationDistance: {
      fontSize: 12,
    },
    savedLocationCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 8,
      borderRadius: 8,
      marginRight: 8,
      gap: 6,
    },
    savedLocationName: {
      fontSize: 12,
    },
    searchTitle: {
      fontSize: 18,
      fontWeight: '600',
      marginBottom: 4,
    },
    searchSubtitle: {
      fontSize: 14,
      marginBottom: 16,
    },
    searchResults: {
      flex: 1,
    },
    locationCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderRadius: 8,
      marginBottom: 8,
    },
    locationInfo: {
      flex: 1,
    },
    locationName: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 4,
    },
    locationAddress: {
      fontSize: 14,
      marginBottom: 2,
    },
    locationDistance: {
      fontSize: 12,
    },
    routeContainer: {
      flex: 1,
    },
    routeHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    backButton: {
      marginRight: 16,
    },
    routeInfo: {
      flex: 1,
    },
    routeTitle: {
      fontSize: 18,
      fontWeight: '600',
    },
    routeStats: {
      fontSize: 14,
      marginTop: 2,
    },
    routeActions: {
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    startButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
      borderRadius: 8,
      gap: 8,
    },
    startButtonText: {
      fontSize: 16,
      fontWeight: '600',
      color: '#fff',
    },
    routeSteps: {
      flex: 1,
      padding: 16,
    },
    stepsTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 12,
    },
    stepCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 12,
      borderRadius: 8,
      marginBottom: 8,
    },
    stepIcon: {
      width: 40,
      alignItems: 'center',
    },
    stepInfo: {
      flex: 1,
      marginLeft: 12,
    },
    stepInstruction: {
      fontSize: 14,
      marginBottom: 2,
    },
    stepDistance: {
      fontSize: 12,
    },
    navigationContainer: {
      flex: 1,
    },
    navigationHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    stopButton: {
      padding: 8,
    },
    navigationTitle: {
      fontSize: 18,
      fontWeight: '600',
    },
    stepCounter: {},
    stepCounterText: {
      fontSize: 14,
    },
    currentInstruction: {
      alignItems: 'center',
      padding: 40,
    },
    instructionIcon: {
      marginBottom: 20,
    },
    instructionText: {
      fontSize: 20,
      fontWeight: '600',
      textAlign: 'center',
      marginBottom: 8,
    },
    instructionDistance: {
      fontSize: 16,
      textAlign: 'center',
    },
    navigationControls: {
      padding: 20,
    },
    nextStepButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
      borderRadius: 8,
      gap: 8,
    },
    nextStepText: {
      fontSize: 16,
      fontWeight: '600',
      color: '#fff',
    },
    loadingContainer: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
    },
    loadingText: {
      fontSize: 16,
      color: colors.textSecondary,
      marginTop: 16,
      textAlign: 'center',
    },
  });

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.container}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>🧭 GPS Navigation</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>

          {/* Search */}
          <View style={styles.searchContainer}>
            <TextInput
              style={styles.searchInput}
              placeholder="Search for places..."
              placeholderTextColor={colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={() => searchForLocation(searchQuery)}
            />
            <TouchableOpacity
              style={styles.searchButton}
              onPress={() => searchForLocation(searchQuery)}
            >
              <Ionicons name="search" size={20} color="#fff" />
            </TouchableOpacity>
          </View>

          {/* Loading */}
          {isLoading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={styles.loadingText}>Loading GPS data...</Text>
            </View>
          )}

          {/* Content */}
          {!isLoading && (
            <>
              {currentView === 'map' && renderMapView()}
              {currentView === 'search' && renderSearchView()}
              {currentView === 'route' && renderRouteView()}
              {currentView === 'navigate' && renderNavigationView()}
            </>
          )}
        </View>
      </View>
    </Modal>
  );
};