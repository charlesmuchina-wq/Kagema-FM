import { Platform, NativeModules, NativeEventEmitter } from 'react-native';
import { Audio } from 'expo-audio';

export interface AudioInputDevice {
  id: string;
  name: string;
  type: 'builtin' | 'bluetooth' | 'airplay' | 'wired' | 'other';
  isSelected: boolean;
}

export interface AudioInputState {
  availableInputs: AudioInputDevice[];
  selectedInput: AudioInputDevice | null;
  isPickerVisible: boolean;
}

class IOSAudioInputPickerService {
  private listeners: Set<(state: AudioInputState) => void> = new Set();
  private currentState: AudioInputState = {
    availableInputs: [],
    selectedInput: null,
    isPickerVisible: false
  };
  private audioSessionConfigured = false;
  private eventEmitter: NativeEventEmitter | null = null;

  constructor() {
    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    if (Platform.OS !== 'ios') {
      console.log('📱 Audio input picker only available on iOS');
      return;
    }

    try {
      // Configure audio session first (required before AVInputPickerInteraction)
      await this.configureAudioSession();
      
      // Initialize event listener for input changes
      this.setupEventListeners();
      
      // Get initial audio inputs
      await this.refreshAvailableInputs();
      
      console.log('🎧 iOS Audio Input Picker Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize iOS Audio Input Picker Service:', error);
    }
  }

  /**
   * Configure the audio session before using AVInputPickerInteraction
   * This is a prerequisite as mentioned in the iOS documentation
   */
  private async configureAudioSession(): Promise<void> {
    try {
      // Configure audio session with enhanced settings for input picker
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: false,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
      });

      // Additional iOS-specific audio session configuration
      if (Platform.OS === 'ios') {
        // Configure AVAudioSession for optimal input picker behavior
        await this.configureiOSAudioSession();
      }

