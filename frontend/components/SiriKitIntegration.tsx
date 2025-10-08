import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  ScrollView, 
  Alert,
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import siriKitService, { SiriShortcut, SiriKitState } from '../services/SiriKitService';
import VoiceControlService from '../services/VoiceControlService';

interface SiriKitIntegrationProps {
  onVoiceCommand?: (command: string, response: any) => void;
}

/**
 * SiriKit Integration Component
 * 
 * Features:
 * - Voice command activation with advanced patterns
 * - Siri Shortcuts management and registration
 * - Visual feedback for voice interactions
 * - Integration with existing voice control system
 * - Advanced command examples and help
 */
export const SiriKitIntegration: React.FC<SiriKitIntegrationProps> = ({
  onVoiceCommand
}) => {
  const [siriState, setSiriState] = useState<SiriKitState>(siriKitService.getState());
  const [isTestingVoice, setIsTestingVoice] = useState(false);
  const [lastCommandResult, setLastCommandResult] = useState<string>('');

  useEffect(() => {
    // Listen for SiriKit state changes
    const unsubscribe = siriKitService.addListener(setSiriState);

    return () => {
      unsubscribe();
    };
  }, []);

  /**
   * Start voice listening session
   */
  const handleStartVoiceListening = async () => {
    try {
      setIsTestingVoice(true);
      const success = await siriKitService.startVoiceListening();
      
      if (success) {
        setLastCommandResult('🎙️ Listening for voice commands...');
        
        // Auto-stop after 10 seconds
        setTimeout(async () => {
          await siriKitService.stopVoiceListening();
          setIsTestingVoice(false);
          if (lastCommandResult.includes('Listening')) {
            setLastCommandResult('👂 Listening session ended');
          }
        }, 10000);
      } else {
        setIsTestingVoice(false);
        setLastCommandResult('❌ Failed to start voice listening');
      }
    } catch (error) {
      setIsTestingVoice(false);
      setLastCommandResult(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  /**
   * Test advanced voice command processing
   */
  const handleTestAdvancedCommand = async (testCommand: string) => {
    try {
      setLastCommandResult('🔄 Processing advanced command...');
      
      const response = await siriKitService.processTextCommand(testCommand);
      
      if (response.success) {
        setLastCommandResult(`✅ ${response.message}`);
        onVoiceCommand?.(testCommand, response);
      } else {
        setLastCommandResult(`❌ ${response.message}`);
      }
    } catch (error) {
      setLastCommandResult(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  /**
   * Register a custom Siri Shortcut
   */
  const handleRegisterShortcut = async (shortcut: SiriShortcut) => {
    try {
      const success = await siriKitService.registerShortcut(shortcut);
      
      if (success) {
        Alert.alert(
          '✅ Shortcut Registered',
          `"${shortcut.title}" has been added to your Siri shortcuts. You can now say "${shortcut.phrase}" to activate it.`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('❌ Registration Failed', 'Could not register the Siri shortcut.');
      }
    } catch (error) {
      Alert.alert('❌ Error', `Failed to register shortcut: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  /**
   * Advanced command examples for testing
   */
  const advancedTestCommands = [
    'Find Brazilian radio stations',
    'Play Portuguese radio stations', 
    'Find jazz radio stations',
    'Play offline content',
    'Find Kenyan radio stations',
    'Search for news radio',
    'Download for offline listening',
    'Find European radio stations'
  ];

  if (!siriState.isAvailable) {
    return (
      <View style={styles.unavailableContainer}>
        <Ionicons name="phone-portrait-outline" size={48} color="#666" />
        <Text style={styles.unavailableText}>
          SiriKit integration is only available on iOS devices
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="mic" size={32} color="#007AFF" />
        <Text style={styles.title}>SiriKit Integration</Text>
        <Text style={styles.subtitle}>Advanced Voice Commands for Kagema FM</Text>
      </View>

      {/* Voice Control Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎙️ Voice Commands</Text>
        
        <TouchableOpacity 
          style={[
            styles.voiceButton,
            isTestingVoice && styles.voiceButtonActive
          ]}
          onPress={handleStartVoiceListening}
          disabled={isTestingVoice}
        >
          <Ionicons 
            name={isTestingVoice ? "radio-button-on" : "mic"} 
            size={24} 
            color="white" 
          />
          <Text style={styles.voiceButtonText}>
            {isTestingVoice ? 'Listening...' : 'Start Voice Command'}
          </Text>
        </TouchableOpacity>

        {lastCommandResult ? (
          <View style={styles.resultContainer}>
            <Text style={styles.resultText}>{lastCommandResult}</Text>
          </View>
        ) : null}
      </View>

      {/* Advanced Commands Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🌍 Advanced Commands</Text>
        <Text style={styles.sectionDescription}>
          Test advanced voice commands for international radio discovery and offline content
        </Text>
        
        <View style={styles.commandsGrid}>
          {advancedTestCommands.map((command, index) => (
            <TouchableOpacity
              key={index}
              style={styles.commandButton}
              onPress={() => handleTestAdvancedCommand(command)}
            >
              <Text style={styles.commandButtonText}>"{command}"</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Siri Shortcuts Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📝 Siri Shortcuts</Text>
        <Text style={styles.sectionDescription}>
          {siriState.shortcuts.length} shortcuts available for quick access
        </Text>
        
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.shortcutsContainer}>
            {siriState.shortcuts.map((shortcut, index) => (
              <View key={shortcut.id} style={styles.shortcutCard}>
                <View style={styles.shortcutHeader}>
                  <Text style={styles.shortcutTitle}>{shortcut.title}</Text>
                  <Text style={styles.shortcutCategory}>{shortcut.category}</Text>
                </View>
                <Text style={styles.shortcutPhrase}>"{shortcut.phrase}"</Text>
                <Text style={styles.shortcutDescription}>
                  {shortcut.description}
                </Text>
                
                <TouchableOpacity
                  style={styles.addShortcutButton}
                  onPress={() => handleRegisterShortcut(shortcut)}
                >
                  <Ionicons name="add-circle" size={20} color="#007AFF" />
                  <Text style={styles.addShortcutText}>Add to Siri</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        </ScrollView>
      </View>

      {/* Voice Commands Help */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💡 Voice Command Examples</Text>
        
        <View style={styles.helpContainer}>
          <Text style={styles.helpCategory}>🌍 Regional Discovery:</Text>
          <Text style={styles.helpText}>• "Find Brazilian radio stations"</Text>
          <Text style={styles.helpText}>• "Play Kenyan radio"</Text>
          <Text style={styles.helpText}>• "Show me European stations"</Text>
          
          <Text style={styles.helpCategory}>🗣️ Language-Specific:</Text>
          <Text style={styles.helpText}>• "Play Portuguese radio stations"</Text>
          <Text style={styles.helpText}>• "Find Swahili speaking radio"</Text>
          
          <Text style={styles.helpCategory}>🎵 Genre & Content:</Text>
          <Text style={styles.helpText}>• "Find jazz radio stations"</Text>
          <Text style={styles.helpText}>• "Play news radio"</Text>
          <Text style={styles.helpText}>• "Search for classical music"</Text>
          
          <Text style={styles.helpCategory}>📱 Offline Features:</Text>
          <Text style={styles.helpText}>• "Play offline content"</Text>
          <Text style={styles.helpText}>• "Download for offline listening"</Text>
        </View>
      </View>

      {/* Status Information */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Status</Text>
        
        <View style={styles.statusContainer}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>SiriKit Available:</Text>
            <Text style={[
              styles.statusValue,
              siriState.isAvailable ? styles.statusSuccess : styles.statusError
            ]}>
              {siriState.isAvailable ? '✅ Yes' : '❌ No'}
            </Text>
          </View>
          
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Voice Listening:</Text>
            <Text style={[
              styles.statusValue,
              siriState.isListening ? styles.statusActive : styles.statusInactive
            ]}>
              {siriState.isListening ? '🎙️ Active' : '💤 Inactive'}
            </Text>
          </View>
          
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Shortcuts Registered:</Text>
            <Text style={styles.statusValue}>
              {siriState.shortcuts.length}
            </Text>
          </View>
          
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Voice Control Available:</Text>
            <Text style={[
              styles.statusValue,
              VoiceControlService.available ? styles.statusSuccess : styles.statusError
            ]}>
              {VoiceControlService.available ? '✅ Yes' : '❌ No'}
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  unavailableContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#f8f9fa',
  },
  unavailableText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  header: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1d1d1d',
    marginTop: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  section: {
    backgroundColor: 'white',
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1d1d1d',
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    lineHeight: 20,
  },
  voiceButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 16,
  },
  voiceButtonActive: {
    backgroundColor: '#FF3B30',
  },
  voiceButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  resultContainer: {
    backgroundColor: '#f1f3f4',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  resultText: {
    fontSize: 14,
    color: '#1d1d1d',
    lineHeight: 20,
  },
  commandsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  commandButton: {
    backgroundColor: '#f1f3f4',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  commandButtonText: {
    fontSize: 13,
    color: '#007AFF',
    fontStyle: 'italic',
  },
  shortcutsContainer: {
    flexDirection: 'row',
    paddingRight: 16,
  },
  shortcutCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginRight: 12,
    width: 240,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  shortcutHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  shortcutTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1d1d1d',
    flex: 1,
  },
  shortcutCategory: {
    fontSize: 12,
    color: '#007AFF',
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    overflow: 'hidden',
  },
  shortcutPhrase: {
    fontSize: 14,
    color: '#007AFF',
    fontStyle: 'italic',
    marginBottom: 6,
  },
  shortcutDescription: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 12,
  },
  addShortcutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'white',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  addShortcutText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
    marginLeft: 4,
  },
  helpContainer: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  helpCategory: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1d1d1d',
    marginTop: 12,
    marginBottom: 4,
  },
  helpText: {
    fontSize: 13,
    color: '#666',
    marginLeft: 8,
    marginBottom: 2,
    lineHeight: 18,
  },
  statusContainer: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    overflow: 'hidden',
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e8ed',
  },
  statusLabel: {
    fontSize: 14,
    color: '#1d1d1d',
    fontWeight: '500',
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  statusSuccess: {
    color: '#28a745',
  },
  statusError: {
    color: '#dc3545',
  },
  statusActive: {
    color: '#007AFF',
  },
  statusInactive: {
    color: '#666',
  },
});

export default SiriKitIntegration;