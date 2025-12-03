import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Station {
  id: string;
  name: string;
  stream_url: string;
  country: string;
  latitude?: number;
  longitude?: number;
  quality_score?: number;
}

export default function MapEnhancedWebScreen() {
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);

  useEffect(() => {
    fetchGeocodedStations();
  }, []);

  const fetchGeocodedStations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stations?limit=100&has_coordinates=true`);
      const data = await response.json();
      
      if (data.status === 'success') {
        const geocoded = data.data.stations.filter(
          (s: Station) => s.latitude && s.longitude
        );
        setStations(geocoded);
      }
    } catch (error) {
      console.error('Error fetching stations:', error);
    } finally {
      setLoading(false);
    }
  };

  const playStation = (station: Station) => {
    setSelectedStation(station);
    // Implement audio playback
  };

  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.title}>📍 Interactive Map</Text>
        <View style={styles.placeholder} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#1E88E5" />
          <Text style={styles.loadingText}>Loading stations...</Text>
        </View>
      ) : (
        <>
          {/* Map Container */}
          <View style={styles.mapContainer}>
            <MapContainer
              center={[0, 0]}
              zoom={2}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              
              {stations.map((station) => (
                station.latitude && station.longitude && (
                  <Marker
                    key={station.id}
                    position={[station.latitude, station.longitude]}
                    eventHandlers={{
                      click: () => playStation(station),
                    }}
                  >
                    <Popup>
                      <View style={styles.popupContent}>
                        <Text style={styles.popupTitle}>{station.name}</Text>
                        <Text style={styles.popupCountry}>{station.country}</Text>
                        <TouchableOpacity
                          style={styles.playButton}
                          onPress={() => playStation(station)}
                        >
                          <Ionicons name="play-circle" size={24} color="#1E88E5" />
                          <Text style={styles.playText}>Play</Text>
                        </TouchableOpacity>
                      </View>
                    </Popup>
                  </Marker>
                )
              ))}
            </MapContainer>
          </View>

          {/* Stats Bar */}
          <View style={styles.statsBar}>
            <View style={styles.stat}>
              <Ionicons name="radio" size={20} color="#1E88E5" />
              <Text style={styles.statText}>{stations.length} Stations</Text>
            </View>
            {selectedStation && (
              <View style={styles.nowPlaying}>
                <Ionicons name="musical-notes" size={20} color="#4CAF50" />
                <Text style={styles.nowPlayingText} numberOfLines={1}>
                  {selectedStation.name}
                </Text>
              </View>
            )}
          </View>
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#1a1f3a',
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  placeholder: {
    width: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 16,
    fontSize: 16,
  },
  mapContainer: {
    flex: 1,
  },
  statsBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#1a1f3a',
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  nowPlaying: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flex: 1,
    marginLeft: 16,
  },
  nowPlayingText: {
    color: '#4CAF50',
    fontSize: 14,
    fontWeight: '600',
  },
  popupContent: {
    padding: 8,
  },
  popupTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  popupCountry: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  playButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 8,
    backgroundColor: '#E3F2FD',
    borderRadius: 8,
  },
  playText: {
    color: '#1E88E5',
    fontWeight: '600',
  },
});
