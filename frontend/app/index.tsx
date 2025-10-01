import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  ScrollView,
  RefreshControl,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';
import { EnhancedAudioPlayer } from '../components/EnhancedAudioPlayer';
import { FavoritesManager, addItemToFavorites } from '../components/FavoritesManager';
import { SocialSharingManager } from '../components/SocialSharingManager';
import { AudioRecorder } from '../components/AudioRecorder';
import { notificationService } from '../services/NotificationService';
import * as Haptics from 'expo-haptics';
import AsyncStorage from '@react-native-async-storage/async-storage';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';

interface StationInfo {
  name: string;
  description: string;
  streamUrl: string;
  currentShow?: string;
  frequency?: string;
}

interface NewsArticle {
  title: string;
  description: string;
  source: string;
  published_at: string;
  category?: string;
}

interface MusicTrack {
  id: string;
  name: string;
  artists: string[];
  album: string;
  popularity: number;
}

const EnhancedKagemaFMApp: React.FC = () => {
  const { colors, isDark, toggleTheme } = useTheme();
  
  // App state
  const [stationInfo, setStationInfo] = useState<StationInfo>({
    name: 'Kagema FM',
    description: 'Your Premier International Radio Platform',
    streamUrl: 'https://ice1.somafm.com/groovesalad-256-mp3',
    currentShow: 'Live International Radio',
    frequency: '101.5 FM'
  });
  
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [musicTracks, setMusicTracks] = useState<MusicTrack[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'radio' | 'news' | 'music' | 'settings'>('radio');
  
  // Modal state
  const [showFavorites, setShowFavorites] = useState(false);
  const [showSharing, setShowSharing] = useState(false);
  const [showRecorder, setShowRecorder] = useState(false);
  const [shareData, setShareData] = useState<any>(null);
  
  // Audio player state
  const [isPlaying, setIsPlaying] = useState(false);
  
  // User preferences
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [autoPlay, setAutoPlay] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);

  useEffect(() => {
    initializeApp();
    loadContent();
    setupNotifications();
  }, []);

  const initializeApp = async () => {
    try {
      // Load user preferences
      const preferences = await AsyncStorage.getItem('user_preferences');
      if (preferences) {
        const parsed = JSON.parse(preferences);
        setNotificationsEnabled(parsed.notifications ?? true);
        setAutoPlay(parsed.autoPlay ?? false);
        setOfflineMode(parsed.offlineMode ?? false);
      }
    } catch (error) {
      console.log('Error loading preferences:', error);
    }
  };

  const setupNotifications = async () => {
    try {
      await notificationService.initialize();
      notificationService.setupNotificationResponseHandler();
      
      // Schedule smart notifications
      await notificationService.scheduleSmartNotifications();
      
      console.log('✅ Notifications initialized');
    } catch (error) {
      console.log('⚠️ Notification setup error:', error);
    }
  };

  const loadContent = async () => {
    try {
      setRefreshing(true);
      
      // Load station info
      const stationResponse = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/station-info`);
      if (stationResponse.ok) {
        const stationData = await stationResponse.json();
        setStationInfo({
          name: stationData.name || 'Kagema FM',
          description: stationData.description || 'International Radio Station',
          streamUrl: stationData.streamUrl || 'https://ice1.somafm.com/groovesalad-256-mp3',
          currentShow: stationData.currentShow || 'Live Radio',
          frequency: stationData.frequency || '101.5 FM'
        });
      }

      // Load news and music (simplified for demo)
      setNewsArticles([
        {
          title: 'Welcome to Enhanced Kagema FM',
          description: 'Experience the new features: themes, favorites, sharing, recording, and smart notifications!',
          source: 'Kagema FM',
          published_at: new Date().toISOString()
        },
        {
          title: 'New Features Available',
          description: 'Dark/Light themes, audio recording, social sharing, and enhanced notifications are now live.',
          source: 'Tech News',
          published_at: new Date().toISOString()
        }
      ]);

      setMusicTracks([
        {
          id: '1',
          name: 'International Vibes',
          artists: ['Kagema FM'],
          album: 'Live Radio Mix',
          popularity: 100
        },
        {
          id: '2',
          name: 'Global Rhythms',
          artists: ['World Music Collective'],
          album: 'International Hits',
          popularity: 95
        }
      ]);

    } catch (error) {
      console.log('Error loading content:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handlePlayStateChange = (playing: boolean) => {
    setIsPlaying(playing);
    
    if (playing) {
      // Send notification about now playing
      notificationService.sendMusicDiscovery(
        stationInfo.name,
        stationInfo.currentShow || 'Live Radio',
        'Now streaming on Kagema FM'
      );
    }
  };

  const handleAddToFavorites = async (item: any, type: string) => {
    const result = await addItemToFavorites({
      type: type as any,
      title: item.title || item.name,
      description: item.description,
      streamUrl: item.streamUrl,
      metadata: item
    });

    if (result.success) {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      Alert.alert('Added!', result.message);
    } else {
      Alert.alert('Info', result.message);
    }
  };

  const handleShare = (item: any, type: string) => {
    setShareData({
      type,
      title: item.title || item.name,
      description: item.description,
      metadata: item
    });
    setShowSharing(true);
  };

  const savePreferences = async () => {
    try {
      const preferences = {
        notifications: notificationsEnabled,
        autoPlay,
        offlineMode,
        theme: isDark ? 'dark' : 'light'
      };
      await AsyncStorage.setItem('user_preferences', JSON.stringify(preferences));
    } catch (error) {
      console.log('Error saving preferences:', error);
    }
  };

  const renderRadioTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadContent} />}
    >
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.appTitle, { color: colors.text }]}>Kagema FM Enhanced</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={toggleTheme}
          >
            <Ionicons 
              name={isDark ? 'sunny' : 'moon'} 
              size={24} 
              color={colors.text} 
            />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => setShowFavorites(true)}
          >
            <Ionicons name="heart" size={24} color={colors.primary} />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => setShowRecorder(true)}
          >
            <Ionicons name="mic" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>
      </View>

      <EnhancedAudioPlayer
        streamUrl={stationInfo.streamUrl}
        title={stationInfo.name}
        subtitle={stationInfo.currentShow || 'Live Radio'}
        onPlayStateChange={handlePlayStateChange}
        onError={(error) => Alert.alert('Audio Error', error)}
      />

      <View style={[styles.stationActions, { backgroundColor: colors.surface }]}>
        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: colors.primary }]}
          onPress={() => handleAddToFavorites(stationInfo, 'radio_station')}
        >
          <Ionicons name="heart-outline" size={20} color="white" />
          <Text style={[styles.actionButtonText, { color: 'white' }]}>Favorite</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: colors.accent }]}
          onPress={() => handleShare(stationInfo, 'radio_station')}
        >
          <Ionicons name="share-outline" size={20} color="white" />
          <Text style={[styles.actionButtonText, { color: 'white' }]}>Share</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  const renderNewsTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadContent} />}
    >
      <View style={styles.sectionHeader}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Latest News</Text>
        <TouchableOpacity onPress={loadContent}>
          <Ionicons name="refresh" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {newsArticles.map((article, index) => (
        <View key={index} style={[styles.newsCard, { backgroundColor: colors.card }]}>
          <Text style={[styles.newsTitle, { color: colors.text }]}>{article.title}</Text>
          <Text style={[styles.newsDescription, { color: colors.textSecondary }]}>
            {article.description}
          </Text>
          
          <View style={styles.newsFooter}>
            <View style={styles.newsInfo}>
              <Text style={[styles.newsSource, { color: colors.textSecondary }]}>
                {article.source}
              </Text>
              <Text style={[styles.newsDate, { color: colors.textSecondary }]}>
                {new Date(article.published_at).toLocaleDateString()}
              </Text>
            </View>
            
            <View style={styles.newsActions}>
              <TouchableOpacity
                onPress={() => handleAddToFavorites(article, 'news_article')}
              >
                <Ionicons name="bookmark-outline" size={20} color={colors.text} />
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={() => handleShare(article, 'news_article')}
              >
                <Ionicons name="share-outline" size={20} color={colors.text} />
              </TouchableOpacity>
            </View>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  const renderMusicTab = () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadContent} />}
    >
      <View style={styles.sectionHeader}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Trending Music</Text>
        <TouchableOpacity onPress={loadContent}>
          <Ionicons name="refresh" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {musicTracks.map((track, index) => (
        <View key={track.id} style={[styles.musicCard, { backgroundColor: colors.card }]}>
          <View style={styles.musicInfo}>
            <Text style={[styles.musicTitle, { color: colors.text }]}>{track.name}</Text>
            <Text style={[styles.musicArtist, { color: colors.textSecondary }]}>
              {track.artists.join(', ')}
            </Text>
            <Text style={[styles.musicAlbum, { color: colors.textSecondary }]}>
              {track.album}
            </Text>
          </View>
          
          <View style={styles.musicActions}>
            <TouchableOpacity
              onPress={() => handleAddToFavorites(track, 'music_track')}
            >
              <Ionicons name="heart-outline" size={24} color={colors.primary} />
            </TouchableOpacity>
            
            <TouchableOpacity
              onPress={() => handleShare(track, 'music_track')}
            >
              <Ionicons name="share-outline" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  const renderSettingsTab = () => (
    <ScrollView style={styles.tabContent}>
      <View style={styles.settingsSection}>
        <Text style={[styles.settingsTitle, { color: colors.text }]}>Preferences</Text>
        
        <View style={[styles.settingItem, { backgroundColor: colors.surface }]}>
          <View>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Theme</Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              {isDark ? 'Dark' : 'Light'} theme enabled
            </Text>
          </View>
          <TouchableOpacity onPress={toggleTheme}>
            <Ionicons 
              name={isDark ? 'sunny' : 'moon'} 
              size={24} 
              color={colors.primary} 
            />
          </TouchableOpacity>
        </View>

        <View style={[styles.settingItem, { backgroundColor: colors.surface }]}>
          <View>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Notifications</Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              Push notifications for shows and updates
            </Text>
          </View>
          <TouchableOpacity
            onPress={() => {
              setNotificationsEnabled(!notificationsEnabled);
              savePreferences();
              notificationService.updateSettings({ enabled: !notificationsEnabled });
            }}
          >
            <Ionicons 
              name={notificationsEnabled ? 'notifications' : 'notifications-off'} 
              size={24} 
              color={notificationsEnabled ? colors.primary : colors.textSecondary} 
            />
          </TouchableOpacity>
        </View>

        <View style={[styles.settingItem, { backgroundColor: colors.surface }]}>
          <View>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Auto Play</Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              Automatically start playing when app opens
            </Text>
          </View>
          <TouchableOpacity
            onPress={() => {
              setAutoPlay(!autoPlay);
              savePreferences();
            }}
          >
            <Ionicons 
              name={autoPlay ? 'play' : 'play-outline'} 
              size={24} 
              color={autoPlay ? colors.primary : colors.textSecondary} 
            />
          </TouchableOpacity>
        </View>

        <View style={[styles.settingItem, { backgroundColor: colors.surface }]}>
          <View>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Offline Mode</Text>
            <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
              Save data and enable offline features
            </Text>
          </View>
          <TouchableOpacity
            onPress={() => {
              setOfflineMode(!offlineMode);
              savePreferences();
            }}
          >
            <Ionicons 
              name={offlineMode ? 'cloud-offline' : 'cloud-outline'} 
              size={24} 
              color={offlineMode ? colors.primary : colors.textSecondary} 
            />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.settingsSection}>
        <Text style={[styles.settingsTitle, { color: colors.text }]}>Tools</Text>
        
        <TouchableOpacity 
          style={[styles.toolButton, { backgroundColor: colors.surface }]}
          onPress={() => setShowRecorder(true)}
        >
          <Ionicons name="mic" size={24} color={colors.primary} />
          <View style={styles.toolInfo}>
            <Text style={[styles.toolTitle, { color: colors.text }]}>Audio Recorder</Text>
            <Text style={[styles.toolDescription, { color: colors.textSecondary }]}>
              Record voice memos and interviews
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.toolButton, { backgroundColor: colors.surface }]}
          onPress={() => setShowFavorites(true)}
        >
          <Ionicons name="heart" size={24} color={colors.primary} />
          <View style={styles.toolInfo}>
            <Text style={[styles.toolTitle, { color: colors.text }]}>Favorites Manager</Text>
            <Text style={[styles.toolDescription, { color: colors.textSecondary }]}>
              Manage your saved content
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>

      <View style={styles.appInfo}>
        <Text style={[styles.appInfoText, { color: colors.textSecondary }]}>
          Kagema FM Enhanced v2.0.0
        </Text>
        <Text style={[styles.appInfoText, { color: colors.textSecondary }]}>
          Your Premier International Radio Experience
        </Text>
      </View>
    </ScrollView>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'radio':
        return renderRadioTab();
      case 'news':
        return renderNewsTab();
      case 'music':
        return renderMusicTab();
      case 'settings':
        return renderSettingsTab();
      default:
        return renderRadioTab();
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      paddingTop: Platform.OS === 'ios' ? 60 : 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    appTitle: {
      fontSize: 20,
      fontWeight: '600',
    },
    headerActions: {
      flexDirection: 'row',
      gap: 16,
    },
    headerButton: {
      padding: 8,
    },
    tabContent: {
      flex: 1,
    },
    stationActions: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      padding: 16,
      marginHorizontal: 16,
      borderRadius: 12,
      marginTop: 8,
    },
    actionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 20,
      paddingVertical: 12,
      borderRadius: 8,
      gap: 8,
    },
    actionButtonText: {
      fontSize: 16,
      fontWeight: '500',
    },
    sectionHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      paddingBottom: 8,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
    },
    newsCard: {
      margin: 16,
      marginTop: 8,
      padding: 16,
      borderRadius: 12,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    newsTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 8,
    },
    newsDescription: {
      fontSize: 14,
      lineHeight: 20,
      marginBottom: 12,
    },
    newsFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    newsInfo: {
      flex: 1,
    },
    newsSource: {
      fontSize: 12,
      fontWeight: '500',
    },
    newsDate: {
      fontSize: 12,
      marginTop: 2,
    },
    newsActions: {
      flexDirection: 'row',
      gap: 16,
    },
    musicCard: {
      flexDirection: 'row',
      alignItems: 'center',
      margin: 16,
      marginTop: 8,
      padding: 16,
      borderRadius: 12,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    musicInfo: {
      flex: 1,
    },
    musicTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 4,
    },
    musicArtist: {
      fontSize: 14,
      marginBottom: 2,
    },
    musicAlbum: {
      fontSize: 12,
    },
    musicActions: {
      flexDirection: 'row',
      gap: 16,
    },
    settingsSection: {
      margin: 16,
    },
    settingsTitle: {
      fontSize: 18,
      fontWeight: '600',
      marginBottom: 16,
    },
    settingItem: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: 16,
      borderRadius: 12,
      marginBottom: 12,
    },
    settingLabel: {
      fontSize: 16,
      fontWeight: '500',
    },
    settingDescription: {
      fontSize: 14,
      marginTop: 2,
    },
    toolButton: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderRadius: 12,
      marginBottom: 12,
    },
    toolInfo: {
      flex: 1,
      marginLeft: 16,
    },
    toolTitle: {
      fontSize: 16,
      fontWeight: '500',
    },
    toolDescription: {
      fontSize: 14,
      marginTop: 2,
    },
    appInfo: {
      alignItems: 'center',
      padding: 24,
    },
    appInfoText: {
      fontSize: 14,
      textAlign: 'center',
      marginVertical: 2,
    },
    tabBar: {
      flexDirection: 'row',
      backgroundColor: colors.surface,
      borderTopWidth: 1,
      borderTopColor: colors.border,
      paddingBottom: Platform.OS === 'ios' ? 34 : 16,
      paddingTop: 16,
    },
    tabButton: {
      flex: 1,
      alignItems: 'center',
      paddingVertical: 8,
    },
    tabLabel: {
      fontSize: 12,
      marginTop: 4,
    },
  });

  return (
    <View style={styles.container}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />
      
      {renderTabContent()}

      {/* Tab Bar */}
      <View style={styles.tabBar}>
        {[
          { key: 'radio', icon: 'radio', label: 'Radio' },
          { key: 'news', icon: 'newspaper', label: 'News' },
          { key: 'music', icon: 'musical-notes', label: 'Music' },
          { key: 'settings', icon: 'settings', label: 'Settings' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={styles.tabButton}
            onPress={() => {
              setActiveTab(tab.key as any);
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            }}
          >
            <Ionicons
              name={tab.icon as any}
              size={24}
              color={activeTab === tab.key ? colors.primary : colors.textSecondary}
            />
            <Text
              style={[
                styles.tabLabel,
                {
                  color: activeTab === tab.key ? colors.primary : colors.textSecondary,
                },
              ]}
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Modals */}
      <FavoritesManager
        visible={showFavorites}
        onClose={() => setShowFavorites(false)}
        currentlyPlaying={isPlaying ? stationInfo.name : undefined}
      />

      <SocialSharingManager
        visible={showSharing}
        onClose={() => setShowSharing(false)}
        shareData={shareData}
      />

      <AudioRecorder
        visible={showRecorder}
        onClose={() => setShowRecorder(false)}
        onRecordingComplete={(recording) => {
          console.log('Recording completed:', recording);
          Alert.alert('Recording Saved!', `${recording.title} has been saved to your recordings.`);
        }}
      />
    </View>
  );
};

// Main App Component with Theme Provider
const App: React.FC = () => {
  return (
    <ThemeProvider>
      <SafeAreaView style={{ flex: 1 }}>
        <EnhancedKagemaFMApp />
      </SafeAreaView>
    </ThemeProvider>
  );
};

export default App;