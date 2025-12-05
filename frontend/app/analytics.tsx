import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.EXPO_BACKEND_URL || 'http://localhost:8001';

export default function AnalyticsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/analytics/dashboard`);
      const result = await response.json();
      
      if (result.success) {
        setAnalyticsData(result.data);
        setError(null);
      } else {
        setError('Failed to load analytics');
      }
    } catch (err) {
      console.error('Analytics fetch error:', err);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchAnalytics();
  };

  const analytics = analyticsData?.analytics || {};
  const userBehavior = analytics.user_behavior || {};
  const stationPopularity = analytics.station_popularity || {};
  const geoDist = analytics.geographic_distribution || {};
  const apiUsage = analytics.api_usage || {};

  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>📊 Analytics Dashboard</Text>
        <TouchableOpacity onPress={fetchAnalytics} style={styles.refreshButton}>
          <Ionicons name="refresh" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#1E88E5" />
            <Text style={styles.loadingText}>Loading analytics...</Text>
          </View>
        ) : error ? (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={48} color="#FF5252" />
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity style={styles.retryButton} onPress={fetchAnalytics}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.cardsContainer}>
            {/* User Behavior Card */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Ionicons name="people" size={24} color="#1E88E5" />
                <Text style={styles.cardTitle}>User Activity (24h)</Text>
              </View>
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{userBehavior.unique_users_24h || 0}</Text>
                  <Text style={styles.statLabel}>Unique Users</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{userBehavior.total_requests_24h || 0}</Text>
                  <Text style={styles.statLabel}>Total Requests</Text>
                </View>
              </View>
              {userBehavior.avg_requests_per_user && (
                <Text style={styles.cardSubtext}>
                  Avg: {userBehavior.avg_requests_per_user.toFixed(1)} requests/user
                </Text>
              )}
            </View>

            {/* Station Popularity Card */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Ionicons name="radio" size={24} color="#4CAF50" />
                <Text style={styles.cardTitle}>Station Stats</Text>
              </View>
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{stationPopularity.online_stations || 0}</Text>
                  <Text style={styles.statLabel}>Online Stations</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>
                    {stationPopularity.avg_quality_score?.toFixed(1) || '0.0'}
                  </Text>
                  <Text style={styles.statLabel}>Avg Quality</Text>
                </View>
              </View>
            </View>

            {/* Geographic Distribution Card */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Ionicons name="globe" size={24} color="#FF9800" />
                <Text style={styles.cardTitle}>Geographic Coverage</Text>
              </View>
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{geoDist.total_countries || 0}</Text>
                  <Text style={styles.statLabel}>Countries</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{geoDist.coverage || 'Global'}</Text>
                  <Text style={styles.statLabel}>Coverage</Text>
                </View>
              </View>
              {geoDist.top_countries && geoDist.top_countries.length > 0 && (
                <View style={styles.topCountriesContainer}>
                  <Text style={styles.topCountriesTitle}>Top Countries:</Text>
                  {geoDist.top_countries.slice(0, 3).map((c: any, idx: number) => (
                    <Text key={idx} style={styles.topCountryItem}>
                      {c.country}: {c.stations} stations
                    </Text>
                  ))}
                </View>
              )}
            </View>

            {/* API Usage Card */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Ionicons name="pulse" size={24} color="#E91E63" />
                <Text style={styles.cardTitle}>API Health</Text>
              </View>
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{apiUsage.total_requests_24h || 0}</Text>
                  <Text style={styles.statLabel}>Requests (24h)</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>
                    {apiUsage.error_rate_percent?.toFixed(1) || '0.0'}%
                  </Text>
                  <Text style={styles.statLabel}>Error Rate</Text>
                </View>
              </View>
              <View style={styles.healthIndicator}>
                <View
                  style={[
                    styles.healthDot,
                    { backgroundColor: apiUsage.health === 'good' ? '#4CAF50' : '#FF9800' },
                  ]}
                />
                <Text style={styles.healthText}>
                  System Health: {apiUsage.health || 'Unknown'}
                </Text>
              </View>
            </View>

            {/* Execution Time */}
            {analyticsData?.execution_time_seconds && (
              <View style={styles.footerInfo}>
                <Text style={styles.footerText}>
                  Analysis completed in {analyticsData.execution_time_seconds.toFixed(2)}s
                </Text>
                <Text style={styles.footerText}>
                  Last updated: {new Date(analyticsData.timestamp).toLocaleTimeString()}
                </Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>
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
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#1A1F3A',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    flex: 1,
    textAlign: 'center',
  },
  refreshButton: {
    padding: 8,
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 100,
  },
  loadingText: {
    marginTop: 16,
    color: '#8B92B0',
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 100,
    paddingHorizontal: 32,
  },
  errorText: {
    marginTop: 16,
    color: '#FF5252',
    fontSize: 16,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 24,
    paddingVertical: 12,
    paddingHorizontal: 32,
    backgroundColor: '#1E88E5',
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  cardsContainer: {
    padding: 16,
  },
  card: {
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#2A2F4A',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 12,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  statLabel: {
    fontSize: 12,
    color: '#8B92B0',
    marginTop: 4,
  },
  cardSubtext: {
    marginTop: 12,
    fontSize: 14,
    color: '#8B92B0',
    textAlign: 'center',
  },
  topCountriesContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#2A2F4A',
  },
  topCountriesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8B92B0',
    marginBottom: 8,
  },
  topCountryItem: {
    fontSize: 14,
    color: '#FFFFFF',
    marginBottom: 4,
  },
  healthIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    justifyContent: 'center',
  },
  healthDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  healthText: {
    fontSize: 14,
    color: '#8B92B0',
  },
  footerInfo: {
    marginTop: 8,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#2A2F4A',
  },
  footerText: {
    fontSize: 12,
    color: '#8B92B0',
    textAlign: 'center',
    marginBottom: 4,
  },
});
