import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface FeatureTileProps {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  tagline: string;
  color: string;
  onPress: () => void;
  style?: ViewStyle;
}

export const FeatureTile: React.FC<FeatureTileProps> = ({
  icon,
  title,
  tagline,
  color,
  onPress,
  style,
}) => {
  return (
    <TouchableOpacity
      style={[styles.tile, { borderColor: color }, style]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.iconContainer, { backgroundColor: color }]}>
        <Ionicons name={icon} size={32} color="#FFFFFF" />
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.tagline}>{tagline}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  tile: {
    width: 160,
    height: 180,
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 20,
    borderWidth: 2,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 4,
  },
  tagline: {
    fontSize: 12,
    color: '#8B92B0',
    textAlign: 'center',
  },
});
