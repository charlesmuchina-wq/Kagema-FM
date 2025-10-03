// AI Voice Assistant Component
// Provides voice control interface for radio operations using speech recognition

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  SafeAreaView,
  ActivityIndicator,
  ScrollView,
  Alert,
  Animated,
  Dimensions
} from 'react-native';
import VoiceControlService, { VoiceCommand, VoiceResponse } from '../services/VoiceControlService';
import { shadowStyles } from '../utils/shadowStyles';

interface AIVoiceAssistantProps {
  visible: boolean;
  onClose: () => void;
  onVoiceCommand: (command: VoiceCommand, response: VoiceResponse) => void;
}

const { width } = Dimensions.get('window');

const AIVoiceAssistant: React.FC<AIVoiceAssistantProps> = ({
  visible,
  onClose,
  onVoiceCommand
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastCommand, setLastCommand] = useState<VoiceCommand | null>(null);
  const [lastResponse, setLastResponse] = useState<VoiceResponse | null>(null);
  const [commandHistory, setCommandHistory] = useState<Array<{command: VoiceCommand, response: VoiceResponse}>>([]);
  const [isAvailable, setIsAvailable] = useState(false);
  const [helpVisible, setHelpVisible] = useState(false);
  
  const pulseAnim = new Animated.Value(1);
  const waveAnim = new Animated.Value(0);

  useEffect(() => {
    if (visible) {
      checkVoiceAvailability();
      setupVoiceCallbacks();
    }
    
    return () => {
      cleanupVoiceCallbacks();
    };
  }, [visible]);

  useEffect(() => {
    if (isListening) {
      startPulseAnimation();
      startWaveAnimation();
    } else {
      stopAnimations();
    }
  }, [isListening]);

  const checkVoiceAvailability = async () => {
    const available = VoiceControlService.available;
    setIsAvailable(available);
    
    if (!available) {
      Alert.alert(
        'Voice Control Unavailable',
        'Voice recognition is not supported on this device or browser.',
        [{ text: 'OK' }]
      );
    }
  };

  const setupVoiceCallbacks = () => {
    VoiceControlService.onCommand(handleVoiceCommand);
    VoiceControlService.onResponse(handleVoiceResponse);
  };

  const cleanupVoiceCallbacks = () => {
    VoiceControlService.removeCommandCallback(handleVoiceCommand);
    VoiceControlService.removeResponseCallback(handleVoiceResponse);
  };

  const handleVoiceCommand = (command: VoiceCommand) => {
    setLastCommand(command);
    setIsProcessing(true);
  };

  const handleVoiceResponse = (response: VoiceResponse) => {
    setLastResponse(response);
    setIsProcessing(false);
    setIsListening(false);
    
    if (lastCommand) {
      const historyEntry = { command: lastCommand, response };
      setCommandHistory(prev => [historyEntry, ...prev.slice(0, 4)]); // Keep last 5 entries
      onVoiceCommand(lastCommand, response);
    }
  };

  const startListening = async () => {
    if (!isAvailable) {
      Alert.alert('Voice Control Unavailable', 'Voice recognition is not available');
      return;
    }

    try {
      console.log('🎤 Starting AI voice assistant...');
      setIsListening(true);
      setIsProcessing(false);
      setLastCommand(null);
      setLastResponse(null);
      
      await VoiceControlService.startListening();
      console.log('✅ Voice recognition started successfully');
    } catch (error) {
      console.error('❌ Error starting voice recognition:', error);
      setIsListening(false);
      Alert.alert('Voice Error', 'Failed to start voice recognition. Please check your microphone permissions.');
    }
  };

  const stopListening = async () => {
    try {
      console.log('🎤 Stopping AI voice assistant...');
      await VoiceControlService.stopListening();
      setIsListening(false);
      setIsProcessing(false);
      console.log('✅ Voice recognition stopped');
    } catch (error) {
      console.error('❌ Error stopping voice recognition:', error);
    }
  };

  // New method to manually process voice command using enhanced backend
  const processVoiceInput = async (transcript: string) => {
    try {
      console.log('🎤 Processing voice input with enhanced backend:', transcript);
      setIsProcessing(true);
      
      const response = await VoiceControlService.processVoiceCommand(transcript);
      
      if (response.success) {
        console.log('✅ Voice command processed successfully:', response);
        
        // Create mock command for compatibility
        const command: VoiceCommand = {
          intent: response.action || 'unknown',
          parameters: response.data || {},
          confidence: 0.9,
          originalText: transcript
        };

        // Create response
        const voiceResponse: VoiceResponse = {
          success: true,
          message: response.message || 'Command executed',
          action: response.action,
          data: response.data
        };

        // Update state
        setLastCommand(command);
        setLastResponse(voiceResponse);
        setIsProcessing(false);
        setIsListening(false);

        // Add to history
        const historyEntry = { command, response: voiceResponse };
        setCommandHistory(prev => [historyEntry, ...prev.slice(0, 4)]);

        // Call parent callback
        onVoiceCommand(command, voiceResponse);

      } else {
        console.error('❌ Voice command processing failed:', response.message);
        const errorResponse: VoiceResponse = {
          success: false,
          message: response.message || 'Processing failed'
        };
        
        setLastResponse(errorResponse);
        setIsProcessing(false);
        setIsListening(false);
      }

    } catch (error) {
      console.error('❌ Error in processVoiceInput:', error);
      const errorResponse: VoiceResponse = {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error'
      };
      
      setLastResponse(errorResponse);
      setIsProcessing(false);
      setIsListening(false);
    }
  };

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const startWaveAnimation = () => {
    Animated.loop(
      Animated.timing(waveAnim, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: true,
      })
    ).start();
  };

  const stopAnimations = () => {
    pulseAnim.stopAnimation();
    waveAnim.stopAnimation();
    Animated.timing(pulseAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
    Animated.timing(waveAnim, {
      toValue: 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const getStatusText = () => {
    if (!isAvailable) return 'Voice recognition unavailable';
    if (isProcessing) return 'Processing your command...';
    if (isListening) return 'Listening... Speak now!';
    return 'Tap to start voice command';
  };

  const getStatusColor = () => {
    if (!isAvailable) return '#999';
    if (isProcessing) return '#FF9500';
    if (isListening) return '#FF3B30';
    return '#007AFF';
  };

  const renderCommandHistory = () => {
    if (commandHistory.length === 0) {
      return (
        <View style={styles.emptyHistory}>
          <Text style={styles.emptyHistoryText}>No voice commands yet</Text>
          <Text style={styles.emptyHistorySubtext}>
            Try saying "play radio" or "next station"
          </Text>
        </View>
      );
    }

    return (
      <ScrollView style={styles.historyScroll} showsVerticalScrollIndicator={false}>
        {commandHistory.map((entry, index) => (
          <View key={index} style={styles.historyItem}>
            <View style={styles.historyCommand}>
              <Text style={styles.historyCommandText}>
                "{entry.command.originalText}"
              </Text>
              <Text style={styles.historyIntent}>
                Intent: {entry.command.intent}
              </Text>
              {entry.command.confidence > 0 && (
                <Text style={styles.historyConfidence}>
                  Confidence: {Math.round(entry.command.confidence * 100)}%
                </Text>
              )}
            </View>
            <View style={[
              styles.historyResponse,
              { backgroundColor: entry.response.success ? '#E8F5E8' : '#FFE8E8' }
            ]}>
              <Text style={[
                styles.historyResponseText,
                { color: entry.response.success ? '#2E7D32' : '#C62828' }
              ]}>
                {entry.response.message}
              </Text>
            </View>
          </View>
        ))}
      </ScrollView>
    );
  };

  const renderHelpModal = () => (
    <Modal
      visible={helpVisible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.helpContainer}>
        <View style={styles.helpHeader}>
          <Text style={styles.helpTitle}>Voice Commands Help</Text>
          <TouchableOpacity
            onPress={() => setHelpVisible(false)}
            style={styles.helpCloseButton}
          >
            <Text style={styles.helpCloseText}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.helpContent}>
          <Text style={styles.helpSectionTitle}>Radio Control Commands:</Text>
          {VoiceControlService.getCommands().map((command, index) => (
            <View key={index} style={styles.helpCommandItem}>
              <Text style={styles.helpCommandText}>"{command}"</Text>
            </View>
          ))}
          
          <Text style={styles.helpSectionTitle}>Tips for Better Recognition:</Text>
          <View style={styles.helpTip}>
            <Text style={styles.helpTipText}>• Speak clearly and at normal speed</Text>
          </View>
          <View style={styles.helpTip}>
            <Text style={styles.helpTipText}>• Use simple, direct commands</Text>
          </View>
          <View style={styles.helpTip}>
            <Text style={styles.helpTipText}>• Ensure you have microphone permissions</Text>
          </View>
          <View style={styles.helpTip}>
            <Text style={styles.helpTipText}>• Reduce background noise when possible</Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );

  return (
    <>
      <Modal
        visible={visible}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.container}>
          <View style={styles.header}>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
            <Text style={styles.headerTitle}>AI Voice Assistant</Text>
            <TouchableOpacity
              onPress={() => setHelpVisible(true)}
              style={styles.helpButton}
            >
              <Text style={styles.helpButtonText}>?</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.content}>
            {/* Voice Control Interface */}
            <View style={styles.voiceInterface}>
              <Text style={styles.statusText}>{getStatusText()}</Text>
              
              {/* Animated Voice Button */}
              <View style={styles.voiceButtonContainer}>
                {/* Wave Animation Background */}
                {isListening && (
                  <Animated.View
                    style={[
                      styles.waveCircle,
                      {
                        opacity: waveAnim,
                        transform: [
                          {
                            scale: waveAnim.interpolate({
                              inputRange: [0, 1],
                              outputRange: [1, 2],
                            }),
                          },
                        ],
                      },
                    ]}
                  />
                )}
                
                {/* Main Voice Button */}
                <Animated.View
                  style={[
                    styles.voiceButton,
                    { transform: [{ scale: pulseAnim }] },
                    { 
                      backgroundColor: isListening ? '#FF3B30' : 
                                      isProcessing ? '#FF9500' : '#007AFF',
                      opacity: !isAvailable ? 0.5 : 1
                    }
                  ]}
                >
                  <TouchableOpacity
                    onPress={isListening ? stopListening : startListening}
                    disabled={!isAvailable || isProcessing}
                    style={styles.voiceButtonTouch}
                  >
                    {isProcessing ? (
                      <ActivityIndicator size="large" color="white" />
                    ) : (
                      <Text style={styles.voiceButtonIcon}>
                        {isListening ? '🎙️' : '🎤'}
                      </Text>
                    )}
                  </TouchableOpacity>
                </Animated.View>
              </View>

              <Text style={[styles.instructionText, { color: getStatusColor() }]}>
                {isListening ? 'Listening for your command...' :
                 isProcessing ? 'Processing...' :
                 'Tap the microphone to give a voice command'}
              </Text>
            </View>

            {/* Current Command Display */}
            {(lastCommand || lastResponse) && (
              <View style={styles.currentCommandContainer}>
                <Text style={styles.currentCommandTitle}>Latest Command:</Text>
                {lastCommand && (
                  <View style={styles.commandDisplay}>
                    <Text style={styles.commandText}>
                      "{lastCommand.originalText}"
                    </Text>
                    <Text style={styles.intentText}>
                      Detected: {lastCommand.intent}
                      {lastCommand.confidence > 0 && 
                        ` (${Math.round(lastCommand.confidence * 100)}% confidence)`
                      }
                    </Text>
                  </View>
                )}
                {lastResponse && (
                  <View style={[
                    styles.responseDisplay,
                    { backgroundColor: lastResponse.success ? '#E8F5E8' : '#FFE8E8' }
                  ]}>
                    <Text style={[
                      styles.responseText,
                      { color: lastResponse.success ? '#2E7D32' : '#C62828' }
                    ]}>
                      {lastResponse.message}
                    </Text>
                  </View>
                )}
              </View>
            )}

            {/* Test Voice Commands */}
            <View style={styles.testCommandsContainer}>
              <Text style={styles.testCommandsTitle}>Quick Test Commands:</Text>
              <View style={styles.testButtonsRow}>
                <TouchableOpacity
                  style={styles.testButton}
                  onPress={() => processVoiceInput('play some jazz music')}
                  disabled={isProcessing}
                >
                  <Text style={styles.testButtonText}>Play Jazz</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.testButton}
                  onPress={() => processVoiceInput('pause the radio')}
                  disabled={isProcessing}
                >
                  <Text style={styles.testButtonText}>Pause</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.testButton}
                  onPress={() => processVoiceInput('next station')}
                  disabled={isProcessing}
                >
                  <Text style={styles.testButtonText}>Next Station</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Command History */}
            <View style={styles.historyContainer}>
              <Text style={styles.historyTitle}>Recent Commands</Text>
              {renderCommandHistory()}
            </View>
          </View>
        </SafeAreaView>
      </Modal>

      {renderHelpModal()}
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    minHeight: 60,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#666',
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#333',
  },
  helpButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  helpButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  voiceInterface: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#fff',
    borderRadius: 16,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 24,
  },
  voiceButtonContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  waveCircle: {
    position: 'absolute',
    width: 160,
    height: 160,
    borderRadius: 80,
    backgroundColor: '#FF3B30',
    opacity: 0.3,
  },
  voiceButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  voiceButtonTouch: {
    width: '100%',
    height: '100%',
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceButtonIcon: {
    fontSize: 40,
  },
  instructionText: {
    fontSize: 14,
    textAlign: 'center',
    paddingHorizontal: 20,
    lineHeight: 20,
  },
  currentCommandContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  currentCommandTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  commandDisplay: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  commandText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  intentText: {
    fontSize: 12,
    color: '#666',
  },
  responseDisplay: {
    borderRadius: 8,
    padding: 12,
  },
  responseText: {
    fontSize: 14,
    fontWeight: '500',
  },
  historyContainer: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    margin: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  historyTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  testCommandsContainer: {
    marginTop: 16,
    marginBottom: 8,
    paddingHorizontal: 16,
  },
  testCommandsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
    color: '#666',
  },
  testButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  testButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 36,
    justifyContent: 'center',
  },
  testButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  historyScroll: {
    flex: 1,
  },
  emptyHistory: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyHistoryText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  emptyHistorySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  historyItem: {
    marginBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    paddingBottom: 12,
  },
  historyCommand: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 8,
    marginBottom: 8,
  },
  historyCommandText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  historyIntent: {
    fontSize: 11,
    color: '#666',
    marginBottom: 2,
  },
  historyConfidence: {
    fontSize: 11,
    color: '#007AFF',
  },
  historyResponse: {
    borderRadius: 8,
    padding: 8,
  },
  historyResponseText: {
    fontSize: 13,
    fontWeight: '500',
  },
  // Help Modal Styles
  helpContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  helpHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  helpTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  helpCloseButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  helpCloseText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#666',
  },
  helpContent: {
    flex: 1,
    padding: 16,
  },
  helpSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 12,
  },
  helpCommandItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  helpCommandText: {
    fontSize: 14,
    color: '#333',
  },
  helpTip: {
    backgroundColor: '#E3F2FD',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  helpTipText: {
    fontSize: 14,
    color: '#1976D2',
  },
});

export default AIVoiceAssistant;