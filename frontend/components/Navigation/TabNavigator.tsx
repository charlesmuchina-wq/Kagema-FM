import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
  Platform,
  AccessibilityInfo,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';
import { shadowStyles } from '../../utils/shadowStyles';
import { 
  PerformanceMonitor, 
  useOptimizedCallback, 
  useOptimizedMemo 
} from '../../utils/performance';

const { width } = Dimensions.get('window');

export type TabName = 'radio' | 'news' | 'music' | 'language' | 'apps' | 'settings';

interface TabConfig {
  name: TabName;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  activeIcon?: keyof typeof Ionicons.glyphMap;
  badge?: number;
}

interface TabNavigatorProps {
  activeTab: TabName;
  onTabChange: (tab: TabName) => void;
  tabs?: TabConfig[];
  style?: any;
  showLabels?: boolean;
  orientation?: 'bottom' | 'top';
}

const defaultTabs: TabConfig[] = [
  { 
    name: 'radio', 
    label: 'Radio', 
    icon: 'radio',
    activeIcon: 'radio',
  },
  { 
    name: 'news', 
    label: 'News', 
    icon: 'newspaper-outline',
    activeIcon: 'newspaper',
  },
  { 
    name: 'music', 
    label: 'Music', 
    icon: 'musical-notes-outline',
    activeIcon: 'musical-notes',
  },
  { 
    name: 'language', 
    label: 'Language', 
    icon: 'language-outline',
    activeIcon: 'language',
  },
  { 
    name: 'apps', 
    label: 'Apps', 
    icon: 'apps-outline',
    activeIcon: 'apps',
  },
  { 
    name: 'settings', 
    label: 'Settings', 
    icon: 'settings-outline',
    activeIcon: 'settings',
  },
];

