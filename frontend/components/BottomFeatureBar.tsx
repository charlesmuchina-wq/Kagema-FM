import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Feature {
  id: string;
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  color: string;
}

interface BottomFeatureBarProps {
  features: Feature[];
  activeFeatures: string[];
  onToggleFeature: (featureId: string) => void;
  currentStation: any;
}

export const BottomFeatureBar: React.FC<BottomFeatureBarProps> = ({
  features,
  activeFeatures,
  onToggleFeature,
  currentStation,
}) => {
  return (
    <View style={styles.container}>
      {/* Now Playing Mini Bar */}
      {currentStation && (
        <View style={styles.nowPlayingMini}>
          <View style={styles.dragonIcon}>
            <Text style={styles.dragonEmoji}>🐉</Text>
          </View>
          <View style={styles.trackInfo}>
            <Text style={styles.trackTitle} numberOfLines={1}>
              {currentStation.name}
            </Text>
            <Text style={styles.trackArtist} numberOfLines={1}>
              {currentStation.country} • Live
            </Text>
          </View>
          <View style={styles.liveIndicator}>
            <View style={styles.liveDot} />
            <Text style={styles.liveText}>LIVE</Text>
          </View>
        </View>
      )}

      {/* Feature Toggles */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.featuresScroll}
      >
        {features.map((feature) => {
          const isActive = activeFeatures.includes(feature.id);
          return (
            <TouchableOpacity
              key={feature.id}
              style={[
                styles.featureButton,
                isActive && { backgroundColor: feature.color, borderColor: feature.color },
              ]}
              onPress={() => onToggleFeature(feature.id)}
              activeOpacity={0.7}
            >
              <Ionicons
                name={feature.icon}
                size={20}
                color={isActive ? '#FFFFFF' : feature.color}
              />
              <Text
                style={[
                  styles.featureLabel,
                  isActive && styles.featureLabelActive,
                ]}
              >
                {feature.label}
              </Text>
              {isActive && <View style={styles.activeIndicator} />}
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(10, 14, 39, 0.98)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 107, 53, 0.3)',
    paddingBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  nowPlayingMini: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(139, 146, 176, 0.2)',
  },
  dragonIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 107, 53, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  dragonEmoji: {
    fontSize: 24,
  },
  trackInfo: {
    flex: 1,
    marginRight: 12,
  },
  trackTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 2,
  },
  trackArtist: {
    fontSize: 12,
    color: '#8B92B0',
  },
  liveIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 107, 53, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#FF6B35',
  },
  liveText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FF6B35',
    letterSpacing: 1,
  },
  featuresScroll: {
    paddingHorizontal: 12,
    paddingVertical: 12,
    gap: 8,
  },
  featureButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: 'rgba(139, 146, 176, 0.3)',
    backgroundColor: 'rgba(26, 31, 58, 0.6)',
    marginRight: 8,
    gap: 6,
  },
  featureLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#8B92B0',
  },
  featureLabelActive: {
    color: '#FFFFFF',
  },
  activeIndicator: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#FFFFFF',
    marginLeft: 4,
  },
});
