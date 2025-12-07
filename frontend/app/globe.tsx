import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Globe3D } from '../components/Globe3D';
import { useTheme } from './theme-context';

const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://radio-uifix.preview.emergentagent.com';

interface Station {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  stream_url: string;
  call_sign?: string;
  quality_score?: number;
}

export default function GlobeViewScreen() {
  const { theme } = useTheme();
  const [loading, setLoading] = useState(true);
  const [stations, setStations] = useState<Station[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStations();
  }, []);

  const fetchStations = async () => {
    try {
      setLoading(true);
      setError(null);

      const apiUrl = `${API_BASE_URL}/api/map/stations?limit=500`;
      console.log('API_BASE_URL:', API_BASE_URL);
      console.log('Fetching stations from:', apiUrl);
      
      // Fetch stations with coordinates
      const response = await fetch(apiUrl);
      console.log('Response status:', response.status);
      
      const data = await response.json();
      console.log('Response data:', JSON.stringify(data).substring(0, 200));

      if (data.status === 'success' && data.data && data.data.stations) {
        const stationCount = data.data.stations.length;
        console.log('SUCCESS: Setting', stationCount, 'stations');
        setStations(data.data.stations);
        
        // Show alert for debugging
        Alert.alert(
          'Stations Loaded',
          `Successfully loaded ${stationCount} stations from ${API_BASE_URL}`,
          [{ text: 'OK' }]
        );
      } else {
        console.error('Invalid response format:', data);
        setError('Failed to load stations - invalid format');
        Alert.alert('Error', 'Invalid response format from server');
      }
    } catch (err) {
      console.error('Error fetching stations:', err);
      const errorMsg = `Failed to load stations: ${err}`;
      setError(errorMsg);
      Alert.alert('Error', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleStationPress = (station: Station) => {
    Alert.alert(
      station.name,
      `${station.country}\nQuality: ${station.quality_score || 'N/A'}`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Play Station',
          onPress: () => {
            // Navigate back to home and play station
            router.push('/');
          },
        },
      ]
    );
  };

  return (
    <SafeAreaView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      edges={['top']}
    >
      <Stack.Screen
        options={{
          title: '3D Globe View',
          headerShown: true,
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTintColor: theme.colors.text,
          headerLeft: () => (
            <TouchableOpacity
              onPress={() => router.back()}
              style={styles.backButton}
            >
              <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
            </TouchableOpacity>
          ),
        }}
      />

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF6B35" />
          <Text style={[styles.loadingText, { color: theme.colors.text }]}>
            Loading global stations...
          </Text>
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={64} color="#FF6B35" />
          <Text style={[styles.errorText, { color: theme.colors.text }]}>
            {error}
          </Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={fetchStations}
          >
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          <Globe3D
            stations={stations}
            onStationPress={handleStationPress}
            autoRotate={true}
          />
          
          {/* Stats Card */}
          <View style={styles.statsCard}>
            <View style={styles.statItem}>
              <Ionicons name="radio" size={20} color="#FF6B35" />
              <Text style={styles.statValue}>{stations.length}</Text>
              <Text style={styles.statLabel}>Stations</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Ionicons name="globe" size={20} color="#FF6B35" />
              <Text style={styles.statValue}>
                {new Set(stations.map(s => s.country)).size}
              </Text>
              <Text style={styles.statLabel}>Countries</Text>
            </View>
          </View>
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    fontSize: 16,
    marginTop: 16,
    fontWeight: '600',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 24,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#FF6B35',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  backButton: {
    marginLeft: 8,
  },
  statsCard: {
    position: 'absolute',
    top: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 53, 0.5)',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statDivider: {
    width: 1,
    backgroundColor: 'rgba(139, 146, 176, 0.3)',
    marginHorizontal: 16,
  },
  statValue: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: '700',
    marginTop: 8,
  },
  statLabel: {
    color: '#8B92B0',
    fontSize: 12,
    marginTop: 4,
  },
});