export const TabNavigator: React.FC<TabNavigatorProps> = ({
  activeTab,
  onTabChange,
  tabs = defaultTabs,
  style,
  showLabels = true,
  orientation = 'bottom',
}) => {
  const { colors } = useTheme();
  
  // Animation values
  const tabAnimations = useRef(
    tabs.reduce((acc, tab) => {
      acc[tab.name] = new Animated.Value(0);
      return acc;
    }, {} as Record<TabName, Animated.Value>)
  ).current;

  const indicatorPosition = useRef(new Animated.Value(0)).current;
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);

  // Check accessibility settings
  useEffect(() => {
    const checkAccessibility = async () => {
      const enabled = await AccessibilityInfo.isScreenReaderEnabled();
      setAccessibilityEnabled(enabled);
    };
    checkAccessibility();

    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      setAccessibilityEnabled
    );

    return () => subscription?.remove();
  }, []);

  // Animate indicator position when active tab changes
  useEffect(() => {
    const activeIndex = tabs.findIndex(tab => tab.name === activeTab);
    const tabWidth = width / tabs.length;
    
    Animated.spring(indicatorPosition, {
      toValue: activeIndex * tabWidth,
      useNativeDriver: false,
      tension: 100,
      friction: 8,
    }).start();

    // Animate active tab
    Object.keys(tabAnimations).forEach(tabName => {
      Animated.timing(tabAnimations[tabName as TabName], {
        toValue: tabName === activeTab ? 1 : 0,
        duration: 200,
        useNativeDriver: true,
      }).start();
    });
  }, [activeTab, tabs, indicatorPosition, tabAnimations]);

  // Optimized tab press handler
  const handleTabPress = useOptimizedCallback((tabName: TabName) => {
    PerformanceMonitor.start(`tab-switch-${tabName}`);
    
    // Haptic feedback for native platforms
    if (Platform.OS !== 'web') {
      // Could add haptic feedback here
    }
    
    onTabChange(tabName);
    PerformanceMonitor.end(`tab-switch-${tabName}`);
  }, [onTabChange]);

  // Optimized tab renderer
  const renderTab = useOptimizedCallback((tab: TabConfig, index: number) => {
    const isActive = tab.name === activeTab;
    const animation = tabAnimations[tab.name];
    const tabWidth = width / tabs.length;
    
    const iconName = isActive && tab.activeIcon ? tab.activeIcon : tab.icon;
    const iconColor = isActive ? colors.primary : colors.textSecondary;
    const labelColor = isActive ? colors.primary : colors.textSecondary;
    
    return (
      <TouchableOpacity
        key={tab.name}
        style={[
          styles.tab,
          { 
            width: tabWidth,
            minHeight: showLabels ? 60 : 50,
          }
        ]}
        onPress={() => handleTabPress(tab.name)}
        accessibilityRole="tab"
        accessibilityState={{ selected: isActive }}
        accessibilityLabel={`${tab.label} tab${isActive ? ', selected' : ''}`}
        accessibilityHint={`Navigate to ${tab.label} section`}
        activeOpacity={0.7}
      >
        <Animated.View
          style={[
            styles.tabContent,
            {
              transform: [{
                scale: animation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [1, 1.1],
                }),
              }],
            },
          ]}
        >
          <View style={styles.iconContainer}>
            <Ionicons 
              name={iconName} 
              size={24} 
              color={iconColor}
            />
            {tab.badge && tab.badge > 0 && (
              <View style={[styles.badge, { backgroundColor: colors.error }]}>
                <Text style={styles.badgeText}>
                  {tab.badge > 99 ? '99+' : tab.badge}
                </Text>
              </View>
            )}
          </View>
          
          {showLabels && (
            <Animated.Text
              style={[
                styles.tabLabel,
                {
                  color: labelColor,
                  opacity: animation.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0.8, 1],
                  }),
                  fontSize: animation.interpolate({
                    inputRange: [0, 1],
                    outputRange: [11, 12],
                  }),
                },
              ]}
              numberOfLines={1}
            >
              {tab.label}
            </Animated.Text>
          )}
        </Animated.View>
      </TouchableOpacity>
    );
  }, [
    activeTab, 
    tabAnimations, 
    tabs.length, 
    colors, 
    showLabels, 
    handleTabPress
  ]);

  // Memoized tab bar style
  const tabBarStyle = useOptimizedMemo(() => [
    styles.container,
    orientation === 'top' ? styles.topOrientation : styles.bottomOrientation,
    {
      backgroundColor: colors.surface,
      borderTopColor: orientation === 'bottom' ? colors.border : 'transparent',
      borderBottomColor: orientation === 'top' ? colors.border : 'transparent',
    },
    ...shadowStyles.small,
    style,
  ], [colors, orientation, style]);

  // Memoized indicator style
  const indicatorStyle = useOptimizedMemo(() => [
    styles.indicator,
    {
      backgroundColor: colors.primary,
      width: width / tabs.length,
      transform: [{ translateX: indicatorPosition }],
    },
  ], [colors.primary, tabs.length, indicatorPosition]);

  return (
    <View style={tabBarStyle}>
      {/* Active tab indicator */}
      <Animated.View style={indicatorStyle} />
      
      {/* Tab buttons */}
      <View style={styles.tabsContainer}>
        {tabs.map((tab, index) => renderTab(tab, index))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'column',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  topOrientation: {
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderTopWidth: 0,
  },
  bottomOrientation: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderBottomWidth: 0,
  },
  indicator: {
    position: 'absolute',
    top: 0,
    height: 3,
    borderRadius: 1.5,
  },
  tabsContainer: {
    flexDirection: 'row',
    paddingTop: 3,
  },
  tab: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 8,
  },
  tabContent: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    position: 'relative',
    marginBottom: 4,
  },
  badge: {
    position: 'absolute',
    top: -6,
    right: -6,
    minWidth: 16,
    height: 16,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 4,
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '600',
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '500',
    textAlign: 'center',
  },
});