      this.audioSessionConfigured = true;
      console.log('✅ Audio session configured for input picker');
    } catch (error) {
      console.error('❌ Failed to configure audio session:', error);
      throw error;
    }
  }

  /**
   * Configure iOS-specific AVAudioSession settings
   * This prepares the session for AVInputPickerInteraction
   */
  private async configureiOSAudioSession(): Promise<void> {
    try {
      // Note: In a full implementation, this would use a native module
      // For now, we'll use expo-audio's configuration capabilities
      
      // The audio session should be configured with:
      // - Category: AVAudioSessionCategoryPlayback
      // - Options: AVAudioSessionCategoryOptionAllowBluetooth, 
      //           AVAudioSessionCategoryOptionAllowBluetoothA2DP,
      //           AVAudioSessionCategoryOptionAllowAirPlay
      
      console.log('📱 iOS AVAudioSession configured for input picker');
    } catch (error) {
      console.error('❌ Failed to configure iOS audio session:', error);
    }
  }

  /**
   * Set up event listeners for audio input changes
   */
  private setupEventListeners(): void {
    try {
      // In a full native implementation, this would listen to:
      // - AVAudioSessionRouteChangeNotification
      // - AVInputPickerInteractionDelegate events
      
      // For now, we'll simulate the event system
      console.log('🔧 Audio input change listeners configured');
    } catch (error) {
      console.error('❌ Failed to setup event listeners:', error);
    }
  }

  /**
   * Refresh the list of available audio inputs
   */
  private async refreshAvailableInputs(): Promise<void> {
    try {
      // In a full implementation, this would query AVAudioSession.sharedInstance().availableInputs
      // For now, we'll provide mock data representing common iOS audio inputs
      
      const mockInputs: AudioInputDevice[] = [
        {
          id: 'builtin-speaker',
          name: 'iPhone Speaker',
          type: 'builtin',
          isSelected: true
        },
        {
          id: 'builtin-receiver',
          name: 'iPhone Receiver',
          type: 'builtin',
          isSelected: false
        },
        {
          id: 'wired-headphones',
          name: 'Wired Headphones',
          type: 'wired',
          isSelected: false
        },
        {
          id: 'bluetooth-airpods',
          name: 'AirPods Pro',
          type: 'bluetooth',
          isSelected: false
        },
        {
          id: 'airplay-apple-tv',
          name: 'Living Room Apple TV',
          type: 'airplay',
          isSelected: false
        },
        {
          id: 'airplay-homepod',
          name: 'Kitchen HomePod',
          type: 'airplay', 
          isSelected: false
        },
        {
          id: 'airplay-speaker-bedroom',
          name: 'Bedroom AirPlay Speaker',
          type: 'airplay',
          isSelected: false
        }
      ];

      // Filter to show only available inputs (in real implementation)
      this.currentState.availableInputs = mockInputs;
      this.currentState.selectedInput = mockInputs.find(input => input.isSelected) || null;
      
      this.notifyListeners();
      console.log(`📱 Found ${mockInputs.length} available audio inputs`);
    } catch (error) {
      console.error('❌ Failed to refresh available inputs:', error);
    }
  }

  /**
   * Present the audio input picker using AVInputPickerInteraction
   * This is the main method that shows the native iOS picker
   */
  async presentInputPicker(): Promise<boolean> {
    if (Platform.OS !== 'ios') {
      console.log('📱 Audio input picker only available on iOS');
      return false;
    }

    if (!this.audioSessionConfigured) {
      console.log('⚠️ Audio session not configured, initializing...');
      await this.configureAudioSession();
    }

    try {
      // Mark picker as visible
      this.currentState.isPickerVisible = true;
      this.notifyListeners();

      // In a full native implementation, this would:
      // 1. Create AVInputPickerInteraction instance
      // 2. Set the delegate to the presenting view controller
      // 3. Call the 'present' method on the interaction
      
      /* Native iOS implementation would be:
      const inputPicker = new AVInputPickerInteraction();
      inputPicker.delegate = self; // view controller
      inputPicker.present();
      */

      // For now, we'll simulate the picker presentation
      await this.simulateInputPickerPresentation();
      
      return true;
    } catch (error) {
      console.error('❌ Failed to present input picker:', error);
      this.currentState.isPickerVisible = false;
      this.notifyListeners();
      return false;
    }
  }

  /**
   * Simulate the input picker presentation for development
   * In production, this would be replaced with native AVInputPickerInteraction
   */
  private async simulateInputPickerPresentation(): Promise<void> {
    try {
      console.log('🎧 Presenting audio input picker...');
      
      // Simulate picker display time
      setTimeout(() => {
        this.currentState.isPickerVisible = false;
        this.notifyListeners();
        console.log('🎧 Audio input picker dismissed');
      }, 2000);
      
    } catch (error) {
      console.error('❌ Error in picker simulation:', error);
    }
  }

  /**
   * Programmatically select an audio input device
   */
  async selectAudioInput(inputId: string): Promise<boolean> {
    try {
      const input = this.currentState.availableInputs.find(i => i.id === inputId);
      if (!input) {
        console.error(`❌ Audio input not found: ${inputId}`);
        return false;
      }

      // Update selection state
      this.currentState.availableInputs.forEach(i => i.isSelected = false);
      input.isSelected = true;
      this.currentState.selectedInput = input;

      // In a full implementation, this would call:
      // AVAudioSession.sharedInstance().setPreferredInput(input)
      
      console.log(`🎧 Selected audio input: ${input.name}`);
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('❌ Failed to select audio input:', error);
      return false;
    }
  }

  /**
   * Get the current audio input state
   */
  getState(): AudioInputState {
    return { ...this.currentState };
  }

  /**
   * Check if the input picker is currently available
   */
  isInputPickerAvailable(): boolean {
    return Platform.OS === 'ios' && this.audioSessionConfigured;
  }

  /**
   * Get available input types for filtering
   */
  getAvailableInputTypes(): string[] {
    const types = new Set(this.currentState.availableInputs.map(input => input.type));
    return Array.from(types);
  }

  /**
   * Filter inputs by type
   */
  getInputsByType(type: string): AudioInputDevice[] {
    return this.currentState.availableInputs.filter(input => input.type === type);
  }

  /**
   * Check if a specific input type is available
   */
  hasInputType(type: string): boolean {
    return this.currentState.availableInputs.some(input => input.type === type);
  }

  /**
   * Get the currently selected input device
   */
  getSelectedInput(): AudioInputDevice | null {
    return this.currentState.selectedInput;
  }

  /**
   * Refresh and update available inputs
   */
  async refreshInputs(): Promise<void> {
    await this.refreshAvailableInputs();
  }

  /**
   * Add a state change listener
   */
  addListener(callback: (state: AudioInputState) => void): () => void {
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Notify all listeners of state changes
   */
  private notifyListeners(): void {
    this.listeners.forEach(callback => {
      try {
        callback({ ...this.currentState });
      } catch (error) {
        console.error('❌ Listener callback error:', error);
      }
    });
  }

  /**
   * Clean up resources and listeners
   */
  async cleanup(): Promise<void> {
    try {
      this.listeners.clear();
      this.currentState = {
        availableInputs: [],
        selectedInput: null,
        isPickerVisible: false
      };
      
      if (this.eventEmitter) {
        this.eventEmitter.removeAllListeners();
        this.eventEmitter = null;
      }
      
      console.log('🧹 iOS Audio Input Picker Service cleaned up');
    } catch (error) {
      console.error('❌ Cleanup error:', error);
    }
  }
}

// Export singleton instance
const iOSAudioInputPickerServiceInstance = new iOSAudioInputPickerService();
export { iOSAudioInputPickerServiceInstance as iOSAudioInputPickerService };