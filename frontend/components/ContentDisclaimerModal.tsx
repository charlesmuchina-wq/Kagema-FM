import React, { useState, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  TextInput,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ContentDisclaimerService from '../services/ContentDisclaimerService';

interface ContentDisclaimerModalProps {
  visible: boolean;
  onClose: () => void;
  onAccept: () => void;
  countryCode: string;
  languageCode: string;
  contentTypes?: string[];
}

const ContentDisclaimerModal: React.FC<ContentDisclaimerModalProps> = ({
  visible,
  onClose,
  onAccept,
  countryCode,
  languageCode,
  contentTypes = ['radio_streams', 'music', 'news']
}) => {
  const [disclaimers, setDisclaimers] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [userAge, setUserAge] = useState('');
  const [ageConfirmed, setAgeConfirmed] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [currentStep, setCurrentStep] = useState<'age' | 'disclaimers' | 'final'>('age');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (visible) {
      loadDisclaimers();
      resetModalState();
    }
  }, [visible, countryCode]);

  const resetModalState = () => {
    setUserAge('');
    setAgeConfirmed(false);
    setAgreedToTerms(false);
    setCurrentStep('age');
    setError(null);
  };

  const loadDisclaimers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const disclaimerData = await ContentDisclaimerService.getContentDisclaimers(
        countryCode,
        languageCode,
        contentTypes
      );
      
      setDisclaimers(disclaimerData);
    } catch (error) {
      console.error('Error loading disclaimers:', error);
      setError('Failed to load content disclaimers. Using default warnings.');
      // Load default disclaimers
      const defaultDisclaimers = ContentDisclaimerService.getDefaultDisclaimers(countryCode, languageCode);
      setDisclaimers(defaultDisclaimers);
    } finally {
      setLoading(false);
    }
  };

  const handleAgeSubmission = () => {
    const age = parseInt(userAge);
    
    if (!userAge || isNaN(age) || age < 1 || age > 120) {
      Alert.alert(
        languageCode.startsWith('pt') ? 'Idade Inválida' : 'Invalid Age',
        languageCode.startsWith('pt') 
          ? 'Por favor, insira uma idade válida (1-120 anos).' 
          : 'Please enter a valid age (1-120 years).'
      );
      return;
    }

    const adultThreshold = disclaimers?.regional_compliance?.adult_age_threshold || 18;
    
    if (age < adultThreshold) {
      Alert.alert(
        languageCode.startsWith('pt') ? 'Restrição de Idade' : 'Age Restriction',
        languageCode.startsWith('pt') 
          ? `Esta aplicação é destinada a adultos (${adultThreshold}+ anos). Você deve ter pelo menos ${adultThreshold} anos para usar este serviço.`
          : `This application is intended for adults (${adultThreshold}+ years). You must be at least ${adultThreshold} years old to use this service.`,
        [
          { 
            text: languageCode.startsWith('pt') ? 'Entendido' : 'Understood', 
            onPress: onClose 
          }
        ]
      );
      return;
    }

    setAgeConfirmed(true);
    setCurrentStep('disclaimers');
  };

  const handleAcceptDisclaimers = async () => {
    if (!agreedToTerms) {
      Alert.alert(
        languageCode.startsWith('pt') ? 'Termos Requeridos' : 'Terms Required',
        languageCode.startsWith('pt') 
          ? 'Você deve concordar com os termos e avisos para continuar.'
          : 'You must agree to the terms and disclaimers to continue.'
      );
      return;
    }

    try {
      const success = await ContentDisclaimerService.acknowledgeDisclaimers(
        disclaimers,
        countryCode,
        parseInt(userAge)
      );

      if (success) {
        setCurrentStep('final');
        // Auto-close after showing confirmation
        setTimeout(() => {
          onAccept();
        }, 2000);
      } else {
        Alert.alert(
          languageCode.startsWith('pt') ? 'Erro' : 'Error',
          languageCode.startsWith('pt') 
            ? 'Falha ao registrar aceitação. Tente novamente.'
            : 'Failed to record acceptance. Please try again.'
        );
      }
    } catch (error) {
      console.error('Error accepting disclaimers:', error);
      Alert.alert(
        languageCode.startsWith('pt') ? 'Erro' : 'Error',
        languageCode.startsWith('pt') 
          ? 'Ocorreu um erro. Tente novamente.'
          : 'An error occurred. Please try again.'
      );
    }
  };

  const getCountryName = () => {
    switch (countryCode) {
      case 'BR': return 'Brasil';
      case 'KE': return 'Kenya';
      default: return 'Global';
    }
  };

  const renderAgeVerification = () => (
    <View style={styles.stepContainer}>
      <View style={styles.stepHeader}>
        <Ionicons name="person-circle" size={48} color="#ff6b6b" />
        <Text style={styles.stepTitle}>
          {languageCode.startsWith('pt') ? 'Verificação de Idade' : 'Age Verification'}
        </Text>
        <Text style={styles.stepSubtitle}>
          {languageCode.startsWith('pt') 
            ? 'Esta aplicação contém conteúdo maduro'
            : 'This application contains mature content'}
        </Text>
      </View>
      
      <View style={styles.inputContainer}>
        <Text style={styles.inputLabel}>
          {languageCode.startsWith('pt') ? 'Sua idade:' : 'Your age:'}
        </Text>
        <TextInput
          style={styles.ageInput}
          value={userAge}
          onChangeText={setUserAge}
          placeholder={languageCode.startsWith('pt') ? 'Digite sua idade' : 'Enter your age'}
          placeholderTextColor="#999"
          keyboardType="number-pad"
          maxLength={3}
        />
      </View>

      <View style={styles.requirementBox}>
        <Text style={styles.requirementText}>
          {languageCode.startsWith('pt') 
            ? `• Você deve ter pelo menos ${disclaimers?.regional_compliance?.adult_age_threshold || 18} anos\n• Este serviço é destinado a adultos\n• Conteúdo pode incluir material explícito`
            : `• You must be at least ${disclaimers?.regional_compliance?.adult_age_threshold || 18} years old\n• This service is intended for adults\n• Content may include explicit material`}
        </Text>
      </View>

      <TouchableOpacity 
        style={[styles.continueButton, !userAge && styles.disabledButton]} 
        onPress={handleAgeSubmission}
        disabled={!userAge}
      >
        <Text style={styles.continueButtonText}>
          {languageCode.startsWith('pt') ? 'Continuar' : 'Continue'}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderDisclaimers = () => (
    <View style={styles.stepContainer}>
      <View style={styles.stepHeader}>
        <Ionicons name="warning" size={48} color="#ff6b6b" />
        <Text style={styles.stepTitle}>
          {languageCode.startsWith('pt') ? 'Avisos de Conteúdo' : 'Content Disclaimers'}
        </Text>
        <Text style={styles.stepSubtitle}>
          {getCountryName()} • {languageCode.startsWith('pt') ? 'Idade' : 'Age'}: {userAge}
        </Text>
      </View>

      <ScrollView style={styles.disclaimersScrollView} showsVerticalScrollIndicator={true}>
        {disclaimers?.content_disclaimers?.map((disclaimer: any, index: number) => (
          <View key={disclaimer.id} style={[
            styles.disclaimerCard,
            disclaimer.severity === 'critical' && styles.criticalDisclaimer,
            disclaimer.severity === 'warning' && styles.warningDisclaimer
          ]}>
            <View style={styles.disclaimerHeader}>
              <Ionicons 
                name={disclaimer.severity === 'critical' ? 'alert-circle' : 'information-circle'} 
                size={24} 
                color={disclaimer.severity === 'critical' ? '#f44336' : '#ff9800'} 
              />
              <Text style={styles.disclaimerTitle}>{disclaimer.title}</Text>
            </View>
            <Text style={styles.disclaimerContent}>{disclaimer.content}</Text>
            
            {disclaimer.applies_to && (
              <View style={styles.appliesTo}>
                <Text style={styles.appliesToLabel}>
                  {languageCode.startsWith('pt') ? 'Aplica-se a:' : 'Applies to:'}
                </Text>
                <Text style={styles.appliesToText}>
                  {disclaimer.applies_to.join(', ')}
                </Text>
              </View>
            )}
          </View>
        ))}

        {disclaimers?.regional_compliance && (
          <View style={styles.complianceCard}>
            <Text style={styles.complianceTitle}>
              {languageCode.startsWith('pt') ? 'Conformidade Regional' : 'Regional Compliance'}
            </Text>
            <Text style={styles.complianceText}>
              {languageCode.startsWith('pt') ? 'Sistema de Classificação:' : 'Rating System:'} {disclaimers.regional_compliance.content_rating_system}
            </Text>
            <Text style={styles.complianceText}>
              {languageCode.startsWith('pt') ? 'Idade Mínima para Adultos:' : 'Adult Age Threshold:'} {disclaimers.regional_compliance.adult_age_threshold}
            </Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.agreementContainer}>
        <TouchableOpacity 
          style={styles.checkboxContainer} 
          onPress={() => setAgreedToTerms(!agreedToTerms)}
        >
          <View style={[styles.checkbox, agreedToTerms && styles.checkedCheckbox]}>
            {agreedToTerms && <Ionicons name="checkmark" size={16} color="#fff" />}
          </View>
          <Text style={styles.agreementText}>
            {languageCode.startsWith('pt') 
              ? 'Eu li, entendi e concordo com todos os avisos e regulamentos de conteúdo acima.'
              : 'I have read, understood, and agree to all content warnings and regulations above.'}
          </Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity 
        style={[styles.acceptButton, !agreedToTerms && styles.disabledButton]} 
        onPress={handleAcceptDisclaimers}
        disabled={!agreedToTerms}
      >
        <Text style={styles.acceptButtonText}>
          {languageCode.startsWith('pt') ? 'Aceitar e Continuar' : 'Accept and Continue'}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderFinalConfirmation = () => (
    <View style={styles.stepContainer}>
      <View style={styles.stepHeader}>
        <Ionicons name="checkmark-circle" size={64} color="#4CAF50" />
        <Text style={styles.stepTitle}>
          {languageCode.startsWith('pt') ? 'Aceito!' : 'Accepted!'}
        </Text>
        <Text style={styles.stepSubtitle}>
          {languageCode.startsWith('pt') 
            ? 'Suas preferências foram registradas'
            : 'Your preferences have been recorded'}
        </Text>
      </View>
      
      <View style={styles.confirmationBox}>
        <Text style={styles.confirmationText}>
          {languageCode.startsWith('pt') 
            ? 'Você pode agora acessar o conteúdo do Kagema FM. Lembre-se de que você é responsável por garantir que o uso esteja em conformidade com as leis locais.'
            : 'You may now access Kagema FM content. Remember that you are responsible for ensuring usage complies with local laws.'}
        </Text>
      </View>

      <ActivityIndicator size="large" color="#ff6b6b" />
    </View>
  );

  if (!visible) return null;

  return (
    <Modal
      animationType="slide"
      transparent={false}
      visible={visible}
      presentationStyle="fullScreen"
    >
      <SafeAreaView style={styles.container}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardContainer}
        >
          <View style={styles.header}>
            <Text style={styles.headerTitle}>Kagema FM</Text>
            <Text style={styles.headerSubtitle}>
              {languageCode.startsWith('pt') ? 'Conformidade de Conteúdo' : 'Content Compliance'}
            </Text>
            {error && (
              <View style={styles.errorBanner}>
                <Ionicons name="warning-outline" size={16} color="#f44336" />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}
          </View>

          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#ff6b6b" />
              <Text style={styles.loadingText}>
                {languageCode.startsWith('pt') ? 'Carregando avisos...' : 'Loading disclaimers...'}
              </Text>
            </View>
          ) : (
            <View style={styles.content}>
              {currentStep === 'age' && renderAgeVerification()}
              {currentStep === 'disclaimers' && renderDisclaimers()}
              {currentStep === 'final' && renderFinalConfirmation()}
            </View>
          )}

          <View style={styles.footer}>
            <Text style={styles.footerText}>
              {languageCode.startsWith('pt') 
                ? 'Seus dados são mantidos localmente e em segurança'
                : 'Your data is kept locally and securely'}
            </Text>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  keyboardContainer: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#2d2d54',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#ff6b6b',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#8B0000',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginTop: 10,
  },
  errorText: {
    color: '#fff',
    fontSize: 12,
    marginLeft: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#ccc',
    marginTop: 16,
    fontSize: 16,
  },
  content: {
    flex: 1,
  },
  stepContainer: {
    flex: 1,
    padding: 20,
  },
  stepHeader: {
    alignItems: 'center',
    marginBottom: 30,
  },
  stepTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 12,
    textAlign: 'center',
  },
  stepSubtitle: {
    fontSize: 14,
    color: '#ccc',
    marginTop: 8,
    textAlign: 'center',
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 8,
    fontWeight: '500',
  },
  ageInput: {
    backgroundColor: '#2d2d54',
    color: '#fff',
    fontSize: 18,
    padding: 15,
    borderRadius: 8,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  requirementBox: {
    backgroundColor: '#2d2d54',
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#ff6b6b',
    marginBottom: 20,
  },
  requirementText: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 22,
  },
  disclaimersScrollView: {
    flex: 1,
    marginBottom: 20,
  },
  disclaimerCard: {
    backgroundColor: '#2d2d54',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#ccc',
  },
  criticalDisclaimer: {
    borderLeftColor: '#f44336',
    backgroundColor: '#2d1a1a',
  },
  warningDisclaimer: {
    borderLeftColor: '#ff9800',
  },
  disclaimerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  disclaimerTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 12,
    flex: 1,
  },
  disclaimerContent: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 12,
  },
  appliesTo: {
    backgroundColor: 'rgba(255, 107, 107, 0.1)',
    padding: 8,
    borderRadius: 6,
  },
  appliesToLabel: {
    color: '#ff6b6b',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  appliesToText: {
    color: '#ccc',
    fontSize: 12,
  },
  complianceCard: {
    backgroundColor: '#1a2d1a',
    padding: 16,
    borderRadius: 8,
    marginTop: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  complianceTitle: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  complianceText: {
    color: '#ccc',
    fontSize: 14,
    marginBottom: 6,
  },
  agreementContainer: {
    marginBottom: 20,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: '#ff6b6b',
    borderRadius: 4,
    marginRight: 12,
    marginTop: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkedCheckbox: {
    backgroundColor: '#ff6b6b',
  },
  agreementText: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 20,
    flex: 1,
  },
  continueButton: {
    backgroundColor: '#ff6b6b',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  acceptButton: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#666',
  },
  continueButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  acceptButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  confirmationBox: {
    backgroundColor: '#1a2d1a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 30,
    borderWidth: 1,
    borderColor: '#4CAF50',
  },
  confirmationText: {
    color: '#ccc',
    fontSize: 16,
    lineHeight: 24,
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderTopWidth: 1,
    borderTopColor: '#2d2d54',
  },
  footerText: {
    color: '#999',
    fontSize: 12,
    textAlign: 'center',
  },
});

export default ContentDisclaimerModal;