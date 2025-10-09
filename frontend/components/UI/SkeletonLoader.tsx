import React, { useEffect } from 'react';
import {
  View,
  StyleSheet,
  Animated,
  ViewStyle,
  Dimensions,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

const { width: screenWidth } = Dimensions.get('window');

interface SkeletonProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
  animated?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = 20,
  borderRadius = 4,
  style,
  animated = true,
}) => {
  const { colors } = useTheme();
  const animatedValue = new Animated.Value(0);

  useEffect(() => {
    if (animated) {
      const animation = Animated.loop(
        Animated.sequence([
          Animated.timing(animatedValue, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: false,
          }),
          Animated.timing(animatedValue, {
            toValue: 0,
            duration: 1000,
            useNativeDriver: false,
          }),
        ])
      );
      animation.start();
      return () => animation.stop();
    }
  }, [animated]);

  const backgroundColor = animated
    ? animatedValue.interpolate({
        inputRange: [0, 1],
        outputRange: [colors.surface, colors.border],
      })
    : colors.surface;

  return (
    <Animated.View
      style={[
        {
          width,
          height,
          borderRadius,
          backgroundColor,
        },
        style,
      ]}
    />
  );
};

// Radio Station Skeleton
export const RadioStationSkeleton: React.FC = () => {
  const { colors } = useTheme();

  return (
    <View style={[styles.stationContainer, { backgroundColor: colors.card }]}>
      {/* Station Image */}
      <Skeleton
        width={60}
        height={60}
        borderRadius={12}
        style={{ marginRight: 16 }}
      />
      
      {/* Station Info */}
      <View style={styles.stationInfo}>
        <Skeleton width="80%" height={18} style={{ marginBottom: 8 }} />
        <Skeleton width="60%" height={14} style={{ marginBottom: 6 }} />
        <Skeleton width="40%" height={12} />
      </View>
      
      {/* Play Button */}
      <Skeleton width={40} height={40} borderRadius={20} />
    </View>
  );
};

// News Article Skeleton
export const NewsArticleSkeleton: React.FC = () => {
  const { colors } = useTheme();

  return (
    <View style={[styles.newsContainer, { backgroundColor: colors.card }]}>
      {/* News Image */}
      <Skeleton
        width="100%"
        height={200}
        borderRadius={12}
        style={{ marginBottom: 16 }}
      />
      
      {/* News Content */}
      <View style={styles.newsContent}>
        <Skeleton width="90%" height={20} style={{ marginBottom: 8 }} />
        <Skeleton width="100%" height={16} style={{ marginBottom: 6 }} />
        <Skeleton width="70%" height={16} style={{ marginBottom: 12 }} />
        
        {/* Meta Info */}
        <View style={styles.newsMeta}>
          <Skeleton width={80} height={12} style={{ marginRight: 16 }} />
          <Skeleton width={60} height={12} />
        </View>
      </View>
    </View>
  );
};

// Music Track Skeleton
export const MusicTrackSkeleton: React.FC = () => {
  const { colors } = useTheme();

  return (
    <View style={[styles.trackContainer, { backgroundColor: colors.card }]}>
      {/* Album Art */}
      <Skeleton
        width={50}
        height={50}
        borderRadius={8}
        style={{ marginRight: 12 }}
      />
      
      {/* Track Info */}
      <View style={styles.trackInfo}>
        <Skeleton width="70%" height={16} style={{ marginBottom: 4 }} />
        <Skeleton width="50%" height={14} style={{ marginBottom: 4 }} />
        <Skeleton width="30%" height={12} />
      </View>
      
      {/* Actions */}
      <View style={styles.trackActions}>
        <Skeleton width={24} height={24} borderRadius={12} style={{ marginRight: 8 }} />
        <Skeleton width={24} height={24} borderRadius={12} />
      </View>
    </View>
  );
};

