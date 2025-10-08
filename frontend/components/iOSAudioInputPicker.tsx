import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Platform,
  Alert,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { iOSAudioInputPickerService, AudioInputState, AudioInputDevice } from '../services/iOSAudioInputPickerService';

interface iOSAudioInputPickerProps {
  onInputSelected?: (input: AudioInputDevice) => void;
  showManualPicker?: boolean;
  style?: any;
}

export const iOSAudioInputPicker: React.FC<iOSAudioInputPickerProps> = ({
  onInputSelected,
  showManualPicker = false,
  style
}) => {
  const [audioState, setAudioState] = useState<AudioInputState>({
    availableInputs: [],
    selectedInput: null,
    isPickerVisible: false
  });
  const [showManualModal, setShowManualModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Subscribe to audio input state changes
    const unsubscribe = iOSAudioInputPickerService.addListener((state) => {
      setAudioState(state);
    });

    // Initialize with current state
    setAudioState(iOSAudioInputPickerService.getState());

    return unsubscribe;
  }, []);

  // Present the native iOS audio input picker
  const handlePresentNativePicker = async () => {
    if (!iOSAudioInputPickerService.isInputPickerAvailable()) {
      Alert.alert(
        'Not Available',
        'Audio input picker is only available on iOS devices with proper audio session configuration.',
        [{ text: 'OK' }]
      );
      return;
    }

    setIsLoading(true);
    try {
      const success = await iOSAudioInputPickerService.presentInputPicker();
      
      if (!success) {
        Alert.alert(
          'Error',
          'Failed to present audio input picker. Please try again.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('❌ Failed to present audio input picker:', error);
      Alert.alert(
        'Error',
        'An error occurred while trying to show the audio input picker.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Handle manual input selection from modal
  const handleManualInputSelection = async (input: AudioInputDevice) => {
    try {
      const success = await iOSAudioInputPickerService.selectAudioInput(input.id);
      
      if (success) {
        setShowManualModal(false);
        onInputSelected?.(input);
      } else {
        Alert.alert(
          'Selection Failed',
          'Failed to select the audio input. Please try again.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('❌ Failed to select audio input:', error);
      Alert.alert(
        'Error',
        'An error occurred while selecting the audio input.',
        [{ text: 'OK' }]
      );
    }
  };

  // Refresh available inputs
  const handleRefreshInputs = async () => {
    setIsLoading(true);
    try {
      await iOSAudioInputPickerService.refreshInputs();
    } catch (error) {
      console.error('❌ Failed to refresh inputs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Get icon for audio input type
  const getInputIcon = (type: string): keyof typeof Ionicons.glyphMap => {
    switch (type) {
      case 'bluetooth':
        return 'bluetooth';
      case 'airplay':
        return 'logo-apple';
      case 'wired':
        return 'headset';
      case 'builtin':
        return 'phone-portrait';
      default:
        return 'volume-medium';
    }
  };

  // Get input type display name
  const getInputTypeLabel = (type: string): string => {
    switch (type) {
      case 'bluetooth':
        return 'Bluetooth';
      case 'airplay':
        return 'AirPlay';
      case 'wired':
        return 'Wired';
      case 'builtin':
        return 'Built-in';
      default:
        return 'Other';
    }
  };

  // Render individual input device item
  const renderInputItem = ({ item }: { item: AudioInputDevice }) => (
    <TouchableOpacity
      style={[
        styles.inputItem,
        item.isSelected && styles.inputItemSelected
      ]}
      onPress={() => handleManualInputSelection(item)}
    >
      <View style={styles.inputItemContent}>
        <Ionicons
          name={getInputIcon(item.type)}
          size={24}
          color={item.isSelected ? '#FF6B6B' : '#666'}
          style={styles.inputIcon}
        />
        <View style={styles.inputInfo}>
          <Text style={[
            styles.inputName,
            item.isSelected && styles.inputNameSelected
          ]}>
            {item.name}
          </Text>
          <Text style={styles.inputType}>
            {getInputTypeLabel(item.type)}
          </Text>
        </View>
        {item.isSelected && (
          <Ionicons
            name="checkmark-circle"
            size={24}
            color="#FF6B6B"
          />
        )}
      </View>
    </TouchableOpacity>
  );

  // Don't render on non-iOS platforms
  if (Platform.OS !== 'ios') {
    return null;
  }

  return (
    <View style={[styles.container, style]}>
      {/* Current Audio Output Display */}
      <View style={styles.currentOutputContainer}>
        <View style={styles.currentOutputInfo}>
          <Ionicons
            name={audioState.selectedInput ? getInputIcon(audioState.selectedInput.type) : 'volume-medium'}
            size={20}
            color="#666"
            style={styles.currentOutputIcon}
          />
          <Text style={styles.currentOutputText}>
            {audioState.selectedInput ? audioState.selectedInput.name : 'Default Output'}
          </Text>
        </View>
        
        {/* Native Picker Button */}
        <TouchableOpacity
          style={[styles.pickerButton, isLoading && styles.pickerButtonDisabled]}
          onPress={handlePresentNativePicker}
          disabled={isLoading || audioState.isPickerVisible}
        >
          <Ionicons
            name="options"
            size={18}
            color={isLoading ? '#ccc' : '#FF6B6B'}
          />
        </TouchableOpacity>
      </View>

      {/* Manual Picker Toggle (if enabled) */}
      {showManualPicker && (
        <View style={styles.manualPickerContainer}>
          <TouchableOpacity
            style={styles.manualPickerButton}
            onPress={() => setShowManualModal(true)}
          >
            <Text style={styles.manualPickerButtonText}>
              Choose Audio Output
            </Text>
            <Ionicons name="chevron-forward" size={16} color="#666" />
          </TouchableOpacity>
        </View>
      )}

      {/* Loading/Picker Status */}
      {(isLoading || audioState.isPickerVisible) && (
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>
            {audioState.isPickerVisible ? '🎧 Audio input picker is open...' : '⏳ Loading audio inputs...'}
          </Text>
        </View>
      )}

      {/* Manual Selection Modal */}
      <Modal
        visible={showManualModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowManualModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Choose Audio Output</Text>
            <TouchableOpacity
              style={styles.modalCloseButton}
              onPress={() => setShowManualModal(false)}
            >
              <Ionicons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>

          <View style={styles.modalActions}>
            <TouchableOpacity
              style={styles.refreshButton}
              onPress={handleRefreshInputs}
              disabled={isLoading}
            >
              <Ionicons
                name="refresh"
                size={16}
                color={isLoading ? '#ccc' : '#FF6B6B'}
              />
              <Text style={[styles.refreshButtonText, isLoading && styles.refreshButtonTextDisabled]}>
                Refresh
              </Text>
            </TouchableOpacity>
          </View>

          <FlatList
            data={audioState.availableInputs}
            renderItem={renderInputItem}
            keyExtractor={(item) => item.id}
            style={styles.inputList}
            showsVerticalScrollIndicator={false}
          />
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
  },
  currentOutputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  currentOutputInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  currentOutputIcon: {
    marginRight: 8,
  },
  currentOutputText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  pickerButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  pickerButtonDisabled: {
    opacity: 0.5,
  },
  manualPickerContainer: {
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  manualPickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  manualPickerButtonText: {
    fontSize: 16,
    color: '#666',
  },
  statusContainer: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  modalCloseButton: {
    padding: 4,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: '#f8f9fa',
  },
  refreshButtonText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#FF6B6B',
    fontWeight: '500',
  },
  refreshButtonTextDisabled: {
    color: '#ccc',
  },
  inputList: {
    flex: 1,
  },
  inputItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  inputItemSelected: {
    backgroundColor: '#fff5f5',
  },
  inputItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  inputIcon: {
    marginRight: 12,
  },
  inputInfo: {
    flex: 1,
  },
  inputName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  inputNameSelected: {
    color: '#FF6B6B',
  },
  inputType: {
    fontSize: 14,
    color: '#666',
  },
});

export default iOSAudioInputPicker;