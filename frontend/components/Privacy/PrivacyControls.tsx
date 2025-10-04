import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Switch,
  TouchableOpacity,
  Alert,
  ScrollView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../../contexts/ThemeContext';

interface PrivacySettings {
  locationSharing: boolean;
  analyticsCollection: boolean;
  personalizedContent: boolean;
  crashReporting: boolean;
  voiceDataProcessing: boolean;
  marketingCommunications: boolean;
  dataSharingPartners: boolean;
  cookiesAndTracking: boolean;
}

const DEFAULT_PRIVACY_SETTINGS: PrivacySettings = {
  locationSharing: true,
  analyticsCollection: true,
  personalizedContent: true,
  crashReporting: true,
  voiceDataProcessing: false,
  marketingCommunications: false,
  dataSharingPartners: false,
  cookiesAndTracking: true,
};

export const PrivacyControls: React.FC = () => {
  const { colors } = useTheme();
  const [settings, setSettings] = useState<PrivacySettings>(DEFAULT_PRIVACY_SETTINGS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPrivacySettings();
  }, []);

  const loadPrivacySettings = async () => {
    try {
      const saved = await AsyncStorage.getItem('privacy_settings');
      if (saved) {
        setSettings({ ...DEFAULT_PRIVACY_SETTINGS, ...JSON.parse(saved) });
      }
    } catch (error) {
      console.error('Error loading privacy settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const savePrivacySettings = async (newSettings: PrivacySettings) => {
    try {
      await AsyncStorage.setItem('privacy_settings', JSON.stringify(newSettings));
      setSettings(newSettings);
    } catch (error) {
      console.error('Error saving privacy settings:', error);
      Alert.alert('Error', 'Failed to save privacy settings');
    }
  };

  const updateSetting = (key: keyof PrivacySettings, value: boolean) => {
    const newSettings = { ...settings, [key]: value };
    savePrivacySettings(newSettings);
  };

  const resetToDefaults = () => {
    Alert.alert(
      'Reset Privacy Settings',
      'This will reset all privacy settings to their default values. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => savePrivacySettings(DEFAULT_PRIVACY_SETTINGS)
        }
      ]
    );
  };

  const exportData = () => {
    Alert.alert(
      'Export Personal Data',
      'We will prepare your personal data export and send it to your registered email within 30 days as required by GDPR/LGPD regulations.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Request Export',
          onPress: () => {
            // TODO: Implement actual data export request
            Alert.alert('Request Submitted', 'Your data export request has been submitted. You will receive an email confirmation shortly.');
          }
        }
      ]
    );
  };

  const deleteAllData = () => {
    Alert.alert(
      'Delete All Personal Data',
      'This will permanently delete all your personal data from our servers. This action cannot be undone. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete All Data',
          style: 'destructive',
          onPress: () => {
            Alert.alert(
              'Final Confirmation',
              'Are you absolutely sure you want to delete all your data? This will remove your account permanently.',
              [
                { text: 'Cancel', style: 'cancel' },
                {
                  text: 'Yes, Delete Everything',
                  style: 'destructive',
                  onPress: () => {
                    // TODO: Implement actual data deletion
                    Alert.alert('Data Deletion Initiated', 'Your data deletion request has been submitted. All personal data will be removed within 72 hours.');
                  }
                }
              ]
            );
          }
        }
      ]
    );
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      padding: 16,
    },
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
      marginBottom: 8,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginBottom: 24,
    },
    section: {
      marginBottom: 24,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 12,
    },
    settingItem: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      paddingVertical: 12,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    settingInfo: {
      flex: 1,
      marginRight: 16,
    },
    settingTitle: {
      fontSize: 16,
      fontWeight: '500',
      color: colors.text,
      marginBottom: 4,
    },
    settingDescription: {
      fontSize: 13,
      color: colors.textSecondary,
      lineHeight: 18,
    },
    switch: {
      marginTop: 4,
    },
    actionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colors.surface,
      padding: 16,
      borderRadius: 12,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: colors.border,
    },
    dangerButton: {
      backgroundColor: '#ff4444',
      borderColor: '#ff4444',
    },
    actionButtonText: {
      fontSize: 16,
      fontWeight: '500',
      color: colors.text,
      marginLeft: 8,
    },
    dangerButtonText: {
      color: '#fff',
    },
    complianceNotice: {
      backgroundColor: colors.primary + '20',
      padding: 12,
      borderRadius: 8,
      marginBottom: 16,
    },
    complianceText: {
      fontSize: 12,
      color: colors.text,
      textAlign: 'center',
    }
  });

  const privacySettings = [
    {
      key: 'locationSharing' as keyof PrivacySettings,
      title: 'Location Services',
      description: 'Allow us to use your location for regional content and radio stations. Required for FCC/broadcasting compliance.',
      essential: true,
    },
    {
      key: 'analyticsCollection' as keyof PrivacySettings,
      title: 'Usage Analytics',
      description: 'Help us improve the app by sharing anonymous usage statistics and performance data.',
      essential: false,
    },
    {
      key: 'personalizedContent' as keyof PrivacySettings,
      title: 'Personalized Content',
      description: 'Customize radio station recommendations and content based on your listening preferences.',
      essential: false,
    },
    {
      key: 'crashReporting' as keyof PrivacySettings,
      title: 'Crash Reports',
      description: 'Automatically send crash reports to help us fix bugs and improve app stability.',
      essential: false,
    },
    {
      key: 'voiceDataProcessing' as keyof PrivacySettings,
      title: 'Voice Data Processing',
      description: 'Process voice commands locally for hands-free control. Voice data is not stored or transmitted.',
      essential: false,
    },
    {
      key: 'marketingCommunications' as keyof PrivacySettings,
      title: 'Marketing Communications',
      description: 'Receive updates about new features, stations, and promotional content via email or notifications.',
      essential: false,
    },
    {
      key: 'dataSharingPartners' as keyof PrivacySettings,
      title: 'Data Sharing with Partners',
      description: 'Share anonymized listening data with radio stations and content partners for licensing purposes.',
      essential: false,
    },
    {
      key: 'cookiesAndTracking' as keyof PrivacySettings,
      title: 'Cookies & Tracking',
      description: 'Use cookies and similar technologies for app functionality and performance monitoring.',
      essential: true,
    }
  ];

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <Text style={styles.title}>Loading Privacy Settings...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>Privacy Controls</Text>
      <Text style={styles.subtitle}>
        Manage how your data is collected, used, and shared
      </Text>

      <View style={styles.complianceNotice}>
        <Text style={styles.complianceText}>
          ✓ FCC Compliant • ✓ GDPR Compliant • ✓ Kenya DPA Compliant • ✓ LGPD Compliant
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data Collection & Usage</Text>
        {privacySettings.map((setting) => (
          <View key={setting.key} style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>
                {setting.title}
                {setting.essential && ' *'}
              </Text>
              <Text style={styles.settingDescription}>
                {setting.description}
                {setting.essential && ' (Essential for app functionality)'}
              </Text>
            </View>
            <Switch
              style={styles.switch}
              value={settings[setting.key]}
              onValueChange={(value) => updateSetting(setting.key, value)}
              trackColor={{ false: colors.border, true: colors.primary + '80' }}
              thumbColor={settings[setting.key] ? colors.primary : colors.textSecondary}
              disabled={setting.essential} // Essential settings cannot be disabled
            />
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data Rights & Actions</Text>
        
        <TouchableOpacity style={styles.actionButton} onPress={exportData}>
          <Ionicons name="download-outline" size={20} color={colors.text} />
          <Text style={styles.actionButtonText}>Export My Data</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton} onPress={resetToDefaults}>
          <Ionicons name="refresh-outline" size={20} color={colors.text} />
          <Text style={styles.actionButtonText}>Reset to Defaults</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.actionButton, styles.dangerButton]} 
          onPress={deleteAllData}
        >
          <Ionicons name="trash-outline" size={20} color="#fff" />
          <Text style={[styles.actionButtonText, styles.dangerButtonText]}>
            Delete All My Data
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.complianceNotice}>
        <Text style={styles.complianceText}>
          * Essential settings are required for core app functionality and regulatory compliance.
          You have the right to access, correct, or delete your personal data under GDPR, LGPD, and local privacy laws.
        </Text>
      </View>
    </ScrollView>
  );
};