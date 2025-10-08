import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Platform,
  Slider,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Import advanced audio services
import { spatialAudioService, SpatialAudioPosition, SpatialEnvironment } from '../services/SpatialAudioService';
import { audioKitService, AudioProcessingChain, AudioAnalysis, EqualizerBand } from '../services/AudioKitService';
import { higAudioControlsService, HIGAudioControl, AccessibilityOptions, MediaSessionMetadata } from '../services/HIGAudioControlsService';

interface AdvancedAudioDashboardProps {
  onClose?: () => void;
  style?: any;
}

export const AdvancedAudioDashboard: React.FC<AdvancedAudioDashboardProps> = ({
  onClose,
  style
}) => {
  // Spatial Audio State
  const [listenerPosition, setListenerPosition] = useState<SpatialAudioPosition>({ x: 0, y: 0, z: 0 });
  const [activeEnvironment, setActiveEnvironment] = useState<string>('radio_studio');
  const [headTrackingEnabled, setHeadTrackingEnabled] = useState(true);
  const [spatialSources, setSpatialSources] = useState<any[]>([]);

  // AudioKit State
  const [activeProcessingChain, setActiveProcessingChain] = useState<AudioProcessingChain | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioAnalysis, setAudioAnalysis] = useState<AudioAnalysis | null>(null);
  const [equalizerBands, setEqualizerBands] = useState<EqualizerBand[]>([
    { frequency: 60, gain: 0, q: 1.0 },
    { frequency: 250, gain: 0, q: 1.0 },
    { frequency: 1000, gain: 0, q: 1.0 },
    { frequency: 4000, gain: 0, q: 1.0 },
    { frequency: 8000, gain: 0, q: 1.0 },
  ]);

  // HIG Controls State
  const [mediaSession, setMediaSession] = useState<MediaSessionMetadata | null>(null);
  const [accessibilityOptions, setAccessibilityOptions] = useState<AccessibilityOptions>({
    enableVoiceOver: false,
    enableReducedMotion: false,
    enableHighContrast: false,
    fontSize: 'medium',
    enableHapticFeedback: true
  });
  const [visibleControls, setVisibleControls] = useState<HIGAudioControl[]>([]);

  useEffect(() => {
    // Initialize services and load initial data
    initializeAdvancedAudio();

    // Subscribe to service events
    const unsubscribes = [
      spatialAudioService.addListener(handleSpatialAudioEvent),
      audioKitService.addListener(handleAudioKitEvent),
      higAudioControlsService.addListener(handleHIGControlsEvent)
    ];

    return () => {
      unsubscribes.forEach(unsub => unsub());
    };
  }, []);

  const initializeAdvancedAudio = async () => {
    try {
      // Load initial states
      const spatialCapabilities = spatialAudioService.getCapabilities();
      const processingChain = audioKitService.getCurrentProcessingChain();
      const controls = higAudioControlsService.getVisibleControls();
      const accessibility = higAudioControlsService.getAccessibilityOptions();

      setActiveProcessingChain(processingChain);
      setVisibleControls(controls);
      setAccessibilityOptions(accessibility);

      console.log('🎧 Advanced audio dashboard initialized');
      console.log('📱 Device capabilities:', spatialCapabilities);
    } catch (error) {
      console.error('❌ Failed to initialize advanced audio dashboard:', error);
    }
  };

  const handleSpatialAudioEvent = (event: any) => {
    console.log('🎯 Spatial audio event:', event.type);
    
    if (event.type === 'listenerPositionChanged') {
      setListenerPosition(event.position);
    }
  };

  const handleAudioKitEvent = (event: any) => {
    console.log('🎛️ AudioKit event:', event.type);
    
    if (event.type === 'processingChainChanged') {
      setActiveProcessingChain(event.chain);
    }
  };

  const handleHIGControlsEvent = (event: any) => {
    console.log('🎮 HIG Controls event:', event.type);
    
    if (event.type === 'mediaSessionUpdated') {
      setMediaSession(event.metadata);
    } else if (event.type === 'accessibilityOptionsChanged') {
      setAccessibilityOptions(event.options);
    }
  };

  // Spatial Audio Handlers
  const handleCreateSpatialSource = async () => {
    const success = await spatialAudioService.createSpatialAudioSource({
      id: `source_${Date.now()}`,
      name: 'Radio Station',
      audioUrl: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one',
      position: { x: Math.random() * 2 - 1, y: 0, z: Math.random() * 2 - 1 },
      sourceType: 'point'
    });

    if (success) {
      setSpatialSources(spatialAudioService.getActiveSources());
      await higAudioControlsService.playUISound('success_chime');
      Alert.alert('Spatial Audio', 'Created 3D positioned radio source!');
    }
  };

  const handleUpdateListenerPosition = (axis: 'x' | 'y' | 'z', value: number) => {
    const newPosition = { ...listenerPosition, [axis]: value };
    setListenerPosition(newPosition);
    spatialAudioService.updateListenerPosition(newPosition);
  };

  const handleSetEnvironment = async (environmentId: string) => {
    const success = await spatialAudioService.setEnvironment(environmentId);
    if (success) {
      setActiveEnvironment(environmentId);
      await higAudioControlsService.playUISound('navigation_swoosh');
    }
  };

  const handleToggleHeadTracking = async () => {
    const newValue = !headTrackingEnabled;
    const success = await spatialAudioService.setHeadTracking(newValue);
    if (success) {
      setHeadTrackingEnabled(newValue);
    }
  };

  // AudioKit Handlers
  const handleSetProcessingChain = async (chainId: string) => {
    const presets = audioKitService.getEffectPresets();
    const preset = presets.find(p => p.id === chainId);
    
    if (preset) {
      const success = await audioKitService.setProcessingChain(preset);
      if (success) {
        await higAudioControlsService.playUISound('button_tap');
        Alert.alert('AudioKit', `Applied ${preset.name} processing chain`);
      }
    }
  };

  const handleToggleRecording = async () => {
    if (isRecording) {
      const recordingUri = await audioKitService.stopRecording();
      if (recordingUri) {
        setIsRecording(false);
        await higAudioControlsService.playUISound('success_chime');
        Alert.alert('Recording Complete', `Saved to: ${recordingUri}`);
      }
    } else {
      const success = await audioKitService.startRecording({
        sampleRate: 44100,
        bitDepth: 16,
        channels: 2,
        format: 'wav',
        quality: 'high'
      });
      
      if (success) {
        setIsRecording(true);
        await higAudioControlsService.playUISound('button_tap');
      }
    }
  };

  const handleStartAudioAnalysis = async () => {
    const success = await audioKitService.startAudioAnalysis((analysis) => {
      setAudioAnalysis(analysis);
    });

    if (success) {
      await higAudioControlsService.playUISound('navigation_swoosh');
      Alert.alert('Audio Analysis', 'Real-time audio analysis started!');
    }
  };

  const handleEqualizerChange = async (index: number, gain: number) => {
    const newBands = [...equalizerBands];
    newBands[index].gain = gain;
    setEqualizerBands(newBands);
    
    await audioKitService.setEqualizer(newBands);
  };

  // HIG Controls Handlers
  const handleUpdateMediaSession = async () => {
    const metadata: MediaSessionMetadata = {
      title: 'BBC Radio 1',
      artist: 'BBC',
      album: 'Live Radio',
      artwork: 'https://example.com/artwork.jpg',
      duration: 0, // Live stream
      position: 0,
      playbackRate: 1.0,
      playbackState: 'playing'
    };

    const success = await higAudioControlsService.updateMediaSession(metadata);
    if (success) {
      await higAudioControlsService.playUISound('success_chime');
    }
  };

  const handleAccessibilityToggle = async (option: keyof AccessibilityOptions) => {
    const newOptions = {
      ...accessibilityOptions,
      [option]: !accessibilityOptions[option]
    };
    
    const success = await higAudioControlsService.setAccessibilityOptions(newOptions);
    if (success) {
      await higAudioControlsService.playUISound('button_tap');
    }
  };

  return (
    <View style={[styles.container, style]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Advanced Audio Features</Text>
        {onClose && (
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#666" />
          </TouchableOpacity>
        )}
      </View>

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        
        {/* Spatial Audio Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="globe-outline" size={20} color="#007AFF" />
            <Text style={styles.sectionTitle}>Spatial Audio & PHASE</Text>
          </View>
          
          <View style={styles.card}>
            <Text style={styles.cardTitle}>3D Audio Environment</Text>
            <View style={styles.environmentSelector}>
              {spatialAudioService.spatialEnvironments.map((env) => (
                <TouchableOpacity
                  key={env.id}
                  style={[
                    styles.environmentButton,
                    activeEnvironment === env.id && styles.environmentButtonActive
                  ]}
                  onPress={() => handleSetEnvironment(env.id)}
                >
                  <Text style={[
                    styles.environmentText,
                    activeEnvironment === env.id && styles.environmentTextActive
                  ]}>
                    {env.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Listener Position</Text>
            <View style={styles.positionControls}>
              {(['x', 'y', 'z'] as const).map((axis) => (
                <View key={axis} style={styles.positionSlider}>
                  <Text style={styles.sliderLabel}>{axis.toUpperCase()}: {listenerPosition[axis].toFixed(2)}</Text>
                  <Slider
                    style={styles.slider}
                    value={listenerPosition[axis]}
                    minimumValue={-2}
                    maximumValue={2}
                    onValueChange={(value) => handleUpdateListenerPosition(axis, value)}
                    minimumTrackTintColor="#007AFF"
                    maximumTrackTintColor="#E0E0E0"
                    thumbStyle={styles.sliderThumb}
                  />
                </View>
              ))}
            </View>
          </View>

          <View style={styles.actionRow}>
            <TouchableOpacity style={styles.actionButton} onPress={handleCreateSpatialSource}>
              <Text style={styles.actionButtonText}>Create 3D Source</Text>
            </TouchableOpacity>
            
            <View style={styles.toggleContainer}>
              <Text style={styles.toggleLabel}>Head Tracking</Text>
              <Switch
                value={headTrackingEnabled}
                onValueChange={handleToggleHeadTracking}
                trackColor={{ false: '#E0E0E0', true: '#007AFF' }}
              />
            </View>
          </View>
        </View>

        {/* AudioKit Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="options-outline" size={20} color="#007AFF" />
            <Text style={styles.sectionTitle}>AudioKit Processing</Text>
          </View>
          
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Processing Presets</Text>
            <View style={styles.presetSelector}>
              {audioKitService.getEffectPresets().map((preset) => (
                <TouchableOpacity
                  key={preset.id}
                  style={[
                    styles.presetButton,
                    activeProcessingChain?.id === preset.id && styles.presetButtonActive
                  ]}
                  onPress={() => handleSetProcessingChain(preset.id)}
                >
                  <Text style={[
                    styles.presetText,
                    activeProcessingChain?.id === preset.id && styles.presetTextActive
                  ]}>
                    {preset.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Equalizer</Text>
            <View style={styles.equalizerContainer}>
              {equalizerBands.map((band, index) => (
                <View key={band.frequency} style={styles.eqBand}>
                  <Text style={styles.eqFreq}>{band.frequency}Hz</Text>
                  <Slider
                    style={styles.eqSlider}
                    value={band.gain}
                    minimumValue={-12}
                    maximumValue={12}
                    onValueChange={(gain) => handleEqualizerChange(index, gain)}
                    minimumTrackTintColor="#007AFF"
                    maximumTrackTintColor="#E0E0E0"
                    vertical={true}
                  />
                  <Text style={styles.eqGain}>{band.gain.toFixed(1)}dB</Text>
                </View>
              ))}
            </View>
          </View>

          <View style={styles.actionRow}>
            <TouchableOpacity 
              style={[styles.actionButton, isRecording && styles.recordingButton]} 
              onPress={handleToggleRecording}
            >
              <Text style={[styles.actionButtonText, isRecording && styles.recordingText]}>
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionButton} onPress={handleStartAudioAnalysis}>
              <Text style={styles.actionButtonText}>Analyze Audio</Text>
            </TouchableOpacity>
          </View>

          {audioAnalysis && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Real-time Analysis</Text>
              <View style={styles.analysisGrid}>
                <View style={styles.analysisItem}>
                  <Text style={styles.analysisLabel}>RMS</Text>
                  <Text style={styles.analysisValue}>{audioAnalysis.rms.toFixed(3)}</Text>
                </View>
                <View style={styles.analysisItem}>
                  <Text style={styles.analysisLabel}>Peak</Text>
                  <Text style={styles.analysisValue}>{audioAnalysis.peak.toFixed(3)}</Text>
                </View>
                <View style={styles.analysisItem}>
                  <Text style={styles.analysisLabel}>Tempo</Text>
                  <Text style={styles.analysisValue}>{audioAnalysis.tempo.toFixed(0)} BPM</Text>
                </View>
                <View style={styles.analysisItem}>
                  <Text style={styles.analysisLabel}>Pitch</Text>
                  <Text style={styles.analysisValue}>{audioAnalysis.pitch.toFixed(0)} Hz</Text>
                </View>
              </View>
            </View>
          )}
        </View>

        {/* HIG Compliance Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="accessibility-outline" size={20} color="#007AFF" />
            <Text style={styles.sectionTitle}>HIG Compliance & Accessibility</Text>
          </View>
          
          <View style={styles.card}>
            <Text style={styles.cardTitle}>System Integration</Text>
            <TouchableOpacity style={styles.systemButton} onPress={handleUpdateMediaSession}>
              <Ionicons name="phone-portrait-outline" size={16} color="#007AFF" />
              <Text style={styles.systemButtonText}>Update Lock Screen Controls</Text>
            </TouchableOpacity>
            
            {mediaSession && (
              <View style={styles.mediaInfo}>
                <Text style={styles.mediaTitle}>{mediaSession.title}</Text>
                <Text style={styles.mediaArtist}>{mediaSession.artist}</Text>
                <Text style={styles.mediaState}>State: {mediaSession.playbackState}</Text>
              </View>
            )}
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Accessibility Options</Text>
            <View style={styles.accessibilityOptions}>
              <View style={styles.accessibilityOption}>
                <Text style={styles.accessibilityLabel}>VoiceOver Support</Text>
                <Switch
                  value={accessibilityOptions.enableVoiceOver}
                  onValueChange={() => handleAccessibilityToggle('enableVoiceOver')}
                />
              </View>
              <View style={styles.accessibilityOption}>
                <Text style={styles.accessibilityLabel}>Reduced Motion</Text>
                <Switch
                  value={accessibilityOptions.enableReducedMotion}
                  onValueChange={() => handleAccessibilityToggle('enableReducedMotion')}
                />
              </View>
              <View style={styles.accessibilityOption}>
                <Text style={styles.accessibilityLabel}>Haptic Feedback</Text>
                <Switch
                  value={accessibilityOptions.enableHapticFeedback}
                  onValueChange={() => handleAccessibilityToggle('enableHapticFeedback')}
                />
              </View>
            </View>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>UI Feedback Sounds</Text>
            <View style={styles.soundButtons}>
              {higAudioControlsService.systemUISounds.map((sound) => (
                <TouchableOpacity
                  key={sound.id}
                  style={styles.soundButton}
                  onPress={() => higAudioControlsService.playUISound(sound.id)}
                >
                  <Text style={styles.soundButtonText}>{sound.name}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

      </ScrollView>
    </View>
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
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  closeButton: {
    padding: 8,
  },
  scrollContainer: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 8,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  
  // Spatial Audio Styles
  environmentSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  environmentButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
  },
  environmentButtonActive: {
    backgroundColor: '#007AFF',
  },
  environmentText: {
    fontSize: 12,
    color: '#666',
  },
  environmentTextActive: {
    color: '#fff',
  },
  positionControls: {
    gap: 8,
  },
  positionSlider: {
    gap: 4,
  },
  sliderLabel: {
    fontSize: 12,
    color: '#666',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  slider: {
    width: '100%',
    height: 20,
  },
  sliderThumb: {
    backgroundColor: '#007AFF',
  },
  
  // AudioKit Styles
  presetSelector: {
    gap: 8,
  },
  presetButton: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  presetButtonActive: {
    backgroundColor: '#007AFF',
  },
  presetText: {
    fontSize: 14,
    color: '#666',
  },
  presetTextActive: {
    color: '#fff',
  },
  equalizerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    height: 120,
  },
  eqBand: {
    alignItems: 'center',
    gap: 4,
  },
  eqFreq: {
    fontSize: 10,
    color: '#666',
  },
  eqSlider: {
    width: 20,
    height: 80,
  },
  eqGain: {
    fontSize: 10,
    color: '#666',
  },
  analysisGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  analysisItem: {
    flex: 1,
    minWidth: '45%',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
  },
  analysisLabel: {
    fontSize: 12,
    color: '#666',
  },
  analysisValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#007AFF',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  
  // HIG Styles
  systemButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    gap: 8,
  },
  systemButtonText: {
    fontSize: 14,
    color: '#007AFF',
  },
  mediaInfo: {
    marginTop: 12,
    padding: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
  },
  mediaTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  mediaArtist: {
    fontSize: 12,
    color: '#666',
  },
  mediaState: {
    fontSize: 12,
    color: '#007AFF',
  },
  accessibilityOptions: {
    gap: 12,
  },
  accessibilityOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  accessibilityLabel: {
    fontSize: 14,
    color: '#333',
  },
  soundButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  soundButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
  },
  soundButtonText: {
    fontSize: 12,
    color: '#666',
  },
  
  // Action Styles
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  recordingButton: {
    backgroundColor: '#FF3B30',
  },
  recordingText: {
    color: '#fff',
  },
  toggleContainer: {
    alignItems: 'center',
    gap: 4,
  },
  toggleLabel: {
    fontSize: 12,
    color: '#666',
  },
});

export default AdvancedAudioDashboard;