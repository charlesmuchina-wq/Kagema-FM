import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, StatusBar } from 'react-native';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';
import { StatusBar as ExpoStatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Import Enhanced Components
import { TabNavigator } from '../components/Navigation/TabNavigator';
import { CountryPicker } from '../components/UI/CountryPicker';
import { Button } from '../components/UI/Button';
import { Card } from '../components/UI/Card';
import { AccessibleText } from '../components/UI/AccessibilityHelpers';

// Temporarily use simple RefreshControl instead of enhanced one
import { ScrollView, RefreshControl } from 'react-native';

type TabName = 'radio' | 'news' | 'music' | 'language' | 'apps' | 'settings';

function EnhancedMainApp() {
  const { colors, isDark } = useTheme();
  const [activeTab, setActiveTab] = useState<TabName>('radio');
  const [selectedCountry, setSelectedCountry] = useState<string>('US');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh
    setTimeout(() => setRefreshing(false), 2000);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'radio':
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={flattenStyle([styles.title, { color: colors.text }])}>
              🎵 Enhanced Radio Experience
            </AccessibleText>
            
            <Card variant="elevated" padding="medium" margin="medium">
              <Text style={flattenStyle([styles.text, { color: colors.text }])}>
                🎯 Phase 3 & 4 UI/UX Enhancements Active!
              </Text>
              <Text style={flattenStyle([styles.subtitle, { color: colors.textSecondary }])}>
                • Enhanced Audio Controls with Animations{'\n'}
                • Mobile-Optimized Country Selection{'\n'}
                • Accessibility Features & Haptic Feedback{'\n'}
                • Performance Optimizations{'\n'}
                • Advanced Caching & Memory Management
              </Text>
            </Card>

            <CountryPicker
              selectedCountry={selectedCountry}
              onCountrySelect={(country) => setSelectedCountry(country.code)}
              placeholder="Select your country"
              showRegionFilter={true}
            />

            <View style={styles.features}>
              <Button
                title="🎧 Enhanced Audio Player"
                variant="primary"
                size="medium"
                onPress={() => console.log('Enhanced Audio Player activated')}
                style={flattenStyle([styles.responsiveButton, { marginBottom: 12 }])}
              />
              <Button
                title="🌍 Country-Based Content"
                variant="outline"
                size="medium"
                onPress={() => console.log('Country-based content loaded')}
                style={flattenStyle([styles.responsiveButton, { marginBottom: 12 }])}
              />
              <Button
                title="⚡ Performance Metrics"
                variant="secondary"
                size="medium"
                onPress={() => console.log('Performance metrics available')}
                style={flattenStyle([styles.responsiveButton])}
              />
            </View>
          </View>
        );

      case 'news':
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={[styles.title, { color: colors.text }]}>
              📰 Enhanced News
            </AccessibleText>
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.text, { color: colors.text }]}>
                News content with enhanced loading states and performance optimizations.
              </Text>
            </Card>
          </View>
        );

      case 'music':
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={[styles.title, { color: colors.text }]}>
              🎶 Enhanced Music
            </AccessibleText>
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.text, { color: colors.text }]}>
                Music library with enhanced audio controls and animations.
              </Text>
            </Card>
          </View>
        );

      case 'settings':
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={[styles.title, { color: colors.text }]}>
              ⚙️ Enhanced Settings
            </AccessibleText>
            
            {/* Car Mode Settings */}
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.settingHeader, { color: colors.text }]}>
                🚗 Car Mode
              </Text>
              <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                Automotive-optimized interface with large controls, voice commands, and driving safety features
              </Text>
              <Text style={[styles.settingStatus, { color: colors.accent }]}>
                Status: Inactive
              </Text>
            </Card>

            {/* Enhanced Player Settings */}
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.settingHeader, { color: colors.text }]}>
                🎵 Enhanced Player
              </Text>
              <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                Advanced audio player with enhanced controls and animations
              </Text>
              <Text style={[styles.settingStatus, { color: colors.accent }]}>
                Toggle: Off/On
              </Text>
            </Card>

            {/* Enhanced Features Status */}
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.settingHeader, { color: colors.text }]}>
                ✅ Phase 3 & 4 Enhancements
              </Text>
              <Text style={[styles.text, { color: colors.text }]}>
                📱 Mobile-First UI/UX Design{'\n'}
                🎨 Enhanced Animations & Transitions{'\n'}
                ♿ Comprehensive Accessibility{'\n'}
                ⚡ Advanced Performance Optimization{'\n'}
                🧠 Memory & Cache Management{'\n'}
                🔄 Smart Loading States
              </Text>
            </Card>
          </View>
        );

      default:
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={[styles.title, { color: colors.text }]}>
              🚀 Enhanced Experience
            </AccessibleText>
            <Text style={[styles.text, { color: colors.text }]}>
              Enhanced content for {activeTab} tab coming soon!
            </Text>
          </View>
        );
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    tabContent: {
      flex: 1,
      paddingHorizontal: 16,
      paddingVertical: 16,
    },
    title: {
      fontSize: 24,
      fontWeight: '600',
      marginBottom: 16,
      textAlign: 'center',
    },
    text: {
      fontSize: 16,
      lineHeight: 24,
    },
    subtitle: {
      fontSize: 14,
      lineHeight: 20,
      marginTop: 8,
    },
    features: {
      marginTop: 24,
      width: '100%',
    },
    responsiveButton: {
      width: '100%',
      maxWidth: '100%',
    },
  });

  // Helper function to safely flatten styles for React Native Web compatibility
  const flattenStyle = (style: any) => {
    if (Array.isArray(style)) {
      return StyleSheet.flatten(style);
    }
    return style;
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar
        barStyle={isDark ? 'light-content' : 'dark-content'}
        backgroundColor={colors.background}
      />
      
      <ScrollView
        style={{ flex: 1 }}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
          />
        }
      >
        {renderContent()}
      </ScrollView>

      <TabNavigator
        activeTab={activeTab}
        onTabChange={setActiveTab}
        showLabels={true}
      />
    </SafeAreaView>
  );
}

// Enhanced Main App Entry Point with Theme Provider
export default function EnhancedMain() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <ExpoStatusBar style="auto" />
        <EnhancedMainApp />
      </ThemeProvider>
    </SafeAreaProvider>
  );
}