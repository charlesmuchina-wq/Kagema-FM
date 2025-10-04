import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';
import { PrivacyPolicyContent } from './PrivacyPolicyContent';
import { PrivacyControls } from './PrivacyControls';

type PrivacyView = 'main' | 'policy' | 'controls';
type Jurisdiction = 'global' | 'us' | 'eu' | 'kenya' | 'brazil';

interface PrivacySettingsProps {
  visible: boolean;
  onClose: () => void;
  currentLanguage?: string;
}

export const PrivacySettings: React.FC<PrivacySettingsProps> = ({
  visible,
  onClose,
  currentLanguage = 'en'
}) => {
  const { colors } = useTheme();
  const [currentView, setCurrentView] = useState<PrivacyView>('main');
  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>('global');

  // Detect jurisdiction based on user location or settings
  useEffect(() => {
    detectJurisdiction();
  }, []);

  const detectJurisdiction = async () => {
    try {
      // In a real app, you might detect this from:
      // - User's location services
      // - IP geolocation
      // - User-selected region in settings
      // For now, we'll use a simple detection
      
      // Mock detection - in real app, replace with actual location detection
      const userRegion = 'global'; // This could come from location services
      setJurisdiction(userRegion as Jurisdiction);
    } catch (error) {
      console.error('Error detecting jurisdiction:', error);
      setJurisdiction('global');
    }
  };

  const handleClose = () => {
    setCurrentView('main');
    onClose();
  };

  const styles = StyleSheet.create({
    overlay: {
      flex: 1,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    modalContainer: {
      width: '95%',
      height: '90%',
      backgroundColor: colors.background,
      borderRadius: 16,
      overflow: 'hidden',
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 16,
      backgroundColor: colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    headerTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      flex: 1,
      textAlign: 'center',
    },
    backButton: {
      padding: 8,
    },
    closeButton: {
      padding: 8,
    },
    content: {
      flex: 1,
    },
    mainContainer: {
      flex: 1,
      padding: 16,
    },
    welcomeText: {
      fontSize: 16,
      color: colors.text,
      textAlign: 'center',
      marginBottom: 24,
      lineHeight: 22,
    },
    menuItem: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      backgroundColor: colors.surface,
      borderRadius: 12,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: colors.border,
    },
    menuIcon: {
      marginRight: 16,
    },
    menuContent: {
      flex: 1,
    },
    menuTitle: {
      fontSize: 16,
      fontWeight: '500',
      color: colors.text,
      marginBottom: 4,
    },
    menuDescription: {
      fontSize: 13,
      color: colors.textSecondary,
      lineHeight: 18,
    },
    chevron: {
      marginLeft: 8,
    },
    jurisdictionSelector: {
      backgroundColor: colors.primary + '20',
      padding: 12,
      borderRadius: 8,
      marginBottom: 20,
    },
    jurisdictionTitle: {
      fontSize: 14,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 8,
    },
    jurisdictionOptions: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    jurisdictionOption: {
      paddingHorizontal: 12,
      paddingVertical: 6,
      backgroundColor: colors.surface,
      borderRadius: 16,
      borderWidth: 1,
      borderColor: colors.border,
    },
    activeJurisdiction: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    },
    jurisdictionText: {
      fontSize: 12,
      color: colors.text,
    },
    activeJurisdictionText: {
      color: colors.background,
      fontWeight: '500',
    }
  });

  const getHeaderTitle = () => {
    switch (currentView) {
      case 'policy':
        return 'Privacy Policy';
      case 'controls':
        return 'Privacy Controls';
      default:
        return 'Privacy Settings';
    }
  };

  const jurisdictionOptions = [
    { key: 'global', label: 'Global' },
    { key: 'us', label: 'United States' },
    { key: 'eu', label: 'European Union' },
    { key: 'kenya', label: 'Kenya' },
    { key: 'brazil', label: 'Brazil' },
  ];

  const renderMainView = () => (
    <ScrollView style={styles.mainContainer} showsVerticalScrollIndicator={false}>
      <Text style={styles.welcomeText}>
        Your privacy matters to us. Manage your privacy preferences and understand how we protect your data in compliance with international regulations.
      </Text>

      <View style={styles.jurisdictionSelector}>
        <Text style={styles.jurisdictionTitle}>Select Your Region:</Text>
        <View style={styles.jurisdictionOptions}>
          {jurisdictionOptions.map((option) => (
            <TouchableOpacity
              key={option.key}
              style={[
                styles.jurisdictionOption,
                jurisdiction === option.key && styles.activeJurisdiction
              ]}
              onPress={() => setJurisdiction(option.key as Jurisdiction)}
            >
              <Text style={[
                styles.jurisdictionText,
                jurisdiction === option.key && styles.activeJurisdictionText
              ]}>
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <TouchableOpacity
        style={styles.menuItem}
        onPress={() => setCurrentView('policy')}
      >
        <Ionicons
          name="document-text-outline"
          size={24}
          color={colors.primary}
          style={styles.menuIcon}
        />
        <View style={styles.menuContent}>
          <Text style={styles.menuTitle}>Privacy Policy</Text>
          <Text style={styles.menuDescription}>
            Read our comprehensive privacy policy with region-specific compliance information (FCC, GDPR, Kenya DPA, LGPD).
          </Text>
        </View>
        <Ionicons
          name="chevron-forward"
          size={20}
          color={colors.textSecondary}
          style={styles.chevron}
        />
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.menuItem}
        onPress={() => setCurrentView('controls')}
      >
        <Ionicons
          name="shield-checkmark-outline"
          size={24}
          color={colors.primary}
          style={styles.menuIcon}
        />
        <View style={styles.menuContent}>
          <Text style={styles.menuTitle}>Privacy Controls</Text>
          <Text style={styles.menuDescription}>
            Manage data collection, sharing preferences, and exercise your privacy rights including data export and deletion.
          </Text>
        </View>
        <Ionicons
          name="chevron-forward"
          size={20}
          color={colors.textSecondary}
          style={styles.chevron}
        />
      </TouchableOpacity>

      <TouchableOpacity style={styles.menuItem}>
        <Ionicons
          name="mail-outline"
          size={24}
          color={colors.primary}
          style={styles.menuIcon}
        />
        <View style={styles.menuContent}>
          <Text style={styles.menuTitle}>Contact Privacy Officer</Text>
          <Text style={styles.menuDescription}>
            Have questions about your data? Contact our Data Protection Officer at privacy@kagemafm.com
          </Text>
        </View>
        <Ionicons
          name="chevron-forward"
          size={20}
          color={colors.textSecondary}
          style={styles.chevron}
        />
      </TouchableOpacity>

      <View style={[styles.jurisdictionSelector, { marginTop: 20 }]}>
        <Text style={styles.jurisdictionText}>
          🛡️ We are committed to protecting your privacy in accordance with {jurisdiction === 'us' ? 'FCC regulations' : jurisdiction === 'eu' ? 'GDPR' : jurisdiction === 'kenya' ? 'Kenya Data Protection Act' : jurisdiction === 'brazil' ? 'LGPD' : 'international privacy standards'} and applicable local laws.
        </Text>
      </View>
    </ScrollView>
  );

  const renderContent = () => {
    switch (currentView) {
      case 'policy':
        return (
          <PrivacyPolicyContent
            language={currentLanguage}
            jurisdiction={jurisdiction}
          />
        );
      case 'controls':
        return <PrivacyControls />;
      default:
        return renderMainView();
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="overFullScreen"
      onRequestClose={handleClose}
    >
      <View style={styles.overlay}>
        <View style={styles.modalContainer}>
          <View style={styles.header}>
            {currentView !== 'main' && (
              <TouchableOpacity
                style={styles.backButton}
                onPress={() => setCurrentView('main')}
              >
                <Ionicons name="arrow-back" size={24} color={colors.text} />
              </TouchableOpacity>
            )}
            <Text style={styles.headerTitle}>{getHeaderTitle()}</Text>
            <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <View style={styles.content}>
            {renderContent()}
          </View>
        </View>
      </View>
    </Modal>
  );
};