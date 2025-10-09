import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  Platform,
} from 'react-native';
import { useTheme } from '../contexts/ThemeContext';

// Enhanced UI Components
import { Button } from './UI/Button';
import { Card } from './UI/Card';
import { LoadingSpinner } from './UI/LoadingSpinner';
import { EnhancedAudioControls } from './UI/EnhancedAudioControls';
import { CountryPicker } from './UI/CountryPicker';
import { RefreshableView } from './UI/EnhancedRefreshControl';
import {
  RadioStationSkeleton,
  NewsArticleSkeleton,
  MusicTrackSkeleton,
  AudioPlayerSkeleton,
} from './UI/SkeletonLoader';
import { AccessibleText, AccessibleTouchable } from './UI/AccessibilityHelpers';
import { TabNavigator } from './Navigation/TabNavigator';

// Performance optimizations
import {
  AdvancedCache,
  ImageOptimizer,
  PerformanceAnalytics,
  NetworkAwareLoader,
  useDebounce,
  useOptimizedRender,
  initializePerformanceOptimizations,
} from '../utils/AdvancedPerformanceOptimizer';

// Services
import { HybridLocationService } from '../services/HybridLocationService';

interface EnhancedMainAppProps {
  initialData?: any;
  onTabChange?: (tab: string) => void;
}

interface AppState {
  isLoading: boolean;
  selectedCountry: string | undefined;
  currentLocation: { latitude: number; longitude: number } | null;
  activeTab: 'radio' | 'news' | 'music' | 'language' | 'apps' | 'settings';
  audioState: {
    isPlaying: boolean;
    currentTrack: {
      title: string;
      artist: string;
      duration?: number;
      position?: number;
    } | null;
  };
  stationsData: any[];
  newsData: any[];
  musicData: any[];
}

