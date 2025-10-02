// Voice Control Service for AI Assistant Integration
// Supports Alexa, Siri, Google Assistant style commands with speech recognition

interface VoiceCommand {
  intent: string;
  parameters: Record<string, any>;
  confidence: number;
  originalText: string;
}

interface VoiceResponse {
  success: boolean;
  message: string;
  action?: string;
  data?: any;
}

interface SpeechRecognition {
  start(): Promise<void>;
  stop(): Promise<void>;
  onResult(callback: (result: string) => void): void;
  onError(callback: (error: Error) => void): void;
}

class VoiceControlService {
  private isListening = false;
  private speechRecognition: SpeechRecognition | null = null;
  private commandCallbacks: ((command: VoiceCommand) => void)[] = [];
  private responseCallbacks: ((response: VoiceResponse) => void)[] = [];
  private emergentApiKey = 'sk-emergent-e19D7A22f3f2b9f8a0';
  private backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';

  private commandPatterns = {
    // Radio control commands
    play: [
      /^(play|start|begin|resume)( radio| music| the radio| the music)?$/i,
      /^(turn on|switch on)( the radio| radio)?$/i
    ],
    pause: [
      /^(pause|stop|halt)( radio| music| the radio| the music)?$/i,
      /^(turn off|switch off)( the radio| radio)?$/i
    ],
    next: [
      /^(next|skip|forward|change)( station| track| song)?$/i,
      /^(go to|switch to|tune to) next( station| track)?$/i
    ],
    previous: [
      /^(previous|back|last|go back)( station| track| song)?$/i,
      /^(go to|switch to|tune to) (previous|last)( station| track)?$/i
    ],
    station: [
      /^(play|tune to|switch to|go to) (?:station )?(.+)$/i,
      /^change (?:to )?(?:station )?(.+)$/i
    ],
    volume_up: [
      /^(volume up|louder|increase volume|turn up)$/i,
      /^make it louder$/i
    ],
    volume_down: [
      /^(volume down|quieter|decrease volume|turn down)$/i,
      /^make it quieter$/i
    ],
    search: [
      /^(search|find|look for|play) (.+)$/i,
      /^find (?:me )?(?:some )?(.+)$/i
    ],
    // External source commands
    browse: [
      /^(browse|show|open) (.+)$/i,
      /^browse (?:music )?(?:from )?(.+)$/i
    ],
    source: [
      /^(?:switch to|use|open) (jamendo|bensound|free music archive|audio blocks|auboutdufil)$/i
    ]
  };

  constructor() {
    this.initializeSpeechRecognition();
  }

