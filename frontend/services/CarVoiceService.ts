import * as Speech from 'expo-speech';
import { Platform } from 'react-native';

export interface CarVoiceCommand {
  command: string;
  intent: 'play' | 'pause' | 'stop' | 'next' | 'previous' | 'volume' | 'station' | 'help';
  parameters?: {
    stationName?: string;
    volumeLevel?: number;
    genre?: string;
  };
}

export interface CarVoiceResponse {
  success: boolean;
  message: string;
  action?: string;
  data?: any;
}

export class CarVoiceService {
  private isListening = false;
  private listeners: Set<(command: CarVoiceCommand, response: CarVoiceResponse) => void> = new Set();

  // Car-specific voice commands patterns
  private commandPatterns = {
    play: [
      /^play$/i,
      /^start playing$/i,
      /^resume$/i,
      /^turn on$/i,
      /^start music$/i,
      /^play radio$/i
    ],
    pause: [
      /^pause$/i,
      /^stop$/i,
      /^turn off$/i,
      /^halt$/i,
      /^silence$/i
    ],
    next: [
      /^next$/i,
      /^next station$/i,
      /^change station$/i,
      /^skip$/i,
      /^forward$/i,
      /^switch$/i
    ],
    previous: [
      /^previous$/i,
      /^back$/i,
      /^last station$/i,
      /^go back$/i,
      /^return$/i
    ],
    volume: [
      /^volume up$/i,
      /^louder$/i,
      /^increase volume$/i,
      /^turn up$/i,
      /^volume down$/i,
      /^quieter$/i,
      /^decrease volume$/i,
      /^turn down$/i,
      /^mute$/i
    ],
    station: [
      /^tune to (.+)$/i,
      /^play (.+) station$/i,
      /^switch to (.+)$/i,
      /^find (.+)$/i,
      /^search for (.+)$/i,
      /^go to (.+)$/i
    ],
    help: [
      /^help$/i,
      /^what can you do$/i,
      /^commands$/i,
      /^voice commands$/i,
      /^assistance$/i
    ]
  };

  constructor() {
    this.initializeVoiceService();
  }

  private async initializeVoiceService() {
    try {
      // Configure speech synthesis for car announcements
      console.log('🎤 Car voice service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize car voice service:', error);
    }
  }

  // Process voice input and return car command
  async processVoiceInput(voiceText: string): Promise<CarVoiceResponse> {
    try {
      const command = this.parseVoiceCommand(voiceText.toLowerCase().trim());
      
      if (!command) {
        return {
          success: false,
          message: "Sorry, I didn't understand that command. Try 'play', 'pause', 'next station', or 'help'."
        };
      }

      const response = await this.executeCarCommand(command);
      
      // Notify listeners
      this.notifyListeners(command, response);
      
      return response;
    } catch (error) {
      console.error('❌ Voice processing error:', error);
      return {
        success: false,
        message: 'Voice command processing failed. Please try again.'
      };
    }
  }

  // Parse voice text into car command
  private parseVoiceCommand(voiceText: string): CarVoiceCommand | null {
    for (const [intent, patterns] of Object.entries(this.commandPatterns)) {
      for (const pattern of patterns) {
        const match = voiceText.match(pattern);
        if (match) {
          const command: CarVoiceCommand = {
            command: voiceText,
            intent: intent as any
          };

          // Extract parameters based on intent
          if (intent === 'station' && match[1]) {
            command.parameters = { stationName: match[1].trim() };
          } else if (intent === 'volume') {
            if (voiceText.includes('up') || voiceText.includes('louder') || voiceText.includes('increase')) {
              command.parameters = { volumeLevel: 1 }; // Increase
            } else if (voiceText.includes('down') || voiceText.includes('quieter') || voiceText.includes('decrease')) {
              command.parameters = { volumeLevel: -1 }; // Decrease
            } else if (voiceText.includes('mute')) {
              command.parameters = { volumeLevel: 0 }; // Mute
            }
          }

          return command;
        }
      }
    }

    return null;
  }

