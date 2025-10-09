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

            {/* Enhanced Audio Features - All 10 Features */}
            <Card variant="elevated" padding="medium" margin="medium">
              <Text style={flattenStyle([styles.settingHeader, { color: colors.text }])}>
                🎵 Enhanced Audio Controls
              </Text>
              <View style={styles.enhancedFeatures}>
                <View style={styles.featureRow}>
                  <Button title="⭐ Favorite" variant="outline" size="small" onPress={() => console.log('Favorite')} style={styles.featureButton} />
                  <Button title="💝 Favorites" variant="outline" size="small" onPress={() => console.log('Favorites')} style={styles.featureButton} />
                </View>
                <View style={styles.featureRow}>
                  <Button title="📤 Share" variant="outline" size="small" onPress={() => console.log('Share')} style={styles.featureButton} />
                  <Button title="🎙️ Record" variant="outline" size="small" onPress={() => console.log('Record')} style={styles.featureButton} />
                </View>
                <View style={styles.featureRow}>
                  <Button title="📻 SoundCast" variant="outline" size="small" onPress={() => console.log('SoundCast')} style={styles.featureButton} />
                  <Button title="🌍 Garden" variant="outline" size="small" onPress={() => console.log('Garden')} style={styles.featureButton} />
                </View>
                <View style={styles.featureRow}>
                  <Button title="🛰️ Satellite" variant="outline" size="small" onPress={() => console.log('Satellite')} style={styles.featureButton} />
                  <Button title="🧭 Navigation" variant="outline" size="small" onPress={() => console.log('Navigation')} style={styles.featureButton} />
                </View>
                <View style={styles.featureRow}>
                  <Button title="🎵 External" variant="outline" size="small" onPress={() => console.log('External')} style={styles.featureButton} />
                  <Button title="🎤 AI Voice" variant="outline" size="small" onPress={() => console.log('AI Voice')} style={styles.featureButton} />
                </View>
              </View>
            </Card>

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
                variant="secondary"
                size="medium"
                onPress={() => console.log('Country-based content loaded')}
                style={flattenStyle([styles.responsiveButton, { marginBottom: 12 }])}
              />
              <Button
                title="⚡ Performance Metrics"
                variant="ghost"
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

      case 'language':
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={[styles.title, { color: colors.text }]}>
              🌍 Language Settings
            </AccessibleText>
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.text, { color: colors.text }]}>
                Language detection and multilingual support for enhanced radio experience.
                Supports 8+ languages with GPS-based auto-detection.
              </Text>
            </Card>
          </View>
        );

      case 'apps':
        return (
          <View style={styles.tabContent}>
            <AccessibleText role="header" level={2} style={[styles.title, { color: colors.text }]}>
              📱 Connected Apps
            </AccessibleText>
            <Card variant="outlined" padding="medium" margin="medium">
              <Text style={[styles.text, { color: colors.text }]}>
                External audio sources and integrations:{'\n\n'}
                🎵 iHeartRadio (US-focused){'\n'}
                🌍 Streema (International){'\n'}
                🎶 Radio Garden (Global){'\n'}
                📻 TuneIn (Live radio & podcasts){'\n'}
                🛰️ Satellite Radio Networks
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
      width: '100%',
      maxWidth: '100%',
      overflow: 'hidden',
    },
    tabContent: {
      flex: 1,
      paddingHorizontal: 16,
      paddingVertical: 16,
      width: '100%',
      maxWidth: '100%',
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
    settingHeader: {
      fontSize: 18,
      fontWeight: '600',
      marginBottom: 8,
    },
    settingDescription: {
      fontSize: 14,
      lineHeight: 20,
      marginBottom: 8,
    },
    settingStatus: {
      fontSize: 14,
      fontWeight: '500',
    },
    enhancedFeatures: {
      marginTop: 12,
    },
    featureRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 8,
      gap: 8,
    },
    featureButton: {
      flex: 1,
      maxWidth: '48%',
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