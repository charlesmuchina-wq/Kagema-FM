import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme, ThemeMode } from './theme-context';

const { width } = Dimensions.get('window');

export default function SettingsScreen() {
  const { theme, setThemeMode, toggleTheme } = useTheme();

  const themes: { mode: ThemeMode; label: string; icon: string; description: string }[] = [
    {
      mode: 'batik',
      label: 'Batik (Default)',
      icon: '🎨',
      description: 'Black & white minimalist mud cloth design',
    },
    {
      mode: 'dark',
      label: 'Dark Mode',
      icon: '🌙',
      description: 'Modern dark theme with purple accents',
    },
    {
      mode: 'light',
      label: 'Light Mode',
      icon: '☀️',
      description: 'Clean bright theme for daylight',
    },
  ];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]} edges={['top']}>
      <Stack.Screen 
        options={{
          title: 'Settings',
          headerShown: true,
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTintColor: theme.colors.text,
        }}
      />

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Theme Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Appearance
          </Text>
          <Text style={[styles.sectionDescription, { color: theme.colors.textSecondary }]}>
            Choose your preferred visual theme
          </Text>

          {themes.map((themeOption) => (
            <TouchableOpacity
              key={themeOption.mode}
              style={[
                styles.themeCard,
                { 
                  backgroundColor: theme.colors.surface,
                  borderColor: theme.mode === themeOption.mode ? theme.colors.accent : theme.colors.border,
                },
              ]}
              onPress={() => setThemeMode(themeOption.mode)}
              activeOpacity={0.8}
            >
              <View style={styles.themeHeader}>
                <Text style={styles.themeIcon}>{themeOption.icon}</Text>
                <View style={styles.themeInfo}>
                  <Text style={[styles.themeLabel, { color: theme.colors.text }]}>
                    {themeOption.label}
                  </Text>
                  <Text style={[styles.themeDescription, { color: theme.colors.textSecondary }]}>
                    {themeOption.description}
                  </Text>
                </View>
                {theme.mode === themeOption.mode && (
                  <Ionicons name="checkmark-circle" size={28} color={theme.colors.accent} />
                )}
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Quick Toggle Button */}
        <TouchableOpacity
          style={[styles.toggleButton, { backgroundColor: theme.colors.accent }]}
          onPress={toggleTheme}
        >
          <Ionicons name="color-palette" size={24} color="#FFFFFF" />
          <Text style={styles.toggleButtonText}>Quick Theme Toggle</Text>
        </TouchableOpacity>

        {/* App Info Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            About
          </Text>
          
          <View style={[styles.infoCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <Text style={[styles.appName, { color: theme.colors.text }]}>
              Dragon KARAU AI Radio
            </Text>
            <Text style={[styles.appVersion, { color: theme.colors.textSecondary }]}>
              Version 5.0.0
            </Text>
            <Text style={[styles.appDescription, { color: theme.colors.textSecondary }]}>
              Global internet radio with AI-powered features, live traffic integration, and intelligent search
            </Text>
          </View>
        </View>

        {/* Features List */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Features
          </Text>
          
          <View style={[styles.featureCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <FeatureItem icon="heart" text="Favorites System" theme={theme} />
            <FeatureItem icon="sparkles" text="AI Smart Search" theme={theme} />
            <FeatureItem icon="map" text="Radio Map & Traffic" theme={theme} />
            <FeatureItem icon="globe" text="Multi-Source Crawler" theme={theme} />
            <FeatureItem icon="share-social" text="Collection Sharing" theme={theme} />
            <FeatureItem icon="download" text="Import/Export" theme={theme} />
          </View>
        </View>

        {/* Map Providers */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Integrated Services
          </Text>
          
          <View style={[styles.providerCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <ProviderItem name="TomTom" status="Active" icon="🗺️" theme={theme} />
            <ProviderItem name="Google Maps" status="Ready" icon="🌍" theme={theme} />
            <ProviderItem name="Mapbox" status="Ready" icon="🎨" theme={theme} />
            <ProviderItem name="OpenStreetMap" status="Active" icon="🆓" theme={theme} />
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function FeatureItem({ icon, text, theme }: { icon: string; text: string; theme: any }) {
  return (
    <View style={styles.featureItem}>
      <Ionicons name={icon as any} size={20} color={theme.colors.accent} />
      <Text style={[styles.featureText, { color: theme.colors.text }]}>{text}</Text>
    </View>
  );
}

function ProviderItem({ name, status, icon, theme }: { name: string; status: string; icon: string; theme: any }) {
  return (
    <View style={styles.providerItem}>
      <Text style={styles.providerIcon}>{icon}</Text>
      <View style={styles.providerInfo}>
        <Text style={[styles.providerName, { color: theme.colors.text }]}>{name}</Text>
        <Text style={[styles.providerStatus, { color: theme.colors.textSecondary }]}>{status}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    marginBottom: 16,
    lineHeight: 20,
  },
  themeCard: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
  },
  themeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  themeIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  themeInfo: {
    flex: 1,
  },
  themeLabel: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  themeDescription: {
    fontSize: 13,
  },
  toggleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
    padding: 16,
    marginBottom: 32,
    gap: 8,
  },
  toggleButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  infoCard: {
    borderRadius: 16,
    padding: 20,
    borderWidth: 2,
  },
  appName: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  appVersion: {
    fontSize: 14,
    marginBottom: 12,
  },
  appDescription: {
    fontSize: 14,
    lineHeight: 20,
  },
  featureCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 2,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    gap: 12,
  },
  featureText: {
    fontSize: 16,
    fontWeight: '500',
  },
  providerCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 2,
  },
  providerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    gap: 12,
  },
  providerIcon: {
    fontSize: 24,
  },
  providerInfo: {
    flex: 1,
  },
  providerName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  providerStatus: {
    fontSize: 13,
  },
});
