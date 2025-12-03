import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Dimensions,
  Alert,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import MapView, { Marker, Circle, PROVIDER_DEFAULT } from 'react-native-maps';
import * as Location from 'expo-location';

const { width, height } = Dimensions.get('window');
const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Station {
  id: string;
  name: string;
  call_sign?: string;
  standard_display_name?: string;
  stream_url: string;
  country: string;
  latitude: number;
  longitude: number;
  quality_score: number;
  genre?: string;
}

interface TrafficIncident {
  id: string;
  type: number;
  severity: string;
  description: string;
  location: { lat: number; lon: number };
  delay_minutes?: number;
}

export default function RadioMapScreen() {
  const [loading, setLoading] = useState(true);
  const [stations, setStations] = useState<Station[]>([]);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);
  const [userLocation, setUserLocation] = useState<Location.LocationObject | null>(null);
  const [trafficIncidents, setTrafficIncidents] = useState<TrafficIncident[]>([]);
  const [trafficAnnouncement, setTrafficAnnouncement] = useState<string>('');
  const [showTrafficPanel, setShowTrafficPanel] = useState(false);
  const [showCoverageRadius, setShowCoverageRadius] = useState(false);
  const [mapType, setMapType] = useState<'standard' | 'satellite' | 'hybrid'>('standard');
  
  const mapRef = useRef<MapView>(null);

  useEffect(() => {
    requestLocationPermission();
    loadStations();
  }, []);

  useEffect(() => {
    if (userLocation) {
      loadTrafficData();
    }
  }, [userLocation]);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const location = await Location.getCurrentPositionAsync({});
        setUserLocation(location);
        
        // Center map on user location
        if (mapRef.current) {
          mapRef.current.animateToRegion({
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            latitudeDelta: 0.5,
            longitudeDelta: 0.5,
          });
        }
      } else {
        Alert.alert('Permission Denied', 'Location permission is required for map features');
      }
    } catch (error) {
      console.error('Location permission error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/map/stations?limit=200`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setStations(data.data.stations || []);
      }
    } catch (error) {
      console.error('Load stations error:', error);
    }
  };

  const loadTrafficData = async () => {
    if (!userLocation) return;

    try {
      const lat = userLocation.coords.latitude;
      const lon = userLocation.coords.longitude;

      // Get traffic incidents
      const incidentsResponse = await fetch(
        `${API_BASE_URL}/api/traffic/incidents?lat=${lat}&lon=${lon}&radius=20&provider=tomtom`
      );
      const incidentsData = await incidentsResponse.json();
      
      if (incidentsData.status === 'success' && incidentsData.data.incidents) {
        setTrafficIncidents(incidentsData.data.incidents);
      }

      // Get traffic announcement
      const announcementResponse = await fetch(
        `${API_BASE_URL}/api/traffic/announcement?lat=${lat}&lon=${lon}&radius=20&location_name=your%20area`,
        { method: 'POST' }
      );
      const announcementData = await announcementResponse.json();
      
      if (announcementData.status === 'success') {
        setTrafficAnnouncement(announcementData.data.announcement || '');
      }
    } catch (error) {
      console.error('Load traffic error:', error);
    }
  };

  const getIncidentIcon = (type: number) => {
    switch (type) {
      case 1: return '🚗💥'; // Accident
      case 2: return '🚧'; // Construction
      case 3: return '🛑'; // Road closure
      default: return '⚠️'; // Unknown
    }
  };

  const getIncidentColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#FF0000';
      case 'major': return '#FF6B35';
      case 'moderate': return '#FFA500';
      case 'minor': return '#FFFF00';
      default: return '#888888';
    }
  };

  const playStation = (station: Station) => {
    setSelectedStation(station);
    Alert.alert(
      'Now Playing',
      `${station.standard_display_name || station.name}\n${station.country}`,
      [
        { text: 'Close', style: 'cancel' },
        { text: 'Add to Favorites', onPress: () => console.log('Add to favorites') }
      ]
    );
  };

  const toggleMapType = () => {
    if (mapType === 'standard') {
      setMapType('satellite');
    } else if (mapType === 'satellite') {
      setMapType('hybrid');
    } else {
      setMapType('standard');
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen 
        options={{
          title: 'Radio Map & Traffic',
          headerShown: true,
          headerStyle: {
            backgroundColor: '#000000',
          },
          headerTintColor: '#FFFFFF',
        }}
      />

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FFFFFF" />
          <Text style={styles.loadingText}>Loading map...</Text>
        </View>
      ) : (
        <View style={styles.mapContainer}>
          <MapView
            ref={mapRef}
            provider={PROVIDER_DEFAULT}
            style={styles.map}
            mapType={mapType}
            showsUserLocation={true}
            showsMyLocationButton={false}
            showsTraffic={true}
            initialRegion={{
              latitude: userLocation?.coords.latitude || 0,
              longitude: userLocation?.coords.longitude || 0,
              latitudeDelta: 0.5,
              longitudeDelta: 0.5,
            }}
          >
            {/* Station Markers */}
            {stations.map((station) => (
              <Marker
                key={station.id}
                coordinate={{
                  latitude: station.latitude,
                  longitude: station.longitude,
                }}
                onPress={() => playStation(station)}
              >
                <View style={styles.stationMarker}>
                  <Ionicons name="radio" size={20} color="#FFFFFF" />
                </View>
              </Marker>
            ))}

            {/* Station Coverage Radius */}
            {showCoverageRadius && selectedStation && (
              <Circle
                center={{
                  latitude: selectedStation.latitude,
                  longitude: selectedStation.longitude,
                }}
                radius={50000} // 50km coverage
                strokeColor="rgba(255, 107, 53, 0.5)"
                fillColor="rgba(255, 107, 53, 0.1)"
                strokeWidth={2}
              />
            )}

            {/* Traffic Incident Markers */}
            {trafficIncidents.map((incident) => (
              <Marker
                key={incident.id}
                coordinate={{
                  latitude: incident.location.lat,
                  longitude: incident.location.lon,
                }}
                onPress={() => Alert.alert('Traffic Incident', incident.description)}
              >
                <View style={[
                  styles.trafficMarker,
                  { backgroundColor: getIncidentColor(incident.severity) }
                ]}>
                  <Text style={styles.trafficIcon}>{getIncidentIcon(incident.type)}</Text>
                </View>
              </Marker>
            ))}
          </MapView>

          {/* Map Controls */}
          <View style={styles.controlsContainer}>
            <TouchableOpacity
              style={styles.controlButton}
              onPress={toggleMapType}
            >
              <Ionicons name="layers" size={24} color="#FFFFFF" />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.controlButton}
              onPress={() => setShowCoverageRadius(!showCoverageRadius)}
            >
              <Ionicons 
                name={showCoverageRadius ? "radio" : "radio-outline"} 
                size={24} 
                color="#FFFFFF" 
              />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.controlButton}
              onPress={() => setShowTrafficPanel(true)}
            >
              <Ionicons name="car" size={24} color="#FFFFFF" />
              {trafficIncidents.length > 0 && (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>{trafficIncidents.length}</Text>
                </View>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.controlButton}
              onPress={() => {
                if (userLocation && mapRef.current) {
                  mapRef.current.animateToRegion({
                    latitude: userLocation.coords.latitude,
                    longitude: userLocation.coords.longitude,
                    latitudeDelta: 0.5,
                    longitudeDelta: 0.5,
                  });
                }
              }}
            >
              <Ionicons name="locate" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          {/* Legend */}
          <View style={styles.legend}>
            <View style={styles.legendItem}>
              <View style={styles.stationMarker}>
                <Ionicons name="radio" size={16} color="#FFFFFF" />
              </View>
              <Text style={styles.legendText}>Radio Stations</Text>
            </View>
            <View style={styles.legendItem}>
              <Text style={styles.trafficIcon}>🚗💥</Text>
              <Text style={styles.legendText}>Traffic Incidents</Text>
            </View>
          </View>

          {/* Traffic Panel Modal */}
          <Modal
            visible={showTrafficPanel}
            animationType="slide"
            transparent={true}
            onRequestClose={() => setShowTrafficPanel(false)}
          >
            <View style={styles.modalOverlay}>
              <View style={styles.trafficPanel}>
                <View style={styles.panelHeader}>
                  <Text style={styles.panelTitle}>🚦 Live Traffic Update</Text>
                  <TouchableOpacity onPress={() => setShowTrafficPanel(false)}>
                    <Ionicons name="close" size={28} color="#FFFFFF" />
                  </TouchableOpacity>
                </View>

                <ScrollView style={styles.panelContent}>
                  {/* Traffic Announcement */}
                  {trafficAnnouncement && (
                    <View style={styles.announcementCard}>
                      <Ionicons name="megaphone" size={24} color="#FF6B35" />
                      <Text style={styles.announcementText}>{trafficAnnouncement}</Text>
                    </View>
                  )}

                  {/* Traffic Incidents List */}
                  {trafficIncidents.length > 0 ? (
                    trafficIncidents.map((incident) => (
                      <View key={incident.id} style={styles.incidentCard}>
                        <View style={styles.incidentHeader}>
                          <Text style={styles.incidentIcon}>{getIncidentIcon(incident.type)}</Text>
                          <View style={[
                            styles.severityBadge,
                            { backgroundColor: getIncidentColor(incident.severity) }
                          ]}>
                            <Text style={styles.severityText}>{incident.severity}</Text>
                          </View>
                        </View>
                        <Text style={styles.incidentDescription}>{incident.description}</Text>
                        {incident.delay_minutes && incident.delay_minutes > 0 && (
                          <Text style={styles.incidentDelay}>
                            ⏱️ ~{incident.delay_minutes} min delay
                          </Text>
                        )}
                      </View>
                    ))
                  ) : (
                    <View style={styles.emptyTraffic}>
                      <Ionicons name="checkmark-circle" size={48} color="#00FF00" />
                      <Text style={styles.emptyTrafficText}>No traffic incidents in your area</Text>
                    </View>
                  )}
                </ScrollView>
              </View>
            </View>
          </Modal>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginTop: 16,
  },
  mapContainer: {
    flex: 1,
  },
  map: {
    width: width,
    height: height,
  },
  stationMarker: {
    backgroundColor: '#FF6B35',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  trafficMarker: {
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  trafficIcon: {
    fontSize: 20,
  },
  controlsContainer: {
    position: 'absolute',
    right: 16,
    top: 16,
    gap: 12,
  },
  controlButton: {
    backgroundColor: '#1A1A1A',
    borderRadius: 12,
    width: 56,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#FF0000',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
  },
  legend: {
    position: 'absolute',
    bottom: 16,
    left: 16,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderRadius: 12,
    padding: 12,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 8,
  },
  legendText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  trafficPanel: {
    backgroundColor: '#1A1A1A',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: height * 0.7,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  panelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  panelTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  panelContent: {
    padding: 16,
  },
  announcementCard: {
    flexDirection: 'row',
    backgroundColor: '#000000',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#FF6B35',
    gap: 12,
  },
  announcementText: {
    flex: 1,
    color: '#FFFFFF',
    fontSize: 14,
    lineHeight: 20,
  },
  incidentCard: {
    backgroundColor: '#000000',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  incidentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 8,
  },
  incidentIcon: {
    fontSize: 24,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  severityText: {
    color: '#000000',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  incidentDescription: {
    color: '#FFFFFF',
    fontSize: 14,
    marginBottom: 4,
  },
  incidentDelay: {
    color: '#FF6B35',
    fontSize: 12,
    fontWeight: '600',
  },
  emptyTraffic: {
    alignItems: 'center',
    padding: 32,
  },
  emptyTrafficText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginTop: 16,
    textAlign: 'center',
  },
});
