import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { sleepTimerService, SleepTimerState, SleepTimerOptions } from '../services/SleepTimerService';

interface SleepTimerComponentProps {
  visible: boolean;
  onClose: () => void;
  style?: any;
}

export const SleepTimerComponent: React.FC<SleepTimerComponentProps> = ({
  visible,
  onClose,
  style
}) => {
  const [timerState, setTimerState] = useState<SleepTimerState>(sleepTimerService.getState());
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customMinutes, setCustomMinutes] = useState('');
  const [fadeOutEnabled, setFadeOutEnabled] = useState(true);
  const [notificationEnabled, setNotificationEnabled] = useState(true);

  useEffect(() => {
    // Subscribe to timer state changes
    const unsubscribe = sleepTimerService.addListener(setTimerState);
    
    // Initialize with current state
    setTimerState(sleepTimerService.getState());

    return unsubscribe;
  }, []);

  const handlePresetSelect = async (minutes: number) => {
    const options: SleepTimerOptions = {
      duration: minutes,
      fadeOut: fadeOutEnabled,
      showNotification: notificationEnabled
    };

    const success = await sleepTimerService.startTimer(options);
    if (success) {
      onClose();
      Alert.alert(
        'Sleep Timer Started',
        `Timer set for ${minutes} minutes. The radio will stop playing automatically.`,
        [{ text: 'OK' }]
      );
    } else {
      Alert.alert(
        'Error',
        'Failed to start sleep timer. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleCustomTimer = async () => {
    const minutes = parseInt(customMinutes);
    
    if (isNaN(minutes) || minutes <= 0 || minutes > 480) {
      Alert.alert(
        'Invalid Duration',
        'Please enter a valid duration between 1 and 480 minutes (8 hours).',
        [{ text: 'OK' }]
      );
      return;
    }

    await handlePresetSelect(minutes);
    setCustomMinutes('');
    setShowCustomInput(false);
  };

  const handleCancelTimer = async () => {
    Alert.alert(
      'Cancel Sleep Timer',
      'Are you sure you want to cancel the sleep timer?',
      [
        { text: 'No', style: 'cancel' },
        {
          text: 'Yes',
          style: 'destructive',
          onPress: async () => {
            await sleepTimerService.cancelTimer();
            Alert.alert('Timer Cancelled', 'Sleep timer has been cancelled.');
          }
        }
      ]
    );
  };

  const handleAddTime = async (minutes: number) => {
    const success = await sleepTimerService.addTime(minutes);
    if (success) {
      Alert.alert(
        'Time Added',
        `Added ${minutes} minutes to your sleep timer.`,
        [{ text: 'OK' }]
      );
    }
  };

  const formatTimeDisplay = () => {
    if (!timerState.isActive) return '00:00';
    return sleepTimerService.getFormattedTime();
  };

  const getProgressPercentage = () => {
    return sleepTimerService.getProgress();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#666" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Sleep Timer</Text>
          <View style={styles.headerSpacer} />
        </View>

        {/* Current Timer Status */}
        {timerState.isActive && (
          <View style={styles.activeTimerContainer}>
            <View style={styles.timerDisplay}>
              <Text style={styles.timerLabel}>Time Remaining</Text>
              <Text style={styles.timerTime}>{formatTimeDisplay()}</Text>
              
              {/* Progress Bar */}
              <View style={styles.progressBarContainer}>
                <View 
                  style={[
                    styles.progressBar, 
                    { width: `${getProgressPercentage()}%` }
                  ]} 
                />
              </View>
              
              <Text style={styles.originalDuration}>
                Original: {timerState.originalDuration} minutes
              </Text>
            </View>

            {/* Timer Controls */}
            <View style={styles.timerControls}>
              <TouchableOpacity
                style={styles.addTimeButton}
                onPress={() => handleAddTime(15)}
              >
                <Ionicons name="add-circle-outline" size={20} color="#007AFF" />
                <Text style={styles.addTimeText}>+15m</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.cancelButton}
                onPress={handleCancelTimer}
              >
                <Ionicons name="stop-circle" size={32} color="#FF3B30" />
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.addTimeButton}
                onPress={() => handleAddTime(30)}
              >
                <Ionicons name="add-circle-outline" size={20} color="#007AFF" />
                <Text style={styles.addTimeText}>+30m</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Timer Options (when no timer is active) */}
        {!timerState.isActive && (
          <>
            {/* Settings */}
            <View style={styles.settingsContainer}>
              <Text style={styles.settingsTitle}>Timer Settings</Text>
              
              <TouchableOpacity
                style={styles.settingRow}
                onPress={() => setFadeOutEnabled(!fadeOutEnabled)}
              >
                <View style={styles.settingInfo}>
                  <Text style={styles.settingLabel}>Fade Out</Text>
                  <Text style={styles.settingDescription}>
                    Gradually reduce volume before stopping
                  </Text>
                </View>
                <View style={[
                  styles.toggle,
                  fadeOutEnabled && styles.toggleActive
                ]}>
                  {fadeOutEnabled && (
                    <View style={styles.toggleIndicator} />
                  )}
                </View>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.settingRow}
                onPress={() => setNotificationEnabled(!notificationEnabled)}
              >
                <View style={styles.settingInfo}>
                  <Text style={styles.settingLabel}>Notifications</Text>
                  <Text style={styles.settingDescription}>
                    Alert when timer is about to end
                  </Text>
                </View>
                <View style={[
                  styles.toggle,
                  notificationEnabled && styles.toggleActive
                ]}>
                  {notificationEnabled && (
                    <View style={styles.toggleIndicator} />
                  )}
                </View>
              </TouchableOpacity>
            </View>

            {/* Preset Durations */}
            <View style={styles.presetsContainer}>
              <Text style={styles.presetsTitle}>Quick Select</Text>
              <View style={styles.presetGrid}>
                {sleepTimerService.presets.map((preset) => (
                  <TouchableOpacity
                    key={preset.value}
                    style={styles.presetButton}
                    onPress={() => handlePresetSelect(preset.value)}
                  >
                    <Ionicons name="time-outline" size={24} color="#007AFF" />
                    <Text style={styles.presetLabel}>{preset.label}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Custom Timer */}
            <View style={styles.customContainer}>
              <TouchableOpacity
                style={styles.customTrigger}
                onPress={() => setShowCustomInput(!showCustomInput)}
              >
                <Ionicons name="create-outline" size={20} color="#007AFF" />
                <Text style={styles.customTriggerText}>Custom Duration</Text>
                <Ionicons 
                  name={showCustomInput ? "chevron-up" : "chevron-down"} 
                  size={16} 
                  color="#666" 
                />
              </TouchableOpacity>

              {showCustomInput && (
                <View style={styles.customInputContainer}>
                  <TextInput
                    style={styles.customInput}
                    placeholder="Enter minutes (1-480)"
                    placeholderTextColor="#999"
                    value={customMinutes}
                    onChangeText={setCustomMinutes}
                    keyboardType="numeric"
                    maxLength={3}
                  />
                  <TouchableOpacity
                    style={styles.customSetButton}
                    onPress={handleCustomTimer}
                  >
                    <Text style={styles.customSetButtonText}>Set Timer</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          </>
        )}

        {/* Info Section */}
        <View style={styles.infoContainer}>
          <View style={styles.infoRow}>
            <Ionicons name="information-circle-outline" size={16} color="#666" />
            <Text style={styles.infoText}>
              Sleep timer will pause playback and can help save battery
            </Text>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="moon-outline" size={16} color="#666" />
            <Text style={styles.infoText}>
              Timer continues running even when the app is in background
            </Text>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  closeButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  headerSpacer: {
    width: 40,
  },
  
  // Active Timer Styles
  activeTimerContainer: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
  },
  timerDisplay: {
    alignItems: 'center',
    marginBottom: 20,
  },
  timerLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  timerTime: {
    fontSize: 48,
    fontWeight: '700',
    color: '#007AFF',
    fontVariant: ['tabular-nums'],
  },
  progressBarContainer: {
    width: 200,
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginVertical: 16,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  originalDuration: {
    fontSize: 14,
    color: '#666',
  },
  timerControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 30,
  },
  addTimeButton: {
    alignItems: 'center',
    padding: 8,
  },
  addTimeText: {
    fontSize: 12,
    color: '#007AFF',
    marginTop: 4,
  },
  cancelButton: {
    alignItems: 'center',
    padding: 8,
  },
  cancelButtonText: {
    fontSize: 12,
    color: '#FF3B30',
    marginTop: 4,
  },

  // Settings Styles
  settingsContainer: {
    margin: 16,
    marginBottom: 8,
  },
  settingsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
  },
  toggle: {
    width: 48,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#e0e0e0',
    justifyContent: 'center',
    paddingHorizontal: 2,
  },
  toggleActive: {
    backgroundColor: '#007AFF',
    alignItems: 'flex-end',
  },
  toggleIndicator: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#fff',
  },

  // Presets Styles
  presetsContainer: {
    margin: 16,
    marginVertical: 8,
  },
  presetsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  presetGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  presetButton: {
    width: '47%',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  presetLabel: {
    fontSize: 14,
    color: '#333',
    marginTop: 8,
    textAlign: 'center',
  },

  // Custom Timer Styles
  customContainer: {
    margin: 16,
    marginVertical: 8,
  },
  customTrigger: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    gap: 8,
  },
  customTriggerText: {
    flex: 1,
    fontSize: 16,
    color: '#007AFF',
  },
  customInputContainer: {
    flexDirection: 'row',
    marginTop: 8,
    gap: 8,
  },
  customInput: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  customSetButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 20,
    paddingVertical: 12,
    justifyContent: 'center',
  },
  customSetButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },

  // Info Styles
  infoContainer: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
    gap: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});

export default SleepTimerComponent;