export const EnhancedMainApp: React.FC<EnhancedMainAppProps> = ({
  initialData,
  onTabChange,
}) => {
  const { colors, isDark } = useTheme();

  // Main app state with performance optimization
  const [appState, setAppState] = useState<AppState>({
    isLoading: false,
    selectedCountry: undefined,
    currentLocation: null,
    activeTab: 'radio',
    audioState: {
      isPlaying: false,
      currentTrack: null,
    },
    stationsData: [],
    newsData: [],
    musicData: [],
  });

  // Debounced search and loading states
  const [searchText, setSearchText] = useState('');
  const debouncedSearch = useDebounce(searchText, 300);
  const [refreshing, setRefreshing] = useState(false);

  // Performance monitoring
  useEffect(() => {
    initializePerformanceOptimizations();
    PerformanceAnalytics.recordMetric('app-mount', 0, { component: 'EnhancedMainApp' });
  }, []);

  // Location detection with caching
  useEffect(() => {
    const detectLocation = async () => {
      try {
        PerformanceAnalytics.recordMetric('location-detection-start', Date.now());
        
        const location = await HybridLocationService.getCurrentLocation();
        if (location) {
          setAppState(prev => ({
            ...prev,
            currentLocation: location,
            selectedCountry: location.country || 'US',
          }));
          
          PerformanceAnalytics.recordMetric('location-detection-success', Date.now());
        }
      } catch (error) {
        console.warn('Location detection failed:', error);
        PerformanceAnalytics.recordMetric('location-detection-error', Date.now(), { error: error.message });
      }
    };

    detectLocation();
  }, []);

  // Optimized data fetching with caching
  const fetchData = useCallback(async (forceRefresh = false) => {
    const cacheKey = `app-data-${appState.activeTab}-${appState.selectedCountry}`;
    
    if (!forceRefresh) {
      // Try to get cached data first
      const cachedData = AdvancedCache.prototype.get(cacheKey);
      if (cachedData) {
        setAppState(prev => ({
          ...prev,
          ...cachedData,
          isLoading: false,
        }));
        return;
      }
    }

    setAppState(prev => ({ ...prev, isLoading: true }));
    
    try {
      PerformanceAnalytics.recordMetric('data-fetch-start', Date.now());

      // Simulate API calls with network-aware loading
      const loadingStrategy = NetworkAwareLoader.getOptimalLoadingStrategy();
      
      const mockData = {
        stationsData: Array.from({ length: 10 }, (_, i) => ({
          id: i,
          name: `Station ${i + 1}`,
          country: appState.selectedCountry,
          genre: 'General',
          isLive: Math.random() > 0.3,
        })),
        newsData: Array.from({ length: 8 }, (_, i) => ({
          id: i,
          title: `News Article ${i + 1}`,
          summary: 'Latest news from around the world...',
          timestamp: new Date().toISOString(),
        })),
        musicData: Array.from({ length: 12 }, (_, i) => ({
          id: i,
          title: `Track ${i + 1}`,
          artist: `Artist ${i + 1}`,
          duration: 180 + Math.random() * 120,
        })),
      };

      // Cache the data
      const cache = new AdvancedCache(100, 30);
      cache.set(cacheKey, mockData);

      setAppState(prev => ({
        ...prev,
        ...mockData,
        isLoading: false,
      }));

      PerformanceAnalytics.recordMetric('data-fetch-success', Date.now());
    } catch (error) {
      console.error('Data fetching failed:', error);
      setAppState(prev => ({ ...prev, isLoading: false }));
      PerformanceAnalytics.recordMetric('data-fetch-error', Date.now(), { error: error.message });
    }
  }, [appState.activeTab, appState.selectedCountry]);

  // Optimized refresh handler
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchData(true);
    setRefreshing(false);
  }, [fetchData]);

  // Tab change handler with performance tracking
  const handleTabChange = useCallback((tab: typeof appState.activeTab) => {
    PerformanceAnalytics.recordMetric('tab-switch', Date.now(), { from: appState.activeTab, to: tab });
    
    setAppState(prev => ({ ...prev, activeTab: tab }));
    onTabChange?.(tab);
  }, [appState.activeTab, onTabChange]);

  // Country selection handler
  const handleCountrySelect = useCallback((country: any) => {
    setAppState(prev => ({ ...prev, selectedCountry: country.code }));
    fetchData();
  }, [fetchData]);

  // Audio controls handlers
  const handlePlayPause = useCallback(() => {
    setAppState(prev => ({
      ...prev,
      audioState: {
        ...prev.audioState,
        isPlaying: !prev.audioState.isPlaying,
      },
    }));
  }, []);

  // Optimized render functions
  const renderTabContent = useMemo(() => {
    switch (appState.activeTab) {
      case 'radio':
        return renderRadioTab();
      case 'news':
        return renderNewsTab();
      case 'music':
        return renderMusicTab();
      case 'language':
        return renderLanguageTab();
      case 'apps':
        return renderAppsTab();
      case 'settings':
        return renderSettingsTab();
      default:
        return renderRadioTab();
    }
  }, [appState.activeTab, appState.isLoading, appState.stationsData, appState.newsData, appState.musicData]);

  const renderRadioTab = () => (
    <View style={styles.tabContent}>
      <AccessibleText role="header" level={2} style={styles.sectionTitle}>
        Radio Stations
      </AccessibleText>
      
      {/* Country Picker */}
      <View style={styles.controlsContainer}>
        <CountryPicker
          selectedCountry={appState.selectedCountry}
          onCountrySelect={handleCountrySelect}
          currentLocation={appState.currentLocation}
          placeholder="Select your country"
          showRegionFilter={true}
        />
      </View>

      {/* Audio Player */}
      <EnhancedAudioControls
        isPlaying={appState.audioState.isPlaying}
        onPlayPause={handlePlayPause}
        currentTrack={appState.audioState.currentTrack}
        showExtendedControls={true}
      />

      {/* Stations List */}
      <View style={styles.listContainer}>
        {appState.isLoading ? (
          <>
            <RadioStationSkeleton />
            <RadioStationSkeleton />
            <RadioStationSkeleton />
          </>
        ) : (
          appState.stationsData.map((station) => (
            <Card
              key={station.id}
              variant="elevated"
              padding="medium"
              margin="small"
              style={styles.stationCard}
            >
              <View style={styles.stationContent}>
                <AccessibleText style={styles.stationName}>
                  {station.name}
                </AccessibleText>
                <Text style={[styles.stationGenre, { color: colors.textSecondary }]}>
                  {station.genre} • {station.country}
                </Text>
                {station.isLive && (
                  <View style={[styles.liveIndicator, { backgroundColor: colors.success }]}>
                    <Text style={styles.liveText}>LIVE</Text>
                  </View>
                )}
              </View>
            </Card>
          ))
        )}
      </View>
    </View>
  );

  const renderNewsTab = () => (
    <View style={styles.tabContent}>
      <AccessibleText role="header" level={2} style={styles.sectionTitle}>
        Latest News
      </AccessibleText>
      
      <View style={styles.listContainer}>
        {appState.isLoading ? (
          <>
            <NewsArticleSkeleton />
            <NewsArticleSkeleton />
          </>
        ) : (
          appState.newsData.map((article) => (
            <Card
              key={article.id}
              variant="elevated"
              padding="medium"
              margin="small"
            >
              <AccessibleText style={styles.newsTitle}>
                {article.title}
              </AccessibleText>
              <Text style={[styles.newsSummary, { color: colors.textSecondary }]}>
                {article.summary}
              </Text>
            </Card>
          ))
        )}
      </View>
    </View>
  );

  const renderMusicTab = () => (
    <View style={styles.tabContent}>
      <AccessibleText role="header" level={2} style={styles.sectionTitle}>
        Music Library
      </AccessibleText>
      
      <View style={styles.listContainer}>
        {appState.isLoading ? (
          <>
            <MusicTrackSkeleton />
            <MusicTrackSkeleton />
            <MusicTrackSkeleton />
          </>
        ) : (
          appState.musicData.map((track) => (
            <Card
              key={track.id}
              variant="outlined"
              padding="small"
              margin="small"
              onPress={() => {
                setAppState(prev => ({
                  ...prev,
                  audioState: {
                    isPlaying: true,
                    currentTrack: track,
                  },
                }));
              }}
            >
              <View style={styles.trackContent}>
                <View>
                  <AccessibleText style={styles.trackTitle}>
                    {track.title}
                  </AccessibleText>
                  <Text style={[styles.trackArtist, { color: colors.textSecondary }]}>
                    {track.artist}
                  </Text>
                </View>
                <Text style={[styles.trackDuration, { color: colors.textSecondary }]}>
                  {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                </Text>
              </View>
            </Card>
          ))
        )}
      </View>
    </View>
  );

  const renderLanguageTab = () => (
    <View style={styles.tabContent}>
      <AccessibleText role="header" level={2} style={styles.sectionTitle}>
        Language Settings
      </AccessibleText>
      <Text style={[styles.placeholder, { color: colors.textSecondary }]}>
        Language configuration options will appear here.
      </Text>
    </View>
  );

  const renderAppsTab = () => (
    <View style={styles.tabContent}>
      <AccessibleText role="header" level={2} style={styles.sectionTitle}>
        Connected Apps
      </AccessibleText>
      <Text style={[styles.placeholder, { color: colors.textSecondary }]}>
        External app integrations will appear here.
      </Text>
    </View>
  );

  const renderSettingsTab = () => (
    <View style={styles.tabContent}>
      <AccessibleText role="header" level={2} style={styles.sectionTitle}>
        Settings
      </AccessibleText>
      
      <Card variant="outlined" padding="medium" margin="medium">
        <Text style={[styles.settingLabel, { color: colors.text }]}>
          Performance Metrics
        </Text>
        <Button
          title="View Performance Report"
          variant="outline"
          size="small"
          onPress={() => {
            const metrics = PerformanceAnalytics.generateReport();
            console.log('📊 Performance Report:', metrics);
          }}
          style={{ marginTop: 8 }}
        />
      </Card>

      <Text style={[styles.placeholder, { color: colors.textSecondary }]}>
        Additional settings will appear here.
      </Text>
    </View>
  );

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    tabContent: {
      flex: 1,
      paddingHorizontal: 16,
      paddingTop: 16,
    },
    sectionTitle: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
      marginBottom: 16,
    },
    controlsContainer: {
      marginBottom: 20,
    },
    listContainer: {
      flex: 1,
    },
    stationCard: {
      marginBottom: 8,
    },
    stationContent: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    stationName: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      flex: 1,
    },
    stationGenre: {
      fontSize: 14,
      marginTop: 2,
    },
    liveIndicator: {
      paddingHorizontal: 8,
      paddingVertical: 2,
      borderRadius: 4,
      alignSelf: 'flex-start',
    },
    liveText: {
      fontSize: 10,
      fontWeight: 'bold',
      color: '#FFFFFF',
    },
    newsTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 8,
    },
    newsSummary: {
      fontSize: 14,
      lineHeight: 20,
    },
    trackContent: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    trackTitle: {
      fontSize: 16,
      fontWeight: '500',
      color: colors.text,
    },
    trackArtist: {
      fontSize: 14,
      marginTop: 2,
    },
    trackDuration: {
      fontSize: 12,
      fontWeight: '500',
    },
    placeholder: {
      fontSize: 16,
      textAlign: 'center',
      marginTop: 50,
      fontStyle: 'italic',
    },
    settingLabel: {
      fontSize: 16,
      fontWeight: '500',
      marginBottom: 8,
    },
  });

  if (appState.isLoading && appState.stationsData.length === 0) {
    return (
      <SafeAreaView style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <StatusBar
          barStyle={isDark ? 'light-content' : 'dark-content'}
          backgroundColor={colors.background}
        />
        <AudioPlayerSkeleton />
        <LoadingSpinner
          size="large"
          message="Loading enhanced experience..."
          overlay={false}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar
        barStyle={isDark ? 'light-content' : 'dark-content'}
        backgroundColor={colors.background}
      />
      
      <RefreshableView
        onRefresh={handleRefresh}
        refreshing={refreshing}
        style={{ flex: 1 }}
      >
        {renderTabContent}
      </RefreshableView>

      <TabNavigator
        activeTab={appState.activeTab}
        onTabChange={handleTabChange}
        showLabels={true}
      />
    </SafeAreaView>
  );
};