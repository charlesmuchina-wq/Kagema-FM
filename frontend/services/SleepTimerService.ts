import { Audio } from 'expo-audio';
import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface SleepTimerOptions {
  duration: number; // in minutes
  fadeOut: boolean;
  showNotification: boolean;
}

export interface SleepTimerState {
  isActive: boolean;
  remainingTime: number; // in seconds
  originalDuration: number; // in minutes
  startTime: number; // timestamp
}

class SleepTimerService {
  private timer: NodeJS.Timeout | null = null;
  private fadeOutTimer: NodeJS.Timeout | null = null;
  private listeners: Set<(state: SleepTimerState) => void> = new Set();
  private currentState: SleepTimerState = {
    isActive: false,
    remainingTime: 0,
    originalDuration: 0,
    startTime: 0
  };

  // Predefined timer options
  public readonly presets = [
    { label: '15 minutes', value: 15 },
    { label: '30 minutes', value: 30 },
    { label: '45 minutes', value: 45 },
    { label: '1 hour', value: 60 },
    { label: '2 hours', value: 120 },
    { label: '3 hours', value: 180 }
  ];

  constructor() {
    this.initializeNotifications();
    this.restoreTimerState();
  }

  private async initializeNotifications() {
    try {
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        console.log('Notification permissions not granted');
        return;
      }

      // Configure notification handler
      Notifications.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false,
        }),
      });

      console.log('🔔 Sleep timer notifications initialized');
    } catch (error) {
      console.error('❌ Failed to initialize notifications:', error);
    }
  }

  private async restoreTimerState() {
    try {
      const savedState = await AsyncStorage.getItem('sleepTimerState');
      if (savedState) {
        const state = JSON.parse(savedState);
        const now = Date.now();
        
        // Check if timer should still be active
        if (state.isActive && state.startTime) {
          const elapsed = Math.floor((now - state.startTime) / 1000);
          const totalDuration = state.originalDuration * 60;
          
          if (elapsed < totalDuration) {
            // Resume timer
            this.currentState = {
              ...state,
              remainingTime: totalDuration - elapsed
            };
            
            this.startCountdown();
            console.log('⏰ Sleep timer resumed from background');
          } else {
            // Timer expired while app was closed
            this.clearTimer();
          }
        }
      }
    } catch (error) {
      console.error('❌ Failed to restore timer state:', error);
    }
  }

  private async saveTimerState() {
    try {
      await AsyncStorage.setItem('sleepTimerState', JSON.stringify(this.currentState));
    } catch (error) {
      console.error('❌ Failed to save timer state:', error);
    }
  }

  /**
   * Start the sleep timer
   */
  async startTimer(options: SleepTimerOptions): Promise<boolean> {
    try {
      // Clear any existing timer
      this.clearTimer();

      const durationInSeconds = options.duration * 60;
      const now = Date.now();

      this.currentState = {
        isActive: true,
        remainingTime: durationInSeconds,
        originalDuration: options.duration,
        startTime: now
      };

      // Save state for app backgrounding
      await this.saveTimerState();

      // Schedule notification
      if (options.showNotification) {
        await this.scheduleTimerNotification(options.duration);
      }

      // Start countdown
      this.startCountdown();

      // Notify listeners
      this.notifyListeners();

      console.log(`⏰ Sleep timer started: ${options.duration} minutes`);
      return true;
    } catch (error) {
      console.error('❌ Failed to start sleep timer:', error);
      return false;
    }
  }

  private startCountdown() {
    this.timer = setInterval(() => {
      if (this.currentState.remainingTime > 0) {
        this.currentState.remainingTime--;
        this.notifyListeners();

        // Start fade out 30 seconds before end
        if (this.currentState.remainingTime === 30 && !this.fadeOutTimer) {
          this.startFadeOut();
        }
      } else {
        // Timer finished
        this.onTimerComplete();
      }
    }, 1000);
  }

  private async startFadeOut() {
    try {
      console.log('🔊 Starting audio fade out...');
      
      // Gradually reduce volume over 30 seconds
      const fadeSteps = 30;
      const originalVolume = await Audio.getVolumeAsync();
      
      this.fadeOutTimer = setInterval(async () => {
        const currentStep = 30 - this.currentState.remainingTime;
        if (currentStep >= fadeSteps) {
          clearInterval(this.fadeOutTimer!);
          this.fadeOutTimer = null;
          return;
        }
        
        const newVolume = originalVolume * (1 - (currentStep / fadeSteps));
        await Audio.setVolumeAsync(Math.max(newVolume, 0));
      }, 1000);
      
    } catch (error) {
      console.error('❌ Failed to start fade out:', error);
    }
  }

  private async onTimerComplete() {
    console.log('⏰ Sleep timer completed');
    
    try {
      // Stop audio playback
      await Audio.pauseAsync();
      
      // Show completion notification
      await this.showCompletionNotification();
      
      // Clear timer
      this.clearTimer();
      
      // Notify listeners
      this.notifyListeners();
      
    } catch (error) {
      console.error('❌ Error completing sleep timer:', error);
    }
  }

  private async scheduleTimerNotification(duration: number) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: 'Sleep Timer',
          body: `Your ${duration} minute sleep timer will end in 1 minute`,
          data: { type: 'sleep_timer_warning' },
        },
        trigger: {
          seconds: Math.max((duration - 1) * 60, 60), // 1 minute before completion
        },
      });

      await Notifications.scheduleNotificationAsync({
        content: {
          title: 'Sleep Timer Complete',
          body: 'Your radio has stopped playing. Sweet dreams! 😴',
          data: { type: 'sleep_timer_complete' },
        },
        trigger: {
          seconds: duration * 60,
        },
      });

      console.log('📱 Sleep timer notifications scheduled');
    } catch (error) {
      console.error('❌ Failed to schedule notifications:', error);
    }
  }

  private async showCompletionNotification() {
    try {
      await Notifications.presentNotificationAsync({
        title: 'Sleep Timer Complete',
        body: 'Kagema FM has stopped playing. Good night! 🌙',
        data: { type: 'sleep_timer_complete' },
      });
    } catch (error) {
      console.error('❌ Failed to show completion notification:', error);
    }
  }

  /**
   * Cancel the active sleep timer
   */
  async cancelTimer(): Promise<void> {
    console.log('❌ Sleep timer cancelled');
    
    try {
      // Cancel scheduled notifications
      await Notifications.cancelAllScheduledNotificationsAsync();
      
      // Restore volume if it was being faded
      if (this.fadeOutTimer) {
        await Audio.setVolumeAsync(1.0);
      }
      
      // Clear timer
      this.clearTimer();
      
      // Notify listeners
      this.notifyListeners();
      
    } catch (error) {
      console.error('❌ Failed to cancel sleep timer:', error);
    }
  }

  private clearTimer() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    
    if (this.fadeOutTimer) {
      clearInterval(this.fadeOutTimer);
      this.fadeOutTimer = null;
    }

    this.currentState = {
      isActive: false,
      remainingTime: 0,
      originalDuration: 0,
      startTime: 0
    };

    // Clear saved state
    AsyncStorage.removeItem('sleepTimerState');
  }

  /**
   * Get current timer state
   */
  getState(): SleepTimerState {
    return { ...this.currentState };
  }

  /**
   * Format remaining time for display
   */
  getFormattedTime(): string {
    const minutes = Math.floor(this.currentState.remainingTime / 60);
    const seconds = this.currentState.remainingTime % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  /**
   * Get progress percentage (0-100)
   */
  getProgress(): number {
    if (!this.currentState.isActive || this.currentState.originalDuration === 0) {
      return 0;
    }
    
    const totalSeconds = this.currentState.originalDuration * 60;
    const elapsed = totalSeconds - this.currentState.remainingTime;
    return (elapsed / totalSeconds) * 100;
  }

  /**
   * Add a listener for timer state changes
   */
  addListener(callback: (state: SleepTimerState) => void): () => void {
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(callback => {
      try {
        callback(this.currentState);
      } catch (error) {
        console.error('❌ Sleep timer listener error:', error);
      }
    });
  }

  /**
   * Check if timer is currently active
   */
  isActive(): boolean {
    return this.currentState.isActive;
  }

  /**
   * Get time remaining in minutes (rounded up)
   */
  getRemainingMinutes(): number {
    return Math.ceil(this.currentState.remainingTime / 60);
  }

  /**
   * Add time to current timer
   */
  async addTime(minutes: number): Promise<boolean> {
    if (!this.currentState.isActive) {
      return false;
    }

    try {
      this.currentState.remainingTime += minutes * 60;
      this.currentState.originalDuration += minutes;
      
      await this.saveTimerState();
      this.notifyListeners();
      
      console.log(`⏰ Added ${minutes} minutes to sleep timer`);
      return true;
    } catch (error) {
      console.error('❌ Failed to add time to timer:', error);
      return false;
    }
  }

  /**
   * Clean up resources
   */
  cleanup() {
    this.clearTimer();
    this.listeners.clear();
  }
}

// Export singleton instance
export const sleepTimerService = new SleepTimerService();
export default SleepTimerService;