// Audio Player Skeleton
export const AudioPlayerSkeleton: React.FC = () => {
  const { colors } = useTheme();

  return (
    <View style={[styles.playerContainer, { backgroundColor: colors.card }]}>
      {/* Track Info */}
      <View style={styles.playerTrackInfo}>
        <Skeleton width="60%" height={18} style={{ marginBottom: 6 }} />
        <Skeleton width="40%" height={14} />
      </View>
      
      {/* Waveform */}
      <View style={styles.waveformSkeleton}>
        {Array.from({ length: 12 }).map((_, index) => (
          <Skeleton
            key={index}
            width={4}
            height={Math.random() * 20 + 10}
            style={{ marginHorizontal: 2 }}
          />
        ))}
      </View>
      
      {/* Controls */}
      <View style={styles.playerControls}>
        <Skeleton width={40} height={40} borderRadius={20} />
        <Skeleton width={60} height={60} borderRadius={30} style={{ marginHorizontal: 20 }} />
        <Skeleton width={40} height={40} borderRadius={20} />
      </View>
      
      {/* Progress Bar */}
      <View style={styles.progressSkeleton}>
        <Skeleton width="100%" height={4} borderRadius={2} style={{ marginVertical: 8 }} />
        <View style={styles.timeLabels}>
          <Skeleton width={30} height={12} />
          <Skeleton width={30} height={12} />
        </View>
      </View>
    </View>
  );
};

// Country List Skeleton
export const CountryListSkeleton: React.FC = () => {
  return (
    <View>
      {Array.from({ length: 8 }).map((_, index) => (
        <View key={index} style={styles.countryItem}>
          <Skeleton width={32} height={32} borderRadius={16} style={{ marginRight: 12 }} />
          <View style={styles.countryInfo}>
            <Skeleton width="70%" height={16} style={{ marginBottom: 4 }} />
            <Skeleton width="40%" height={12} />
          </View>
          <Skeleton width={20} height={20} borderRadius={10} />
        </View>
      ))}
    </View>
  );
};

// Grid Skeleton (for featured content)
export const GridSkeleton: React.FC<{ columns?: number; items?: number }> = ({
  columns = 2,
  items = 6,
}) => {
  const { colors } = useTheme();
  const itemWidth = (screenWidth - 48 - (columns - 1) * 16) / columns;

  return (
    <View style={styles.gridContainer}>
      {Array.from({ length: items }).map((_, index) => (
        <View
          key={index}
          style={[
            styles.gridItem,
            {
              width: itemWidth,
              backgroundColor: colors.card,
              marginRight: index % columns === columns - 1 ? 0 : 16,
            },
          ]}
        >
          <Skeleton
            width="100%"
            height={itemWidth * 0.75}
            borderRadius={12}
            style={{ marginBottom: 12 }}
          />
          <Skeleton width="80%" height={16} style={{ marginBottom: 6 }} />
          <Skeleton width="60%" height={12} />
        </View>
      ))}
    </View>
  );
};

// Card List Skeleton
export const CardListSkeleton: React.FC<{ items?: number }> = ({ items = 5 }) => {
  const { colors } = useTheme();

  return (
    <View>
      {Array.from({ length: items }).map((_, index) => (
        <View
          key={index}
          style={[styles.cardSkeleton, { backgroundColor: colors.card }]}
        >
          <Skeleton width="100%" height={120} borderRadius={12} style={{ marginBottom: 16 }} />
          <Skeleton width="90%" height={18} style={{ marginBottom: 8 }} />
          <Skeleton width="70%" height={14} style={{ marginBottom: 8 }} />
          <View style={styles.cardFooter}>
            <Skeleton width={60} height={12} />
            <Skeleton width={40} height={12} />
          </View>
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  stationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 12,
  },
  stationInfo: {
    flex: 1,
  },
  newsContainer: {
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
  },
  newsContent: {
    flex: 1,
  },
  newsMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trackContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 8,
  },
  trackInfo: {
    flex: 1,
  },
  trackActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  playerContainer: {
    padding: 20,
    margin: 16,
    borderRadius: 16,
  },
  playerTrackInfo: {
    alignItems: 'center',
    marginBottom: 16,
  },
  waveformSkeleton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 40,
    marginVertical: 16,
  },
  playerControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 20,
  },
  progressSkeleton: {
    marginTop: 16,
  },
  timeLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  countryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  countryInfo: {
    flex: 1,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
  },
  gridItem: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  cardSkeleton: {
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
});