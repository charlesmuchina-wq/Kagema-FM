import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ScrollView,
  Switch,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width } = Dimensions.get('window');

interface ContentDisclaimer {
  id: string;
  title: string;
  content: string;
  severity: string;
  applies_to: string[];
}

interface ComplianceInfo {
  country: string;
  content_rating_system: string;
  adult_age_threshold: number;
  content_warnings_required: boolean;
  government_regulations: string[];
}

interface ContentDisclaimerProps {
  visible: boolean;
  onClose: () => void;
  disclaimers: ContentDisclaimer[];
  complianceInfo: ComplianceInfo;
  countryCode: string;
  languageCode: string;
  onAccept: (disclaimerIds: string[], userAge: number) => void;
  onReject: () => void;
}

const ContentDisclaimerModal: React.FC<ContentDisclaimerProps> = ({
  visible,
  onClose,
  disclaimers,
  complianceInfo,
  countryCode,
  languageCode,
  onAccept,
  onReject,
}) => {
  const [userAge, setUserAge] = useState<number>(18);
  const [ageVerified, setAgeVerified] = useState<boolean>(false);
  const [acceptAdultContent, setAcceptAdultContent] = useState<boolean>(false);
  const [acknowledgedDisclaimers, setAcknowledgedDisclaimers] = useState<Set<string>>(new Set());
  const [currentDisclaimerIndex, setCurrentDisclaimerIndex] = useState<number>(0);
  const [showAgeVerification, setShowAgeVerification] = useState<boolean>(true);
  const [hasReadAll, setHasReadAll] = useState<boolean>(false);

  useEffect(() => {
    if (visible) {
      checkExistingAcknowledgment();
    }
  }, [visible]);

  const checkExistingAcknowledgment = async () => {
    try {
      const existingAcknowledgment = await AsyncStorage.getItem('content_disclaimer_acknowledged');
      if (existingAcknowledgment) {
        const acknowledgment = JSON.parse(existingAcknowledgment);
        const acknowledgmentDate = new Date(acknowledgment.timestamp);
        const now = new Date();
        
        // Check if acknowledgment is still valid (within 24 hours)
        if (now.getTime() - acknowledgmentDate.getTime() < 24 * 60 * 60 * 1000) {
          onClose();
          return;
        }
      }
    } catch (error) {
      console.error('Error checking existing acknowledgment:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      case 'notice':
        return '#2196f3';
      default:
        return '#757575';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'warning';
      case 'warning':
        return 'alert-circle';
      case 'notice':
        return 'information-circle';
      default:
        return 'document-text';
    }
  };

  const handleAgeInput = (age: string) => {
    const ageNum = parseInt(age) || 0;
    setUserAge(ageNum);
    setAgeVerified(ageNum >= complianceInfo.adult_age_threshold);
  };

  const handleDisclaimerAcknowledge = (disclaimerId: string) => {
    const newAcknowledged = new Set(acknowledgedDisclaimers);
    newAcknowledged.add(disclaimerId);
    setAcknowledgedDisclaimers(newAcknowledged);
    
    // Check if user has acknowledged all disclaimers
    if (newAcknowledged.size === disclaimers.length) {
      setHasReadAll(true);
    }
  };

  const handleNextDisclaimer = () => {
    const currentDisclaimer = disclaimers[currentDisclaimerIndex];
    if (!acknowledgedDisclaimers.has(currentDisclaimer.id)) {
      Alert.alert(
        'Acknowledgment Required',
        'Please acknowledge that you have read and understood this disclaimer before proceeding.',
        [{ text: 'OK' }]
      );
      return;
    }

    if (currentDisclaimerIndex < disclaimers.length - 1) {
      setCurrentDisclaimerIndex(currentDisclaimerIndex + 1);
    } else {
      setShowAgeVerification(false);
    }
  };

  const handlePreviousDisclaimer = () => {
    if (currentDisclaimerIndex > 0) {
      setCurrentDisclaimerIndex(currentDisclaimerIndex - 1);
    }
  };

  const handleFinalAccept = async () => {
    if (!ageVerified) {
      Alert.alert(
        'Age Verification Required',
        `You must be at least ${complianceInfo.adult_age_threshold} years old to use this service.`,
        [{ text: 'OK' }]
      );
      return;
    }

    if (!hasReadAll) {
      Alert.alert(
        'Disclaimer Acknowledgment Required',
        'Please read and acknowledge all content disclaimers before proceeding.',
        [{ text: 'OK' }]
      );
      return;
    }

    try {
      // Store acknowledgment
      const acknowledgment = {
        disclaimerIds: Array.from(acknowledgedDisclaimers),
        userAge,
        countryCode,
        languageCode,
        timestamp: new Date().toISOString(),
        acceptAdultContent
      };

      await AsyncStorage.setItem('content_disclaimer_acknowledged', JSON.stringify(acknowledgment));
      onAccept(Array.from(acknowledgedDisclaimers), userAge);
    } catch (error) {
      console.error('Error saving acknowledgment:', error);
      Alert.alert('Error', 'Failed to save acknowledgment. Please try again.');
    }
  };

  const handleReject = () => {
    Alert.alert(
      'Content Access Denied',
      'You must accept the content disclaimers to use this radio service. The app will close.',
      [
        { text: 'Reconsider', style: 'cancel' },
        { text: 'Exit App', onPress: onReject, style: 'destructive' }
      ]
    );
  };

  const renderAgeVerification = () => (
    <View style={styles.ageVerificationContainer}>
      <Text style={styles.ageVerificationTitle}>Age Verification Required</Text>
      <Text style={styles.ageVerificationText}>
        This radio platform contains mature content and is designed for adult listeners. 
        In {complianceInfo.country}, you must be at least {complianceInfo.adult_age_threshold} years old to access this content.
      </Text>
      
      <View style={styles.ageInputContainer}>
        <Text style={styles.ageInputLabel}>Enter your age:</Text>
        <TextInput
          style={styles.ageInput}
          value={userAge.toString()}
          onChangeText={handleAgeInput}
          keyboardType="numeric"
          maxLength={2}
          placeholder="18"
        />
      </View>

      {userAge >= complianceInfo.adult_age_threshold && (
        <View style={styles.adultContentContainer}>
          <View style={styles.switchContainer}>
            <Switch
              value={acceptAdultContent}
              onValueChange={setAcceptAdultContent}
              trackColor={{ false: '#767577', true: '#ff6b6b' }}
              thumbColor={acceptAdultContent ? '#fff' : '#f4f3f4'}
            />
            <Text style={styles.switchLabel}>I accept that I may encounter adult content</Text>
          </View>
        </View>
      )}

      <View style={styles.complianceInfo}>
        <Text style={styles.complianceTitle}>Regional Compliance Information</Text>
        <Text style={styles.complianceText}>Country: {complianceInfo.country}</Text>
        <Text style={styles.complianceText}>Rating System: {complianceInfo.content_rating_system}</Text>
        <Text style={styles.complianceText}>
          Government Regulations: {complianceInfo.government_regulations.slice(0, 2).join(', ')}
        </Text>
      </View>

      {ageVerified && acceptAdultContent && (
        <TouchableOpacity
          style={styles.continueButton}
          onPress={() => setShowAgeVerification(false)}
        >
          <Text style={styles.continueButtonText}>Continue to Content Disclaimers</Text>
          <Ionicons name="arrow-forward" size={20} color="#fff" />
        </TouchableOpacity>
      )}
    </View>
  );

  const renderDisclaimer = (disclaimer: ContentDisclaimer) => (
    <View key={disclaimer.id} style={styles.disclaimerContainer}>
      <View style={styles.disclaimerHeader}>
        <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(disclaimer.severity) }]}>
          <Ionicons 
            name={getSeverityIcon(disclaimer.severity)} 
            size={16} 
            color="#fff" 
          />
          <Text style={styles.severityText}>{disclaimer.severity.toUpperCase()}</Text>
        </View>
        <Text style={styles.disclaimerProgress}>
          {currentDisclaimerIndex + 1} of {disclaimers.length}
        </Text>
      </View>

      <Text style={styles.disclaimerTitle}>{disclaimer.title}</Text>
      
      <ScrollView style={styles.disclaimerContentScroll}>
        <Text style={styles.disclaimerContent}>{disclaimer.content}</Text>
      </ScrollView>

      <View style={styles.appliesTo}>
        <Text style={styles.appliesToLabel}>Applies to:</Text>
        <View style={styles.appliesToTags}>
          {disclaimer.applies_to.map((type, index) => (
            <View key={index} style={styles.appliesToTag}>
              <Text style={styles.appliesToTagText}>{type}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.acknowledgeContainer}>
        <TouchableOpacity
          style={[
            styles.acknowledgeButton,
            acknowledgedDisclaimers.has(disclaimer.id) && styles.acknowledgedButton
          ]}
          onPress={() => handleDisclaimerAcknowledge(disclaimer.id)}
        >
          <Ionicons 
            name={acknowledgedDisclaimers.has(disclaimer.id) ? "checkmark-circle" : "checkmark-circle-outline"} 
            size={20} 
            color={acknowledgedDisclaimers.has(disclaimer.id) ? "#4CAF50" : "#ccc"} 
          />
          <Text style={[
            styles.acknowledgeButtonText,
            acknowledgedDisclaimers.has(disclaimer.id) && styles.acknowledgedButtonText
          ]}>
            {acknowledgedDisclaimers.has(disclaimer.id) ? 'Acknowledged' : 'I have read and understood this disclaimer'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="fullScreen"
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Content Compliance Required</Text>
          <Text style={styles.headerSubtitle}>
            Legal disclaimers must be acknowledged before accessing radio content
          </Text>
        </View>

        {showAgeVerification ? (
          renderAgeVerification()
        ) : (
          <>
            {renderDisclaimer(disclaimers[currentDisclaimerIndex])}
            
            <View style={styles.navigationContainer}>
              <TouchableOpacity
                style={[styles.navButton, currentDisclaimerIndex === 0 && styles.disabledButton]}
                onPress={handlePreviousDisclaimer}
                disabled={currentDisclaimerIndex === 0}
              >
                <Ionicons name="arrow-back" size={20} color={currentDisclaimerIndex === 0 ? "#ccc" : "#fff"} />
                <Text style={[styles.navButtonText, currentDisclaimerIndex === 0 && styles.disabledButtonText]}>
                  Previous
                </Text>
              </TouchableOpacity>

              {currentDisclaimerIndex < disclaimers.length - 1 ? (
                <TouchableOpacity
                  style={styles.navButton}
                  onPress={handleNextDisclaimer}
                >
                  <Text style={styles.navButtonText}>Next</Text>
                  <Ionicons name="arrow-forward" size={20} color="#fff" />
                </TouchableOpacity>
              ) : (
                <TouchableOpacity
                  style={[styles.finalAcceptButton, !hasReadAll && styles.disabledButton]}
                  onPress={handleFinalAccept}
                  disabled={!hasReadAll}
                >
                  <Text style={[styles.finalAcceptButtonText, !hasReadAll && styles.disabledButtonText]}>
                    Accept All & Continue
                  </Text>
                  <Ionicons name="checkmark" size={20} color={hasReadAll ? "#fff" : "#ccc"} />
                </TouchableOpacity>
              )}
            </View>

            <TouchableOpacity style={styles.rejectButton} onPress={handleReject}>
              <Text style={styles.rejectButtonText}>I Do Not Accept</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 20,
  },
  ageVerificationContainer: {
    flex: 1,
    padding: 20,
  },
  ageVerificationTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 16,
  },
  ageVerificationText: {
    fontSize: 16,
    color: '#ccc',
    lineHeight: 24,
    marginBottom: 24,
  },
  ageInputContainer: {
    marginBottom: 24,
  },
  ageInputLabel: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 8,
  },
  ageInput: {
    borderWidth: 1,
    borderColor: '#2d2d54',
    backgroundColor: '#2d2d54',
    color: '#fff',
    padding: 12,
    borderRadius: 8,
    fontSize: 18,
    textAlign: 'center',
    width: 80,
  },
  adultContentContainer: {
    marginBottom: 24,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  switchLabel: {
    fontSize: 16,
    color: '#fff',
    marginLeft: 12,
    flex: 1,
  },
  complianceInfo: {
    backgroundColor: '#2d2d54',
    padding: 16,
    borderRadius: 8,
    marginBottom: 24,
  },
  complianceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ff6b6b',
    marginBottom: 8,
  },
  complianceText: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 4,
  },
  continueButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ff6b6b',
    padding: 16,
    borderRadius: 8,
  },
  continueButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginRight: 8,
  },
  disclaimerContainer: {
    flex: 1,
    padding: 20,
  },
  disclaimerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  severityBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  severityText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
    marginLeft: 6,
  },
  disclaimerProgress: {
    fontSize: 14,
    color: '#ccc',
  },
  disclaimerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  disclaimerContentScroll: {
    flex: 1,
    maxHeight: 300,
  },
  disclaimerContent: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 22,
  },
  appliesTo: {
    marginTop: 16,
    marginBottom: 16,
  },
  appliesToLabel: {
    fontSize: 14,
    color: '#fff',
    marginBottom: 8,
  },
  appliesToTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  appliesToTag: {
    backgroundColor: '#ff6b6b',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 8,
  },
  appliesToTagText: {
    fontSize: 12,
    color: '#fff',
  },
  acknowledgeContainer: {
    marginTop: 16,
  },
  acknowledgeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#2d2d54',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#444',
  },
  acknowledgedButton: {
    backgroundColor: 'rgba(76, 175, 80, 0.2)',
    borderColor: '#4CAF50',
  },
  acknowledgeButtonText: {
    fontSize: 14,
    color: '#ccc',
    marginLeft: 8,
    flex: 1,
  },
  acknowledgedButtonText: {
    color: '#4CAF50',
  },
  navigationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
  },
  navButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2d2d54',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  navButtonText: {
    fontSize: 16,
    color: '#fff',
    marginHorizontal: 8,
  },
  finalAcceptButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  finalAcceptButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginRight: 8,
  },
  disabledButton: {
    opacity: 0.5,
  },
  disabledButtonText: {
    color: '#ccc',
  },
  rejectButton: {
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'transparent',
    borderTopWidth: 1,
    borderTopColor: '#2d2d54',
  },
  rejectButtonText: {
    fontSize: 16,
    color: '#f44336',
  },
});

export default ContentDisclaimerModal;