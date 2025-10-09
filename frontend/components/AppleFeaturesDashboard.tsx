import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import SiriKitIntegration from './SiriKitIntegration';
import EnhancedAirPlayInterface from './EnhancedAirPlayInterface';

interface AppleFeaturesDashboardProps {
  currentlyPlaying?: {
    title: string;
    artist: string;
    stream: string;
  };
  onFeatureActivated?: (feature: string, data: any) => void;
}

type FeatureTab = 'sirikit' | 'airplay';

/**
 * Apple Features Dashboard
 * 
 * Combines SiriKit and Enhanced AirPlay 2 features into a unified interface
 * showcasing the new Apple iOS capabilities for 2024/2025
 */
export const AppleFeaturesDashboard: React.FC<AppleFeaturesDashboardProps> = ({
  currentlyPlaying,
  onFeatureActivated
}) => {
  const [activeTab, setActiveTab] = useState<FeatureTab>('sirikit');

  const handleFeatureActivation = (feature: string, data: any) => {
    console.log(`🍎 Apple feature activated: ${feature}`, data);
    onFeatureActivated?.(feature, data);
  };

  const handleSiriVoiceCommand = (command: string, response: any) => {
    handleFeatureActivation('siri_voice_command', { command, response });
  };

  const handleAirPlayDeviceChange = (deviceId: string) => {
    handleFeatureActivation('airplay_device_change', { deviceId });
  };

  const handleAirPlayGroupChange = (groupId: string) => {
    handleFeatureActivation('airplay_group_change', { groupId });
  };

  if (Platform.OS !== 'ios') {
    return (
      <View style={styles.unavailableContainer}>
        <Ionicons name="logo-apple" size={64} color="#666" />
        <Text style={styles.unavailableTitle}>Apple Features</Text>
        <Text style={styles.unavailableText}>
          SiriKit and Enhanced AirPlay 2 features are only available on iOS devices
        </Text>
        <Text style={styles.unavailableSubtext}>
          These features showcase the latest Apple iOS capabilities for 2024/2025
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header with Apple branding */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Ionicons name="logo-apple" size={32} color="#007AFF" />
          <View style={styles.headerText}>
            <Text style={styles.title}>Apple Features</Text>
            <Text style={styles.subtitle}>SiriKit & Enhanced AirPlay 2</Text>
          </View>
        </View>
        
        <View style={styles.featureBadges}>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>iOS 2024</Text>
          </View>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>NEW</Text>
          </View>
        </View>
      </View>

      {/* Feature Navigation Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[
            styles.tab,
            activeTab === 'sirikit' && styles.tabActive
          ]}
          onPress={() => setActiveTab('sirikit')}
        >
          <Ionicons 
            name="mic" 
            size={20} 
            color={activeTab === 'sirikit' ? '#007AFF' : '#666'} 
          />
          <Text style={[
            styles.tabText,
            activeTab === 'sirikit' && styles.tabTextActive
          ]}>
            SiriKit
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.tab,
            activeTab === 'airplay' && styles.tabActive
          ]}
          onPress={() => setActiveTab('airplay')}
        >
          <Ionicons 
            name="wifi" 
            size={20} 
            color={activeTab === 'airplay' ? '#007AFF' : '#666'} 
          />
          <Text style={[
            styles.tabText,
            activeTab === 'airplay' && styles.tabTextActive
          ]}>
            AirPlay 2
          </Text>
        </TouchableOpacity>
      </View>

      {/* Feature Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {activeTab === 'sirikit' ? (
          <View style={styles.featureContainer}>
            <SiriKitIntegration
              onVoiceCommand={handleSiriVoiceCommand}
            />
          </View>
        ) : (
          <View style={styles.featureContainer}>
            <EnhancedAirPlayInterface
              currentlyPlaying={currentlyPlaying}
              onDeviceChange={handleAirPlayDeviceChange}
              onGroupChange={handleAirPlayGroupChange}
            />
          </View>
        )}
      </ScrollView>

      {/* Quick Feature Overview */}
      <View style={styles.quickOverview}>
        <Text style={styles.overviewTitle}>Apple Features Overview</Text>
        
        <View style={styles.overviewGrid}>
          <View style={styles.overviewItem}>
            <Ionicons name="mic" size={16} color="#007AFF" />
            <Text style={styles.overviewText}>Advanced Voice Commands</Text>
          </View>
          
          <View style={styles.overviewItem}>
            <Ionicons name="language" size={16} color="#007AFF" />
            <Text style={styles.overviewText}>Multi-language Support</Text>
          </View>
          
          <View style={styles.overviewItem}>
            <Ionicons name="wifi" size={16} color="#007AFF" />
            <Text style={styles.overviewText}>Multi-room Audio</Text>
          </View>
          
          <View style={styles.overviewItem}>
            <Ionicons name="musical-notes" size={16} color="#007AFF" />
            <Text style={styles.overviewText}>Lossless Streaming</Text>
          </View>
          
          <View style={styles.overviewItem}>
            <Ionicons name="location" size={16} color="#007AFF" />
            <Text style={styles.overviewText}>Location-aware Suggestions</Text>
          </View>
          
          <View style={styles.overviewItem}>
            <Ionicons name="download" size={16} color="#007AFF" />
            <Text style={styles.overviewText}>Offline Content</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  unavailableContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#f8f9fa',
  },
  unavailableTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1d1d1d',
    marginTop: 16,
    marginBottom: 8,
  },
  unavailableText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 8,
  },
  unavailableSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    lineHeight: 20,
    fontStyle: 'italic',
  },
  header: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerText: {
    marginLeft: 12,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1d1d1d',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  featureBadges: {
    flexDirection: 'row',
    gap: 8,
  },
  badge: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeText: {
    fontSize: 11,
    color: '#007AFF',
    fontWeight: '600',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingTop: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 12,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#007AFF',
  },
  tabText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    marginLeft: 6,
  },
  tabTextActive: {
    color: '#007AFF',
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  featureContainer: {
    flex: 1,
  },
  quickOverview: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: '#e1e8ed',
  },
  overviewTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 12,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  overviewItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  overviewText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
    fontWeight: '500',
  },
});

export default AppleFeaturesDashboard;