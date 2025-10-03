import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Alert,
  Modal,
  Slider,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { accessibilityService, AccessibilitySettings as AccessibilitySettingsType, AccessibilityColors } from '../services/AccessibilityService';

interface AccessibilitySettingsProps {
  visible: boolean;
  onClose: () => void;
}

export const AccessibilitySettings: React.FC<AccessibilitySettingsProps> = ({
  visible,
  onClose,
}) => {
  const [settings, setSettings] = useState<AccessibilitySettingsType | null>(null);
  const [colors, setColors] = useState<AccessibilityColors | null>(null);
  const [currentTab, setCurrentTab] = useState<'display' | 'audio' | 'interaction' | 'emergency'>('display');

  useEffect(() => {
    if (visible) {
      loadSettings();
      setupListeners();
    }
  }, [visible]);

  const loadSettings = () => {
    const currentSettings = accessibilityService.getSettings();
    const currentColors = accessibilityService.getAccessibilityColors();
    setSettings(currentSettings);
    setColors(currentColors);
  };

  const setupListeners = () => {
    const unsubscribe = accessibilityService.addListener((newSettings) => {
      setSettings(newSettings);
      setColors(accessibilityService.getAccessibilityColors());
    });

    return () => {
      unsubscribe();
    };
  };

  const handleUpdateSetting = async (key: keyof AccessibilitySettingsType, value: any) => {
    try {
      await accessibilityService.updateSettings({ [key]: value });
      
      // Provide feedback about the change
      switch (key) {
        case 'screenReaderEnabled':
          accessibilityService.announceIf(value ? 'Screen reader support enabled' : 'Screen reader support disabled');
          break;
        case 'highContrastEnabled':
          accessibilityService.announceIf(value ? 'High contrast mode enabled' : 'High contrast mode disabled');
          break;
        case 'largeTextEnabled':
          accessibilityService.announceIf(value ? 'Large text enabled' : 'Large text disabled');
          break;
        case 'voiceAnnouncementsEnabled':
          if (value) {
            accessibilityService.announce('Voice announcements are now enabled');
          }
          break;
        case 'hapticFeedbackEnabled':
          if (value) {
            accessibilityService.hapticFeedback('success');
          }
          break;
      }
    } catch (error) {
      console.error('Failed to update accessibility setting:', error);
      Alert.alert('Error', 'Failed to update setting. Please try again.');
    }
  };

  const handleEmergencyAccessibility = () => {
    Alert.alert(
      'Emergency Accessibility',
      'This will enable all accessibility features for emergency situations. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Enable All',
          style: 'default',
          onPress: async () => {
            try {
              await accessibilityService.enableEmergencyAccessibility();
              loadSettings();
            } catch (error) {
              Alert.alert('Error', 'Failed to enable emergency accessibility.');
            }
          },
        },
      ]
    );
  };

  const getAccessibilityReport = () => {
    const report = accessibilityService.getAccessibilityReport();
    Alert.alert(
      'Accessibility Status',
      report,
      [
        { text: 'OK', style: 'default' },
        { text: 'Read Aloud', onPress: () => accessibilityService.announce(report) },
      ]
    );
  };

  if (!settings || !colors) return null;

  const dynamicStyles = StyleSheet.create({
    container: {
      ...styles.container,
      backgroundColor: colors.background,
    },
    header: {
      ...styles.header,
      backgroundColor: colors.surface,
      borderBottomColor: colors.border,
    },
    title: {
      ...styles.title,
      color: colors.text,
      fontSize: accessibilityService.getFontSize(24),
    },
    tabBar: {
      ...styles.tabBar,
      backgroundColor: colors.surface,
      borderBottomColor: colors.border,
    },
    tab: {
      ...styles.tab,
      minHeight: accessibilityService.getTouchTargetSize(48),
    },
    activeTab: {
      ...styles.activeTab,
      borderBottomColor: colors.primary,
    },
    tabLabel: {
      ...styles.tabLabel,
      color: colors.textSecondary,
      fontSize: accessibilityService.getFontSize(14),
    },
    activeTabLabel: {
      ...styles.activeTabLabel,
      color: colors.primary,
    },
    sectionTitle: {
      ...styles.sectionTitle,
      color: colors.text,
      fontSize: accessibilityService.getFontSize(18),
    },
    settingItem: {
      ...styles.settingItem,
      borderBottomColor: colors.border,
      minHeight: accessibilityService.getTouchTargetSize(60),
    },
    settingTitle: {
      ...styles.settingTitle,
      color: colors.text,
      fontSize: accessibilityService.getFontSize(16),
    },
    settingDescription: {
      ...styles.settingDescription,
      color: colors.textSecondary,
      fontSize: accessibilityService.getFontSize(14),
    },
    sliderContainer: {
      ...styles.sliderContainer,
      backgroundColor: colors.surface,
    },
    emergencyButton: {
      ...styles.emergencyButton,
      backgroundColor: colors.error,
      minHeight: accessibilityService.getTouchTargetSize(50),
    },
    emergencyButtonText: {
      ...styles.emergencyButtonText,
      fontSize: accessibilityService.getFontSize(16),
    },
    statusButton: {
      ...styles.statusButton,
      backgroundColor: colors.primary,
      minHeight: accessibilityService.getTouchTargetSize(44),
    },
  });

  const renderDisplayTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={dynamicStyles.sectionTitle}>Visual Settings</Text>
      
      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>High Contrast Mode</Text>
          <Text style={dynamicStyles.settingDescription}>
            Increases contrast for better visibility
          </Text>
        </View>
        <Switch
          value={settings.highContrastEnabled}
          onValueChange={(value) => handleUpdateSetting('highContrastEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="High contrast mode"
          accessibilityRole="switch"
        />
      </View>

      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Color Theme</Text>
          <Text style={dynamicStyles.settingDescription}>
            Current: {settings.colorTheme.replace('_', ' ')}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.themeSelector}
          onPress={() => {
            const themes: Array<typeof settings.colorTheme> = ['normal', 'high_contrast', 'high_contrast_dark'];
            const currentIndex = themes.indexOf(settings.colorTheme);
            const nextIndex = (currentIndex + 1) % themes.length;
            handleUpdateSetting('colorTheme', themes[nextIndex]);
          }}
          accessible={true}
          accessibilityLabel="Change color theme"
          accessibilityHint="Double tap to cycle through available themes"
        >
          <Ionicons name="color-palette" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Large Text</Text>
          <Text style={dynamicStyles.settingDescription}>
            Enables larger text throughout the app
          </Text>
        </View>
        <Switch
          value={settings.largeTextEnabled}
          onValueChange={(value) => handleUpdateSetting('largeTextEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Large text"
        />
      </View>

      <Text style={dynamicStyles.sectionTitle}>Text Size</Text>
      
      <View style={dynamicStyles.sliderContainer}>
        <Text style={dynamicStyles.settingTitle}>
          Font Size: {Math.round(settings.fontSizeMultiplier * 100)}%
        </Text>
        <Slider
          style={styles.slider}
          value={settings.fontSizeMultiplier}
          minimumValue={0.8}
          maximumValue={2.0}
          step={0.1}
          onValueChange={(value) => handleUpdateSetting('fontSizeMultiplier', value)}
          thumbStyle={{ backgroundColor: colors.primary }}
          trackStyle={{ backgroundColor: colors.border }}
          minimumTrackTintColor={colors.primary}
          maximumTrackTintColor={colors.border}
          accessible={true}
          accessibilityLabel="Font size slider"
          accessibilityValue={{ text: `${Math.round(settings.fontSizeMultiplier * 100)} percent` }}
        />
        <Text style={dynamicStyles.settingDescription}>
          This text will be {settings.fontSizeMultiplier < 1 ? 'smaller' : settings.fontSizeMultiplier > 1 ? 'larger' : 'normal size'}
        </Text>
      </View>

      <Text style={dynamicStyles.sectionTitle}>Touch Targets</Text>
      
      <View style={dynamicStyles.sliderContainer}>
        <Text style={dynamicStyles.settingTitle}>
          Touch Target Size: {Math.round(settings.touchTargetSizeMultiplier * 100)}%
        </Text>
        <Slider
          style={styles.slider}
          value={settings.touchTargetSizeMultiplier}
          minimumValue={1.0}
          maximumValue={1.8}
          step={0.1}
          onValueChange={(value) => handleUpdateSetting('touchTargetSizeMultiplier', value)}
          thumbStyle={{ backgroundColor: colors.primary }}
          trackStyle={{ backgroundColor: colors.border }}
          minimumTrackTintColor={colors.primary}
          maximumTrackTintColor={colors.border}
          accessible={true}
          accessibilityLabel="Touch target size slider"
        />
        <Text style={dynamicStyles.settingDescription}>
          Makes buttons and interactive elements larger and easier to tap
        </Text>
      </View>
    </ScrollView>
  );

  const renderAudioTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={dynamicStyles.sectionTitle}>Voice & Audio</Text>
      
      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Voice Announcements</Text>
          <Text style={dynamicStyles.settingDescription}>
            Announces important actions and navigation
          </Text>
        </View>
        <Switch
          value={settings.voiceAnnouncementsEnabled}
          onValueChange={(value) => handleUpdateSetting('voiceAnnouncementsEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Voice announcements"
        />
      </View>

      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Audio Descriptions</Text>
          <Text style={dynamicStyles.settingDescription}>
            Automatically describes media content and player state
          </Text>
        </View>
        <Switch
          value={settings.autoplayAudioDescriptions}
          onValueChange={(value) => handleUpdateSetting('autoplayAudioDescriptions', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Audio descriptions"
        />
      </View>

      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Screen Reader Support</Text>
          <Text style={dynamicStyles.settingDescription}>
            Enhanced compatibility with screen readers like VoiceOver and TalkBack
          </Text>
        </View>
        <Switch
          value={settings.screenReaderEnabled}
          onValueChange={(value) => handleUpdateSetting('screenReaderEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Screen reader support"
        />
      </View>

      <TouchableOpacity
        style={styles.testButton}
        onPress={() => {
          accessibilityService.announce('This is a test of the voice announcement system. If you can hear this, voice announcements are working correctly.');
        }}
        accessible={true}
        accessibilityLabel="Test voice announcements"
        accessibilityHint="Double tap to test if voice announcements are working"
      >
        <Ionicons name="volume-high" size={20} color={colors.primary} />
        <Text style={[styles.testButtonText, { color: colors.primary }]}>
          Test Voice Announcements
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );

  const renderInteractionTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={dynamicStyles.sectionTitle}>Interaction Settings</Text>
      
      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Haptic Feedback</Text>
          <Text style={dynamicStyles.settingDescription}>
            Vibration feedback for button presses and interactions
          </Text>
        </View>
        <Switch
          value={settings.hapticFeedbackEnabled}
          onValueChange={(value) => handleUpdateSetting('hapticFeedbackEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Haptic feedback"
        />
      </View>

      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Reduced Motion</Text>
          <Text style={dynamicStyles.settingDescription}>
            Reduces animations and motion effects
          </Text>
        </View>
        <Switch
          value={settings.reducedMotionEnabled}
          onValueChange={(value) => handleUpdateSetting('reducedMotionEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Reduced motion"
        />
      </View>

      <View style={dynamicStyles.settingItem}>
        <View style={styles.settingLabel}>
          <Text style={dynamicStyles.settingTitle}>Keyboard Navigation</Text>
          <Text style={dynamicStyles.settingDescription}>
            Enhanced support for external keyboard navigation
          </Text>
        </View>
        <Switch
          value={settings.keyboardNavigationEnabled}
          onValueChange={(value) => handleUpdateSetting('keyboardNavigationEnabled', value)}
          thumbColor={Platform.OS === 'android' ? colors.primary : undefined}
          trackColor={{ false: colors.border, true: colors.primary }}
          accessible={true}
          accessibilityLabel="Keyboard navigation"
        />
      </View>

      <TouchableOpacity
        style={styles.testButton}
        onPress={() => {
          accessibilityService.hapticFeedback('light');
          setTimeout(() => accessibilityService.hapticFeedback('medium'), 200);
          setTimeout(() => accessibilityService.hapticFeedback('heavy'), 400);
          accessibilityService.announceIf('Haptic feedback test: light, medium, heavy vibrations');
        }}
        accessible={true}
        accessibilityLabel="Test haptic feedback"
        accessibilityHint="Double tap to test vibration patterns"
      >
        <Ionicons name="phone-portrait" size={20} color={colors.primary} />
        <Text style={[styles.testButtonText, { color: colors.primary }]}>
          Test Haptic Feedback
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );

  const renderEmergencyTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={dynamicStyles.sectionTitle}>Emergency Features</Text>
      
      <View style={styles.emergencyCard}>
        <Ionicons name="warning" size={32} color={colors.warning} />
        <Text style={[styles.emergencyTitle, { color: colors.text }]}>
          Emergency Accessibility Mode
        </Text>
        <Text style={[styles.emergencyDescription, { color: colors.textSecondary }]}>
          Quickly enables all accessibility features for emergency situations or when immediate maximum accessibility is needed.
        </Text>
        
        <TouchableOpacity
          style={dynamicStyles.emergencyButton}
          onPress={handleEmergencyAccessibility}
          accessible={true}
          accessibilityLabel="Enable emergency accessibility mode"
          accessibilityHint="Double tap to activate all accessibility features"
        >
          <Text style={dynamicStyles.emergencyButtonText}>
            Enable All Accessibility Features
          </Text>
        </TouchableOpacity>
      </View>

      <Text style={dynamicStyles.sectionTitle}>Status & Information</Text>
      
      <TouchableOpacity
        style={dynamicStyles.statusButton}
        onPress={getAccessibilityReport}
        accessible={true}
        accessibilityLabel="Get accessibility status report"
        accessibilityHint="Double tap to view current accessibility settings"
      >
        <Ionicons name="information-circle" size={20} color="#FFFFFF" />
        <Text style={[styles.statusButtonText, { fontSize: accessibilityService.getFontSize(16) }]}>
          Accessibility Status Report
        </Text>
      </TouchableOpacity>

      <View style={styles.infoCard}>
        <Text style={[styles.infoTitle, { color: colors.text }]}>
          Platform Integration
        </Text>
        <Text style={[styles.infoText, { color: colors.textSecondary }]}>
          This app integrates with your device's built-in accessibility features:
        </Text>
        <Text style={[styles.infoText, { color: colors.textSecondary }]}>
          • VoiceOver (iOS) / TalkBack (Android){'\n'}
          • Dynamic Type / Font Size{'\n'}
          • Reduce Motion{'\n'}
          • High Contrast{'\n'}
          • Switch Control{'\n'}
          • Voice Control
        </Text>
      </View>
    </ScrollView>
  );

  const renderTabBar = () => (
    <View style={dynamicStyles.tabBar}>
      {[
        { key: 'display', label: 'Display', icon: 'eye-outline' },
        { key: 'audio', label: 'Audio', icon: 'volume-high-outline' },
        { key: 'interaction', label: 'Interaction', icon: 'hand-left-outline' },
        { key: 'emergency', label: 'Emergency', icon: 'warning-outline' },
      ].map((tab) => (
        <TouchableOpacity
          key={tab.key}
          style={[dynamicStyles.tab, currentTab === tab.key && dynamicStyles.activeTab]}
          onPress={() => {
            setCurrentTab(tab.key as any);
            accessibilityService.hapticFeedback('light');
            accessibilityService.setFocusedElement(`accessibility_tab_${tab.key}`, `${tab.label} tab`);
          }}
          accessible={true}
          accessibilityLabel={`${tab.label} tab`}
          accessibilityRole="tab"
          accessibilityState={{ selected: currentTab === tab.key }}
        >
          <Ionicons 
            name={tab.icon as any} 
            size={18} 
            color={currentTab === tab.key ? colors.primary : colors.textSecondary} 
          />
          <Text style={[
            dynamicStyles.tabLabel,
            currentTab === tab.key && dynamicStyles.activeTabLabel
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <View style={dynamicStyles.container}>
        <View style={dynamicStyles.header}>
          <Text style={dynamicStyles.title}>Accessibility Settings</Text>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={onClose}
            accessible={true}
            accessibilityLabel="Close accessibility settings"
            accessibilityHint="Double tap to close this screen"
          >
            <Ionicons name="close" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>
        
        {renderTabBar()}
        
        <View style={styles.content}>
          {currentTab === 'display' && renderDisplayTab()}
          {currentTab === 'audio' && renderAudioTab()}
          {currentTab === 'interaction' && renderInteractionTab()}
          {currentTab === 'emergency' && renderEmergencyTab()}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
  },
  title: {
    fontWeight: 'bold',
  },
  closeButton: {
    padding: 5,
  },
  tabBar: {
    flexDirection: 'row',
    borderBottomWidth: 1,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  activeTab: {
    borderBottomWidth: 2,
  },
  tabLabel: {
    marginLeft: 6,
    fontWeight: '500',
  },
  activeTabLabel: {},
  content: {
    flex: 1,
  },
  tabContent: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: 15,
    marginTop: 10,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 5,
    borderBottomWidth: 1,
  },
  settingLabel: {
    flex: 1,
    marginRight: 15,
  },
  settingTitle: {
    fontWeight: '500',
    marginBottom: 4,
  },
  settingDescription: {
    lineHeight: 18,
  },
  themeSelector: {
    padding: 10,
    borderRadius: 8,
  },
  sliderContainer: {
    padding: 15,
    borderRadius: 10,
    marginVertical: 10,
  },
  slider: {
    width: '100%',
    height: 40,
    marginVertical: 10,
  },
  testButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    marginTop: 15,
    borderWidth: 1,
    borderRadius: 8,
    borderColor: '#4ECDC4',
  },
  testButtonText: {
    marginLeft: 8,
    fontWeight: '500',
  },
  emergencyCard: {
    padding: 20,
    borderRadius: 12,
    backgroundColor: '#FFF3E0',
    alignItems: 'center',
    marginBottom: 20,
  },
  emergencyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 10,
    marginBottom: 10,
    textAlign: 'center',
  },
  emergencyDescription: {
    fontSize: 14,
    lineHeight: 20,
    textAlign: 'center',
    marginBottom: 20,
  },
  emergencyButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emergencyButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  statusButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginBottom: 20,
  },
  statusButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 8,
  },
  infoCard: {
    padding: 15,
    borderRadius: 10,
    backgroundColor: '#F0F8FF',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 18,
    marginBottom: 5,
  },
});

export default AccessibilitySettings;