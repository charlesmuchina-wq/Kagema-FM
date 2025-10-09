import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  RefreshControl,
  ScrollView,
  Dimensions,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';
import * as Haptics from 'expo-haptics';

const { height: screenHeight } = Dimensions.get('window');

interface EnhancedRefreshControlProps {
  children: React.ReactNode;
  onRefresh: () => Promise<void>;
  refreshing?: boolean;
  pullDownMessage?: string;
  refreshingMessage?: string;
  successMessage?: string;
  showProgressBar?: boolean;
  hapticFeedback?: boolean;
  customIndicator?: React.ReactNode;
  pullThreshold?: number;
}

export const EnhancedRefreshControl: React.FC<EnhancedRefreshControlProps> = ({
  children,
  onRefresh,
  refreshing = false,
  pullDownMessage = "Pull down to refresh",
  refreshingMessage = "Refreshing...",
  successMessage = "Updated successfully!",
  showProgressBar = true,
  hapticFeedback = true,
  customIndicator,
  pullThreshold = 80,
}) => {
  const { colors, isDark } = useTheme();
  const [isRefreshing, setIsRefreshing] = useState(refreshing);
  const [showSuccess, setShowSuccess] = useState(false);
  const [refreshProgress, setRefreshProgress] = useState(0);

  // Animation values
  const pulseAnimation = useRef(new Animated.Value(1)).current;
  const spinAnimation = useRef(new Animated.Value(0)).current;
  const progressAnimation = useRef(new Animated.Value(0)).current;
  const successAnimation = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    setIsRefreshing(refreshing);
  }, [refreshing]);

  // Pulse animation for pull indicator
  useEffect(() => {
    const pulseLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnimation, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnimation, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );

    if (isRefreshing) {
      pulseLoop.start();
    } else {
      pulseLoop.stop();
      pulseAnimation.setValue(1);
    }

    return () => pulseLoop.stop();
  }, [isRefreshing, pulseAnimation]);

  // Spin animation for loading indicator
  useEffect(() => {
    const spinLoop = Animated.loop(
      Animated.timing(spinAnimation, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: true,
      })
    );

    if (isRefreshing) {
      spinLoop.start();
    } else {
      spinLoop.stop();
      spinAnimation.setValue(0);
    }

    return () => spinLoop.stop();
  }, [isRefreshing, spinAnimation]);

  // Progress bar animation
  useEffect(() => {
    if (showProgressBar && isRefreshing) {
      Animated.timing(progressAnimation, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: false,
      }).start();
    } else {
      progressAnimation.setValue(0);
    }
  }, [isRefreshing, showProgressBar, progressAnimation]);

  // Success animation
  useEffect(() => {
    if (showSuccess) {
      Animated.sequence([
        Animated.timing(successAnimation, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.delay(2000),
        Animated.timing(successAnimation, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start(() => {
        setShowSuccess(false);
      });
    }
  }, [showSuccess, successAnimation]);

  const handleRefresh = async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    setRefreshProgress(0);

    // Haptic feedback
    if (hapticFeedback && Platform.OS !== 'web') {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    try {
      // Simulate progress updates
      if (showProgressBar) {
        const progressInterval = setInterval(() => {
          setRefreshProgress(prev => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return prev;
            }
            return prev + Math.random() * 20;
          });
        }, 200);
      }

      await onRefresh();

      // Complete progress
      if (showProgressBar) {
        setRefreshProgress(100);
      }

      // Show success message
      setShowSuccess(true);

      // Success haptic feedback
      if (hapticFeedback && Platform.OS !== 'web') {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
    } catch (error) {
      console.error('Refresh error:', error);
      
      // Error haptic feedback
      if (hapticFeedback && Platform.OS !== 'web') {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
    } finally {
      // Reset after a short delay
      setTimeout(() => {
        setIsRefreshing(false);
        setRefreshProgress(0);
      }, 500);
    }
  };

  const renderCustomIndicator = () => {
    if (customIndicator) {
      return customIndicator;
    }

    return (
      <View style={[styles.indicatorContainer, { backgroundColor: colors.surface }]}>
        {/* Animated Icon */}
        <Animated.View
          style={[
            styles.iconContainer,
            {
              transform: [
                { scale: pulseAnimation },
                {
                  rotate: spinAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0deg', '360deg'],
                  }),
                },
              ],
            },
          ]}
        >
          <Ionicons
            name={isRefreshing ? 'sync' : 'arrow-down'}
            size={24}
            color={colors.primary}
          />
        </Animated.View>

        {/* Status Text */}
        <Text style={[styles.statusText, { color: colors.text }]}>
          {isRefreshing ? refreshingMessage : pullDownMessage}
        </Text>

        {/* Progress Bar */}
        {showProgressBar && isRefreshing && (
          <View style={[styles.progressBarContainer, { backgroundColor: colors.border }]}>
            <Animated.View
              style={[
                styles.progressBar,
                {
                  backgroundColor: colors.primary,
                  width: progressAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0%', '100%'],
                  }),
                },
              ]}
            />
          </View>
        )}

        {/* Progress Percentage */}
        {showProgressBar && isRefreshing && (
          <Text style={[styles.progressText, { color: colors.textSecondary }]}>
            {Math.round(refreshProgress)}%
          </Text>
        )}
      </View>
    );
  };

  const renderSuccessMessage = () => {
    if (!showSuccess) return null;

    return (
      <Animated.View
        style={[
          styles.successContainer,
          {
            backgroundColor: colors.success + '20',
            borderColor: colors.success,
            opacity: successAnimation,
            transform: [
              {
                translateY: successAnimation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [-50, 0],
                }),
              },
            ],
          },
        ]}
      >
        <Ionicons name="checkmark-circle" size={20} color={colors.success} />
        <Text style={[styles.successText, { color: colors.success }]}>
          {successMessage}
        </Text>
      </Animated.View>
    );
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
    },
    indicatorContainer: {
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 20,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
    },
    iconContainer: {
      marginBottom: 8,
    },
    statusText: {
      fontSize: 14,
      fontWeight: '500',
      textAlign: 'center',
      marginBottom: 12,
    },
    progressBarContainer: {
      width: 200,
      height: 3,
      borderRadius: 2,
      overflow: 'hidden',
      marginBottom: 8,
    },
    progressBar: {
      height: '100%',
      borderRadius: 2,
    },
    progressText: {
      fontSize: 12,
      fontWeight: '500',
    },
    successContainer: {
      position: 'absolute',
      top: Platform.OS === 'ios' ? 100 : 80,
      left: 20,
      right: 20,
      zIndex: 1000,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 12,
      paddingHorizontal: 16,
      borderRadius: 8,
      borderWidth: 1,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 4,
    },
    successText: {
      fontSize: 14,
      fontWeight: '500',
      marginLeft: 8,
    },
  });

  // Enhanced RefreshControl
  const enhancedRefreshControl = (
    <RefreshControl
      refreshing={isRefreshing}
      onRefresh={handleRefresh}
      colors={[colors.primary]}
      tintColor={colors.primary}
      title={isRefreshing ? refreshingMessage : pullDownMessage}
      titleColor={colors.text}
      progressBackgroundColor={colors.surface}
    />
  );

  return (
    <View style={styles.container}>
      {renderSuccessMessage()}
      
      <ScrollView
        style={{ flex: 1 }}
        refreshControl={enhancedRefreshControl}
        showsVerticalScrollIndicator={false}
        scrollEventThrottle={16}
      >
        {/* Custom indicator (only show when refreshing) */}
        {isRefreshing && renderCustomIndicator()}
        
        {children}
      </ScrollView>
    </View>
  );
};

// Simple wrapper for enhanced refresh functionality
interface RefreshableViewProps {
  children: React.ReactNode;
  onRefresh: () => Promise<void>;
  refreshing?: boolean;
  style?: any;
}

export const RefreshableView: React.FC<RefreshableViewProps> = ({
  children,
  onRefresh,
  refreshing = false,
  style,
}) => {
  return (
    <View style={[{ flex: 1 }, style]}>
      <EnhancedRefreshControl
        onRefresh={onRefresh}
        refreshing={refreshing}
        pullDownMessage="Pull to refresh content"
        refreshingMessage="Loading fresh content..."
        successMessage="Content updated!"
        showProgressBar={true}
        hapticFeedback={true}
      >
        {children}
      </EnhancedRefreshControl>
    </View>
  );
};