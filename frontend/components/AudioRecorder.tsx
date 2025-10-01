import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Modal,
  ActivityIndicator,
  Dimensions,
  Animated,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import * as Haptics from 'expo-haptics';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Audio recording will be platform-specific
let Audio: any;
try {
  Audio = require('expo-av').Audio;
} catch (error) {
  console.log('Audio recording not available on this platform');
}

const { width } = Dimensions.get('window');

interface Recording {
  id: string;
  title: string;
  duration: number;
  fileUri: string;
  dateCreated: string;
  size: number;
  quality: 'high' | 'medium' | 'low';
  transcript?: string;
}

interface AudioRecorderProps {
  visible: boolean;
  onClose: () => void;
  onRecordingComplete?: (recording: Recording) => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  visible,
  onClose,
  onRecordingComplete,
}) => {
  const { colors, isDark } = useTheme();
  
  // Recording state
  const [recording, setRecording] = useState<any>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordingLevel, setRecordingLevel] = useState(0);
  
  // Playback state
  const [sound, setSound] = useState<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackPosition, setPlaybackPosition] = useState(0);
  const [playbackDuration, setPlaybackDuration] = useState(0);
  
  // UI state
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [quality, setQuality] = useState<'high' | 'medium' | 'low'>('medium');
  const [isTranscribing, setIsTranscribing] = useState(false);
  
  // Animations
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const levelAnim = useRef(new Animated.Value(0)).current;
  
  // Refs
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadRecordings();
    return () => {
      cleanup();
    };
  }, []);

  useEffect(() => {
    if (isRecording) {
      startPulseAnimation();
      startLevelAnimation();
    } else {
      stopAnimations();
    }
  }, [isRecording]);

  const loadRecordings = async () => {
    try {
      const stored = await AsyncStorage.getItem('audio_recordings');
      if (stored) {
        setRecordings(JSON.parse(stored));
      }
    } catch (error) {
      console.log('Error loading recordings:', error);
    }
  };

  const saveRecordings = async (newRecordings: Recording[]) => {
    try {
      await AsyncStorage.setItem('audio_recordings', JSON.stringify(newRecordings));
      setRecordings(newRecordings);
    } catch (error) {
      console.log('Error saving recordings:', error);
    }
  };

  const cleanup = async () => {
    if (recording) {
      await recording.stopAndUnloadAsync();
    }
    if (sound) {
      await sound.unloadAsync();
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
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

  const startLevelAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(levelAnim, {
          toValue: Math.random(),
          duration: 100,
          useNativeDriver: false,
        }),
      ])
    ).start();
  };

  const stopAnimations = () => {
    pulseAnim.stopAnimation();
    levelAnim.stopAnimation();
  };

  const getRecordingOptions = () => {
    const baseOptions = {
      android: {
        extension: '.m4a',
        outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
        audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
        sampleRate: 44100,
        numberOfChannels: 2,
        bitRate: 128000,
      },
      ios: {
        extension: '.m4a',
        audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
        sampleRate: 44100,
        numberOfChannels: 2,
        bitRate: 128000,
        linearPCMBitDepth: 16,
        linearPCMIsBigEndian: false,
        linearPCMIsFloat: false,
      },
      web: {
        mimeType: 'audio/webm;codecs=opus',
        bitsPerSecond: 128000,
      },
    };

    // Adjust quality based on setting
    switch (quality) {
      case 'high':
        if (baseOptions.android) baseOptions.android.bitRate = 256000;
        if (baseOptions.ios) baseOptions.ios.bitRate = 256000;
        if (baseOptions.web) baseOptions.web.bitsPerSecond = 256000;
        break;
      case 'low':
        if (baseOptions.android) baseOptions.android.bitRate = 64000;
        if (baseOptions.ios) baseOptions.ios.bitRate = 64000;
        if (baseOptions.web) baseOptions.web.bitsPerSecond = 64000;
        break;
      default: // medium
        break;
    }

    return baseOptions;
  };

  const startRecording = async () => {
    try {
      if (!Audio) {
        Alert.alert('Not Available', 'Audio recording is not available on this platform');
        return;
      }

      // Request permissions
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Microphone permission is required for recording');
        return;
      }

      // Configure audio session
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recordingOptions = getRecordingOptions();
      
      const { recording: newRecording } = await Audio.Recording.createAsync(recordingOptions);
      
      setRecording(newRecording);
      setIsRecording(true);
      setRecordingDuration(0);

      // Update duration every second
      intervalRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);

      // Monitor recording levels (if available)
      newRecording.setOnRecordingStatusUpdate((status) => {
        if (status.isRecording) {
          setRecordingLevel(status.metering || 0);
        }
      });

      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      console.log('🎙️ Recording started');
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Recording Error', 'Failed to start recording. Please try again.');
    }
  };

  const pauseRecording = async () => {
    if (recording) {
      try {
        if (isPaused) {
          await recording.startAsync();
          setIsPaused(false);
        } else {
          await recording.pauseAsync();
          setIsPaused(true);
        }
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } catch (error) {
        console.error('Failed to pause/resume recording:', error);
      }
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      setIsRecording(false);
      setIsPaused(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }

      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      
      if (uri) {
        // Get file info
        const info = await recording.getStatusAsync();
        
        const newRecording: Recording = {
          id: Date.now().toString(),
          title: `Recording ${new Date().toLocaleTimeString()}`,
          duration: recordingDuration,
          fileUri: uri,
          dateCreated: new Date().toISOString(),
          size: info.durationMillis || 0,
          quality: quality,
        };

        const updatedRecordings = [newRecording, ...recordings];
        await saveRecordings(updatedRecordings);
        
        setSelectedRecording(newRecording);
        onRecordingComplete?.(newRecording);
        
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        
        Alert.alert(
          'Recording Complete',
          `Recording saved successfully! Duration: ${formatDuration(recordingDuration)}`,
          [
            { text: 'OK' },
            { text: 'Play', onPress: () => playRecording(newRecording) }
          ]
        );
      }

      setRecording(null);
      setRecordingDuration(0);
      setRecordingLevel(0);
      
    } catch (error) {
      console.error('Failed to stop recording:', error);
      Alert.alert('Error', 'Failed to save recording');
    }
  };

  const playRecording = async (recordingItem: Recording) => {
    try {
      // Stop current playback if any
      if (sound) {
        await sound.unloadAsync();
        setSound(null);
      }

      if (isPlaying && selectedRecording?.id === recordingItem.id) {
        setIsPlaying(false);
        return;
      }

      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: recordingItem.fileUri },
        { shouldPlay: true }
      );

      newSound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded) {
          setIsPlaying(status.isPlaying || false);
          setPlaybackPosition(status.positionMillis || 0);
          setPlaybackDuration(status.durationMillis || 0);
          
          if (status.didJustFinish) {
            setIsPlaying(false);
            setPlaybackPosition(0);
          }
        }
      });

      setSound(newSound);
      setSelectedRecording(recordingItem);
      setIsPlaying(true);
      
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      
    } catch (error) {
      console.error('Failed to play recording:', error);
      Alert.alert('Playback Error', 'Failed to play recording');
    }
  };

  const deleteRecording = async (recordingItem: Recording) => {
    Alert.alert(
      'Delete Recording',
      'Are you sure you want to delete this recording? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            const updatedRecordings = recordings.filter(r => r.id !== recordingItem.id);
            await saveRecordings(updatedRecordings);
            
            if (selectedRecording?.id === recordingItem.id) {
              setSelectedRecording(null);
              if (sound) {
                await sound.unloadAsync();
                setSound(null);
              }
            }
            
            await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          }
        }
      ]
    );
  };

  const transcribeRecording = async (recordingItem: Recording) => {
    if (!recordingItem.fileUri) return;

    setIsTranscribing(true);
    
    try {
      // In a real app, you would send the audio file to a transcription service
      // For now, we'll simulate the process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const mockTranscript = `This is a simulated transcript for the recording "${recordingItem.title}". In a real application, this would be generated by a speech-to-text service like Google Speech-to-Text, AWS Transcribe, or Azure Speech Services.`;
      
      const updatedRecordings = recordings.map(r => 
        r.id === recordingItem.id 
          ? { ...r, transcript: mockTranscript }
          : r
      );
      
      await saveRecordings(updatedRecordings);
      
      if (selectedRecording?.id === recordingItem.id) {
        setSelectedRecording({ ...recordingItem, transcript: mockTranscript });
      }
      
      Alert.alert('Transcript Ready', 'Speech-to-text conversion completed!');
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
    } catch (error) {
      console.error('Transcription error:', error);
      Alert.alert('Transcription Failed', 'Unable to transcribe recording. Please try again.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const styles = StyleSheet.create({
    modalOverlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.5)',
      justifyContent: 'center',
    },
    container: {
      backgroundColor: colors.background,
      margin: 20,
      borderRadius: 20,
      padding: 20,
      maxHeight: '80%',
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 20,
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
    },
    closeButton: {
      padding: 8,
    },
    recordingControls: {
      alignItems: 'center',
      marginVertical: 20,
    },
    recordButton: {
      width: 80,
      height: 80,
      borderRadius: 40,
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: 16,
    },
    recordButtonRecording: {
      backgroundColor: colors.error,
    },
    recordButtonIdle: {
      backgroundColor: colors.primary,
    },
    controlButtons: {
      flexDirection: 'row',
      justifyContent: 'center',
      gap: 20,
    },
    controlButton: {
      width: 50,
      height: 50,
      borderRadius: 25,
      backgroundColor: colors.surface,
      alignItems: 'center',
      justifyContent: 'center',
    },
    duration: {
      fontSize: 18,
      fontWeight: '500',
      color: colors.text,
      marginBottom: 8,
    },
    levelMeter: {
      width: width - 80,
      height: 4,
      backgroundColor: colors.border,
      borderRadius: 2,
      overflow: 'hidden',
      marginBottom: 16,
    },
    levelBar: {
      height: '100%',
      backgroundColor: colors.primary,
      borderRadius: 2,
    },
    qualitySelector: {
      flexDirection: 'row',
      justifyContent: 'center',
      marginBottom: 20,
    },
    qualityButton: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 16,
      marginHorizontal: 4,
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    qualityButtonActive: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    },
    qualityText: {
      fontSize: 14,
      color: colors.text,
    },
    qualityTextActive: {
      color: colors.background,
    },
    recordingsList: {
      maxHeight: 300,
    },
    recordingItem: {
      backgroundColor: colors.surface,
      borderRadius: 12,
      padding: 16,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: colors.border,
    },
    recordingItemActive: {
      borderColor: colors.primary,
      backgroundColor: colors.card,
    },
    recordingHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 8,
    },
    recordingTitle: {
      fontSize: 16,
      fontWeight: '500',
      color: colors.text,
      flex: 1,
    },
    recordingActions: {
      flexDirection: 'row',
      gap: 12,
    },
    recordingInfo: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 8,
    },
    recordingDetail: {
      fontSize: 12,
      color: colors.textSecondary,
    },
    playbackControls: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    playButton: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    progressContainer: {
      flex: 1,
      marginHorizontal: 12,
      alignItems: 'center',
    },
    progressText: {
      fontSize: 12,
      color: colors.textSecondary,
    },
    transcript: {
      marginTop: 8,
      padding: 12,
      backgroundColor: colors.background,
      borderRadius: 8,
      borderWidth: 1,
      borderColor: colors.border,
    },
    transcriptText: {
      fontSize: 14,
      color: colors.text,
      lineHeight: 20,
    },
    emptyState: {
      alignItems: 'center',
      padding: 40,
    },
    emptyStateText: {
      fontSize: 16,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 16,
    },
  });

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>Audio Recorder</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>

          <View style={styles.recordingControls}>
            <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
              <TouchableOpacity
                style={[
                  styles.recordButton,
                  isRecording ? styles.recordButtonRecording : styles.recordButtonIdle,
                ]}
                onPress={isRecording ? stopRecording : startRecording}
                disabled={!Audio}
              >
                {isRecording ? (
                  <Ionicons name="stop" size={32} color="#fff" />
                ) : (
                  <Ionicons name="mic" size={32} color="#fff" />
                )}
              </TouchableOpacity>
            </Animated.View>

            {isRecording && (
              <View style={styles.controlButtons}>
                <TouchableOpacity style={styles.controlButton} onPress={pauseRecording}>
                  <Ionicons
                    name={isPaused ? 'play' : 'pause'}
                    size={20}
                    color={colors.text}
                  />
                </TouchableOpacity>
              </View>
            )}

            <Text style={styles.duration}>
              {formatDuration(recordingDuration)}
            </Text>

            {isRecording && (
              <View style={styles.levelMeter}>
                <Animated.View
                  style={[
                    styles.levelBar,
                    {
                      width: levelAnim.interpolate({
                        inputRange: [0, 1],
                        outputRange: ['0%', '100%'],
                      }),
                    },
                  ]}
                />
              </View>
            )}
          </View>

          <View style={styles.qualitySelector}>
            {['low', 'medium', 'high'].map((q) => (
              <TouchableOpacity
                key={q}
                style={[
                  styles.qualityButton,
                  quality === q && styles.qualityButtonActive,
                ]}
                onPress={() => setQuality(q as any)}
                disabled={isRecording}
              >
                <Text
                  style={[
                    styles.qualityText,
                    quality === q && styles.qualityTextActive,
                  ]}
                >
                  {q.toUpperCase()}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.recordingsList}>
            {recordings.length === 0 ? (
              <View style={styles.emptyState}>
                <Ionicons name="mic-outline" size={48} color={colors.textSecondary} />
                <Text style={styles.emptyStateText}>
                  No recordings yet.{'\n'}Tap the microphone to start recording.
                </Text>
              </View>
            ) : (
              recordings.map((item) => (
                <View
                  key={item.id}
                  style={[
                    styles.recordingItem,
                    selectedRecording?.id === item.id && styles.recordingItemActive,
                  ]}
                >
                  <View style={styles.recordingHeader}>
                    <Text style={styles.recordingTitle}>{item.title}</Text>
                    <View style={styles.recordingActions}>
                      <TouchableOpacity
                        onPress={() => transcribeRecording(item)}
                        disabled={isTranscribing}
                      >
                        {isTranscribing && selectedRecording?.id === item.id ? (
                          <ActivityIndicator size="small" color={colors.primary} />
                        ) : (
                          <Ionicons name="document-text" size={20} color={colors.text} />
                        )}
                      </TouchableOpacity>
                      <TouchableOpacity onPress={() => deleteRecording(item)}>
                        <Ionicons name="trash" size={20} color={colors.error} />
                      </TouchableOpacity>
                    </View>
                  </View>

                  <View style={styles.recordingInfo}>
                    <Text style={styles.recordingDetail}>
                      {formatDuration(item.duration)}
                    </Text>
                    <Text style={styles.recordingDetail}>
                      {new Date(item.dateCreated).toLocaleDateString()}
                    </Text>
                    <Text style={styles.recordingDetail}>
                      {item.quality.toUpperCase()}
                    </Text>
                  </View>

                  <View style={styles.playbackControls}>
                    <TouchableOpacity
                      style={styles.playButton}
                      onPress={() => playRecording(item)}
                    >
                      <Ionicons
                        name={
                          isPlaying && selectedRecording?.id === item.id
                            ? 'pause'
                            : 'play'
                        }
                        size={20}
                        color="#fff"
                      />
                    </TouchableOpacity>

                    {selectedRecording?.id === item.id && playbackDuration > 0 && (
                      <View style={styles.progressContainer}>
                        <Text style={styles.progressText}>
                          {formatDuration(Math.floor(playbackPosition / 1000))} /{' '}
                          {formatDuration(Math.floor(playbackDuration / 1000))}
                        </Text>
                      </View>
                    )}
                  </View>

                  {item.transcript && (
                    <View style={styles.transcript}>
                      <Text style={styles.transcriptText}>{item.transcript}</Text>
                    </View>
                  )}
                </View>
              ))
            )}
          </View>
        </View>
      </View>
    </Modal>
  );
};