  // Initialize speech recognition based on platform
  private initializeSpeechRecognition() {
    // Web Speech API implementation
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      recognition.maxAlternatives = 1;

      this.speechRecognition = {
        start: () => {
          return new Promise((resolve, reject) => {
            recognition.start();
            recognition.onstart = () => resolve();
            recognition.onerror = (event: any) => reject(new Error(event.error));
          });
        },
        stop: () => {
          return new Promise((resolve) => {
            recognition.stop();
            recognition.onstop = () => resolve();
          });
        },
        onResult: (callback: (result: string) => void) => {
          recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            callback(transcript);
          };
        },
        onError: (callback: (error: Error) => void) => {
          recognition.onerror = (event: any) => {
            callback(new Error(event.error));
          };
        }
      };
    }
  }

  // Start listening for voice commands
  async startListening(): Promise<void> {
    if (this.isListening || !this.speechRecognition) {
      return;
    }

    try {
      this.isListening = true;
      
      this.speechRecognition.onResult((transcript: string) => {
        this.processVoiceCommand(transcript);
      });

      this.speechRecognition.onError((error: Error) => {
        console.error('Speech recognition error:', error);
        this.isListening = false;
        this.notifyResponse({
          success: false,
          message: `Voice recognition error: ${error.message}`
        });
      });

      await this.speechRecognition.start();
    } catch (error) {
      this.isListening = false;
      throw error;
    }
  }

  // Stop listening for voice commands
  async stopListening(): Promise<void> {
    if (!this.isListening || !this.speechRecognition) {
      return;
    }

    try {
      await this.speechRecognition.stop();
      this.isListening = false;
    } catch (error) {
      console.error('Error stopping speech recognition:', error);
    }
  }

  // Process recognized speech into voice commands
  private async processVoiceCommand(transcript: string): Promise<void> {
    try {
      console.log('Processing voice command:', transcript);
      
      // First try pattern matching for quick commands
      const command = this.parseCommand(transcript);
      
      if (command.intent === 'unknown') {
        // Use AI to interpret complex commands
        const aiCommand = await this.interpretWithAI(transcript);
        if (aiCommand) {
          command.intent = aiCommand.intent;
          command.parameters = aiCommand.parameters;
          command.confidence = aiCommand.confidence;
        }
      }

      // Execute the command
      const response = await this.executeCommand(command);
      
      // Notify listeners
      this.notifyCommand(command);
      this.notifyResponse(response);

      // Provide voice feedback
      await this.speakResponse(response.message);

    } catch (error) {
      console.error('Error processing voice command:', error);
      this.notifyResponse({
        success: false,
        message: 'Sorry, I couldn\'t understand that command.'
      });
    } finally {
      this.isListening = false;
    }
  }

  // Parse command using pattern matching
  private parseCommand(transcript: string): VoiceCommand {
    const text = transcript.toLowerCase().trim();

    for (const [intent, patterns] of Object.entries(this.commandPatterns)) {
      for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) {
          const parameters: Record<string, any> = {};
          
          // Extract parameters based on intent
          if (intent === 'station' && match[2]) {
            parameters.station = match[2].trim();
          } else if (intent === 'search' && match[2]) {
            parameters.query = match[2].trim();
          } else if (intent === 'browse' && match[2]) {
            parameters.source = match[2].trim();
          } else if (intent === 'source' && match[1]) {
            parameters.source = match[1].trim();
          }

          return {
            intent,
            parameters,
            confidence: 0.9,
            originalText: transcript
          };
        }
      }
    }

    return {
      intent: 'unknown',
      parameters: {},
      confidence: 0.0,
      originalText: transcript
    };
  }

  // Use AI (Emergent LLM) to interpret complex commands
  private async interpretWithAI(transcript: string): Promise<VoiceCommand | null> {
    try {
      const response = await fetch(`${this.backendUrl}/api/voice/interpret`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.emergentApiKey}`
        },
        body: JSON.stringify({
          text: transcript,
          context: 'radio_control'
        })
      });

      if (!response.ok) {
        throw new Error(`AI interpretation failed: ${response.status}`);
      }

      const result = await response.json();
      return {
        intent: result.intent || 'unknown',
        parameters: result.parameters || {},
        confidence: result.confidence || 0.5,
        originalText: transcript
      };
    } catch (error) {
      console.error('AI interpretation error:', error);
      return null;
    }
  }

  // Execute the parsed command
  private async executeCommand(command: VoiceCommand): Promise<VoiceResponse> {
    try {
      switch (command.intent) {
        case 'play':
          return {
            success: true,
            message: 'Starting radio playback',
            action: 'play'
          };

        case 'pause':
          return {
            success: true,
            message: 'Radio paused',
            action: 'pause'
          };

        case 'next':
          return {
            success: true,
            message: 'Switching to next station',
            action: 'next_station'
          };

        case 'previous':
          return {
            success: true,
            message: 'Switching to previous station',
            action: 'previous_station'
          };

        case 'station':
          const station = command.parameters.station;
          return {
            success: true,
            message: `Tuning to ${station}`,
            action: 'change_station',
            data: { station }
          };

        case 'volume_up':
          return {
            success: true,
            message: 'Increasing volume',
            action: 'volume_up'
          };

        case 'volume_down':
          return {
            success: true,
            message: 'Decreasing volume',
            action: 'volume_down'
          };

        case 'search':
          const query = command.parameters.query;
          return {
            success: true,
            message: `Searching for ${query}`,
            action: 'search',
            data: { query }
          };

        case 'browse':
          const source = command.parameters.source;
          return {
            success: true,
            message: `Opening ${source}`,
            action: 'browse_source',
            data: { source }
          };

        case 'source':
          const newSource = command.parameters.source;
          return {
            success: true,
            message: `Switching to ${newSource}`,
            action: 'switch_source',
            data: { source: newSource }
          };

        default:
          return {
            success: false,
            message: 'Sorry, I didn\'t understand that command. Try saying "play", "pause", "next station", or "search for music".'
          };
      }
    } catch (error) {
      console.error('Command execution error:', error);
      return {
        success: false,
        message: 'Sorry, there was an error executing that command.'
      };
    }
  }

  // Provide text-to-speech feedback
  private async speakResponse(message: string): Promise<void> {
    try {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(message);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        // Use a pleasant voice if available
        const voices = speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice => 
          voice.name.includes('Female') || voice.name.includes('Samantha') || voice.name.includes('Karen')
        );
        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }

        speechSynthesis.speak(utterance);
      }
    } catch (error) {
      console.error('Text-to-speech error:', error);
    }
  }

  // Register callback for voice commands
  onCommand(callback: (command: VoiceCommand) => void): void {
    this.commandCallbacks.push(callback);
  }

  // Register callback for voice responses
  onResponse(callback: (response: VoiceResponse) => void): void {
    this.responseCallbacks.push(callback);
  }

  // Remove command callback
  removeCommandCallback(callback: (command: VoiceCommand) => void): void {
    const index = this.commandCallbacks.indexOf(callback);
    if (index > -1) {
      this.commandCallbacks.splice(index, 1);
    }
  }

  // Remove response callback
  removeResponseCallback(callback: (response: VoiceResponse) => void): void {
    const index = this.responseCallbacks.indexOf(callback);
    if (index > -1) {
      this.responseCallbacks.splice(index, 1);
    }
  }

  // Notify command listeners
  private notifyCommand(command: VoiceCommand): void {
    this.commandCallbacks.forEach(callback => {
      try {
        callback(command);
      } catch (error) {
        console.error('Command callback error:', error);
      }
    });
  }

  // Notify response listeners
  private notifyResponse(response: VoiceResponse): void {
    this.responseCallbacks.forEach(callback => {
      try {
        callback(response);
      } catch (error) {
        console.error('Response callback error:', error);
      }
    });
  }

  // Get listening status
  get listening(): boolean {
    return this.isListening;
  }

  // Check if speech recognition is available
  get available(): boolean {
    return this.speechRecognition !== null;
  }

  // Get supported commands help
  getCommands(): string[] {
    return [
      "Play radio - Start playing music",
      "Pause - Stop the current music",
      "Next station - Switch to next station",
      "Previous station - Go to previous station",
      "Volume up/down - Adjust volume",
      "Search for [artist/song] - Find specific music",
      "Play station [name] - Tune to specific station",
      "Browse [source] - Open music source",
      "Switch to [Jamendo/Bensound/etc] - Change music source"
    ];
  }

  // Test voice recognition
  async testVoiceRecognition(): Promise<boolean> {
    if (!this.available) {
      return false;
    }

    try {
      await this.startListening();
      await new Promise(resolve => setTimeout(resolve, 1000));
      await this.stopListening();
      return true;
    } catch (error) {
      console.error('Voice recognition test failed:', error);
      return false;
    }
  }
}

export default new VoiceControlService();
export type { VoiceCommand, VoiceResponse };