  // Execute car-specific command
  private async executeCarCommand(command: CarVoiceCommand): Promise<CarVoiceResponse> {
    switch (command.intent) {
      case 'play':
        await this.speakResponse('Playing radio');
        return {
          success: true,
          message: 'Playing radio',
          action: 'play'
        };

      case 'pause':
        await this.speakResponse('Paused');
        return {
          success: true,
          message: 'Paused',
          action: 'pause'
        };

      case 'next':
        await this.speakResponse('Next station');
        return {
          success: true,
          message: 'Switching to next station',
          action: 'next_station'
        };

      case 'previous':
        await this.speakResponse('Previous station');
        return {
          success: true,
          message: 'Switching to previous station',
          action: 'previous_station'
        };

      case 'volume':
        const volumeLevel = command.parameters?.volumeLevel;
        let volumeMessage = 'Volume adjusted';
        
        if (volumeLevel === 1) {
          volumeMessage = 'Volume up';
        } else if (volumeLevel === -1) {
          volumeMessage = 'Volume down';
        } else if (volumeLevel === 0) {
          volumeMessage = 'Muted';
        }
        
        await this.speakResponse(volumeMessage);
        return {
          success: true,
          message: volumeMessage,
          action: 'volume',
          data: { level: volumeLevel }
        };

      case 'station':
        const stationName = command.parameters?.stationName;
        await this.speakResponse(`Searching for ${stationName} station`);
        return {
          success: true,
          message: `Searching for ${stationName} station`,
          action: 'find_station',
          data: { stationName }
        };

      case 'help':
        const helpMessage = 'Available commands: play, pause, next station, previous station, volume up, volume down, tune to station name, or help';
        await this.speakResponse(helpMessage);
        return {
          success: true,
          message: helpMessage,
          action: 'help'
        };

      default:
        return {
          success: false,
          message: 'Command not recognized'
        };
    }
  }

  // Speak response for hands-free feedback
  private async speakResponse(message: string): Promise<void> {
    try {
      // Use faster speech rate for car environment
      await Speech.speak(message, {
        language: 'en',
        rate: 1.2, // Slightly faster for efficiency
        pitch: 1.0,
        volume: 1.0
      });
    } catch (error) {
      console.log('ℹ️ Speech synthesis not available:', error.message);
    }
  }

  // Get car-specific voice command suggestions
  getCarCommandSuggestions(): string[] {
    return [
      'Play radio',
      'Pause',
      'Next station',
      'Previous station',
      'Volume up',
      'Volume down',
      'Tune to jazz station',
      'Find classical music',
      'Help with commands'
    ];
  }

  // Check if device supports speech recognition
  isSpeechRecognitionAvailable(): boolean {
    // This would need platform-specific implementation
    return Platform.OS === 'ios' || Platform.OS === 'android';
  }

  // Add voice command listener
  addListener(callback: (command: CarVoiceCommand, response: CarVoiceResponse) => void): () => void {
    this.listeners.add(callback);
    
    return () => {
      this.listeners.delete(callback);
    };
  }

  // Notify listeners of voice commands
  private notifyListeners(command: CarVoiceCommand, response: CarVoiceResponse): void {
    this.listeners.forEach(callback => {
      try {
        callback(command, response);
      } catch (error) {
        console.error('❌ Voice listener error:', error);
      }
    });
  }

  // Start listening for voice commands
  async startListening(): Promise<void> {
    try {
      this.isListening = true;
      console.log('🎤 Car voice listening started');
      
      // This would integrate with expo-speech-recognition or similar
      // For now, we'll use the integration service
    } catch (error) {
      console.error('❌ Failed to start voice listening:', error);
      this.isListening = false;
    }
  }

  // Stop listening for voice commands
  async stopListening(): Promise<void> {
    try {
      this.isListening = false;
      console.log('🎤 Car voice listening stopped');
    } catch (error) {
      console.error('❌ Failed to stop voice listening:', error);
    }
  }

  // Get listening status
  isCurrentlyListening(): boolean {
    return this.isListening;
  }

  // Emergency voice commands (highest priority)
  handleEmergencyCommand(voiceText: string): CarVoiceResponse | null {
    const emergencyPatterns = [
      /^emergency$/i,
      /^help me$/i,
      /^call emergency$/i,
      /^accident$/i,
      /^crash$/i
    ];

    for (const pattern of emergencyPatterns) {
      if (pattern.test(voiceText)) {
        return {
          success: true,
          message: 'Emergency mode activated',
          action: 'emergency'
        };
      }
    }

    return null;
  }

  // Cleanup resources
  async cleanup(): Promise<void> {
    try {
      await this.stopListening();
      this.listeners.clear();
      console.log('🧹 Car voice service cleaned up');
    } catch (error) {
      console.error('❌ Voice service cleanup error:', error);
    }
  }
}

// Export singleton instance
export const carVoiceService = new CarVoiceService();