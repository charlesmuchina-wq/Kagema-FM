import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform, AccessibilityInfo, Alert, Dimensions } from 'react-native';
import * as Speech from 'expo-speech';
import { Haptics } from 'expo-haptics';

export interface AccessibilitySettings {
  screenReaderEnabled: boolean;
  highContrastEnabled: boolean;
  largeTextEnabled: boolean;
  hapticFeedbackEnabled: boolean;
  voiceAnnouncementsEnabled: boolean;
  reducedMotionEnabled: boolean;
  autoplayAudioDescriptions: boolean;
  fontSizeMultiplier: number; // 1.0 = normal, 1.5 = large, 2.0 = extra large
  touchTargetSizeMultiplier: number; // 1.0 = normal, 1.5 = large
  colorTheme: 'normal' | 'high_contrast' | 'high_contrast_dark';
  keyboardNavigationEnabled: boolean;
}

export interface AccessibilityColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  focus: string;
  success: string;
  warning: string;
  error: string;
}

class AccessibilityService {
  private static instance: AccessibilityService;
  private settings: AccessibilitySettings;
  private listeners: Set<(settings: AccessibilitySettings) => void> = new Set();
  private screenReaderEnabled: boolean = false;
  private focusedElement: string | null = null;

  private constructor() {
    this.settings = {
      screenReaderEnabled: false,
      highContrastEnabled: false,
      largeTextEnabled: false,
      hapticFeedbackEnabled: true,
      voiceAnnouncementsEnabled: false,
      reducedMotionEnabled: false,
      autoplayAudioDescriptions: false,
      fontSizeMultiplier: 1.0,
      touchTargetSizeMultiplier: 1.0,
      colorTheme: 'normal',
      keyboardNavigationEnabled: false,
    };
    this.initialize();
  }

  public static getInstance(): AccessibilityService {
    if (!AccessibilityService.instance) {
      AccessibilityService.instance = new AccessibilityService();
    }
    return AccessibilityService.instance;
  }

  private async initialize(): Promise<void> {
    try {
      // Load saved settings
      await this.loadSettings();
      
      // Detect system accessibility settings
      await this.detectSystemSettings();
      
      // Setup accessibility listeners
      this.setupAccessibilityListeners();
      
      console.log('✅ Accessibility service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize accessibility service:', error);
    }
  }

  private async detectSystemSettings(): Promise<void> {
    try {
      // Detect screen reader
      const isScreenReaderEnabled = await AccessibilityInfo.isScreenReaderEnabled();
      this.screenReaderEnabled = isScreenReaderEnabled;
      
      if (isScreenReaderEnabled && !this.settings.screenReaderEnabled) {
        this.settings.screenReaderEnabled = true;
        this.settings.voiceAnnouncementsEnabled = true;
        console.log('🔊 Screen reader detected - enabling accessibility features');
      }

      // Detect reduced motion (iOS)
      if (Platform.OS === 'ios') {
        try {
          const isReduceMotionEnabled = await AccessibilityInfo.isReduceMotionEnabled();
          if (isReduceMotionEnabled) {
            this.settings.reducedMotionEnabled = true;
            console.log('🎭 Reduced motion preference detected');
          }
        } catch (error) {
          console.log('ℹ️ Reduced motion detection not available');
        }
      }

      await this.saveSettings();
      this.notifyListeners();
    } catch (error) {
      console.error('❌ Failed to detect system accessibility settings:', error);
    }
  }

  private setupAccessibilityListeners(): void {
    // Listen for screen reader changes
    AccessibilityInfo.addEventListener('screenReaderChanged', (isEnabled) => {
      this.screenReaderEnabled = isEnabled;
      if (isEnabled !== this.settings.screenReaderEnabled) {
        this.updateSettings({ 
          screenReaderEnabled: isEnabled,
          voiceAnnouncementsEnabled: isEnabled 
        });
        this.announceScreenReaderStatus(isEnabled);
      }
    });

    // Listen for reduce motion changes (iOS)
    if (Platform.OS === 'ios') {
      AccessibilityInfo.addEventListener('reduceMotionChanged', (isEnabled) => {
        if (isEnabled !== this.settings.reducedMotionEnabled) {
          this.updateSettings({ reducedMotionEnabled: isEnabled });
        }
      });
    }
  }

  // Update accessibility settings
  async updateSettings(newSettings: Partial<AccessibilitySettings>): Promise<void> {
    const previousSettings = { ...this.settings };
    this.settings = { ...this.settings, ...newSettings };
    
    // Handle specific setting changes
    if (newSettings.voiceAnnouncementsEnabled !== undefined) {
      if (newSettings.voiceAnnouncementsEnabled) {
        this.announce('Voice announcements enabled');
      }
    }

    if (newSettings.hapticFeedbackEnabled !== undefined) {
      if (newSettings.hapticFeedbackEnabled) {
        await this.hapticFeedback('light');
      }
    }

    if (newSettings.highContrastEnabled !== undefined || newSettings.colorTheme !== undefined) {
      this.announceIf('Display theme updated for better visibility');
    }

    await this.saveSettings();
    this.notifyListeners();
    
    console.log('♿ Accessibility settings updated');
  }

  // Get current settings
  getSettings(): AccessibilitySettings {
    return { ...this.settings };
  }

  // Get accessibility colors based on current theme
  getAccessibilityColors(): AccessibilityColors {
    switch (this.settings.colorTheme) {
      case 'high_contrast':
        return {
          primary: '#000000',
          secondary: '#000000',
          background: '#FFFFFF',
          surface: '#F5F5F5',
          text: '#000000',
          textSecondary: '#333333',
          border: '#000000',
          focus: '#0066CC',
          success: '#006600',
          warning: '#CC6600',
          error: '#CC0000',
        };
      
      case 'high_contrast_dark':
        return {
          primary: '#FFFFFF',
          secondary: '#FFFF00',
          background: '#000000',
          surface: '#1A1A1A',
          text: '#FFFFFF',
          textSecondary: '#CCCCCC',
          border: '#FFFFFF',
          focus: '#00CCFF',
          success: '#00FF00',
          warning: '#FFCC00',
          error: '#FF0000',
        };
      
      default: // normal
        return {
          primary: '#FF6B6B',
          secondary: '#4ECDC4',
          background: '#FFFFFF',
          surface: '#F8F9FA',
          text: '#333333',
          textSecondary: '#666666',
          border: '#E0E0E0',
          focus: '#4285F4',
          success: '#4CAF50',
          warning: '#FF9800',
          error: '#F44336',
        };
    }
  }

  // Get font size based on accessibility settings
  getFontSize(baseSize: number): number {
    return baseSize * this.settings.fontSizeMultiplier;
  }

  // Get touch target size based on accessibility settings
  getTouchTargetSize(baseSize: number): number {
    const multiplier = this.settings.touchTargetSizeMultiplier;
    const minSize = Platform.OS === 'ios' ? 44 : 48; // Platform minimum guidelines
    const adjustedSize = baseSize * multiplier;
    return Math.max(adjustedSize, minSize);
  }

  // Voice announcements
  async announce(message: string, priority: 'low' | 'high' = 'low'): Promise<void> {
    if (!this.settings.voiceAnnouncementsEnabled && !this.screenReaderEnabled) return;
    
    try {
      await Speech.speak(message, {
        language: 'en-US',
        pitch: 1.0,
        rate: this.settings.reducedMotionEnabled ? 0.8 : 1.0,
      });
    } catch (error) {
      console.error('❌ Failed to announce message:', error);
    }
  }

  // Announce only if voice announcements are enabled
  announceIf(message: string): void {
    if (this.settings.voiceAnnouncementsEnabled) {
      this.announce(message);
    }
  }

  // Announce screen reader status change
  private announceScreenReaderStatus(isEnabled: boolean): void {
    const message = isEnabled 
      ? 'Screen reader enabled. Kagema FM accessibility features are now active.'
      : 'Screen reader disabled.';
    this.announce(message, 'high');
  }

  // Haptic feedback
  async hapticFeedback(type: 'light' | 'medium' | 'heavy' | 'success' | 'warning' | 'error' = 'light'): Promise<void> {
    if (!this.settings.hapticFeedbackEnabled) return;

    try {
      switch (type) {
        case 'light':
          await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          break;
        case 'medium':
          await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          break;
        case 'heavy':
          await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          break;
        case 'success':
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          break;
        case 'warning':
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          break;
        case 'error':
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
          break;
      }
    } catch (error) {
      console.error('❌ Haptic feedback failed:', error);
    }
  }

  // Focus management for keyboard navigation
  setFocusedElement(elementId: string, description?: string): void {
    this.focusedElement = elementId;
    if (description && this.settings.keyboardNavigationEnabled) {
      this.announceIf(`Focused: ${description}`);
    }
  }

  getFocusedElement(): string | null {
    return this.focusedElement;
  }

  // Accessibility hints for UI elements
  getAccessibilityHint(type: 'button' | 'toggle' | 'slider' | 'tab', state?: any): string {
    switch (type) {
      case 'button':
        return 'Double tap to activate';
      case 'toggle':
        return state ? 'Double tap to turn off' : 'Double tap to turn on';
      case 'slider':
        return 'Swipe up or down to adjust value';
      case 'tab':
        return 'Double tap to switch to this tab';
      default:
        return 'Double tap to interact';
    }
  }

  // Generate accessibility labels
  getAccessibilityLabel(context: string, value?: any, state?: any): string {
    switch (context) {
      case 'play_button':
        return state?.isPlaying ? 'Pause radio' : 'Play radio';
      case 'volume_slider':
        return `Volume ${Math.round((value || 0) * 100)} percent`;
      case 'station_button':
        return `Radio station ${value?.name || 'Unknown'}${state?.isPlaying ? ', currently playing' : ''}`;
      case 'car_mode_toggle':
        return `Car mode ${state?.isActive ? 'active' : 'inactive'}`;
      case 'favorite_button':
        return `${state?.isFavorite ? 'Remove from' : 'Add to'} favorites`;
      default:
        return context;
    }
  }

  // Screen reader compatibility helpers
  getAccessibilityRole(elementType: string): string {
    const roleMap: { [key: string]: string } = {
      'button': 'button',
      'link': 'link',
      'slider': 'adjustable',
      'toggle': 'switch',
      'tab': 'tab',
      'header': 'header',
      'text': 'text',
      'image': 'image',
      'list': 'list',
    };
    return roleMap[elementType] || 'none';
  }

  // Generate style adjustments for accessibility
  getAccessibilityStyles(baseStyles: any): any {
    const styles = { ...baseStyles };
    
    // Adjust font sizes
    if (styles.fontSize) {
      styles.fontSize = this.getFontSize(styles.fontSize);
    }

    // Adjust touch targets
    if (styles.width && styles.height) {
      const minSize = this.getTouchTargetSize(Math.min(styles.width, styles.height));
      if (styles.width < minSize) styles.width = minSize;
      if (styles.height < minSize) styles.height = minSize;
    }

    // Apply high contrast colors if enabled
    if (this.settings.highContrastEnabled || this.settings.colorTheme !== 'normal') {
      const accessibilityColors = this.getAccessibilityColors();
      if (styles.color) styles.color = accessibilityColors.text;
      if (styles.backgroundColor) styles.backgroundColor = accessibilityColors.background;
      if (styles.borderColor) styles.borderColor = accessibilityColors.border;
    }

    // Reduce animations if requested
    if (this.settings.reducedMotionEnabled) {
      styles.animationDuration = 0;
      styles.transitionDuration = 0;
    }

    return styles;
  }

  // Keyboard navigation helpers
  async handleKeyboardNavigation(key: string, currentFocus: string): Promise<string | null> {
    if (!this.settings.keyboardNavigationEnabled) return null;

    // This would be implemented based on your app's navigation structure
    // For now, return null to indicate no navigation occurred
    switch (key) {
      case 'ArrowUp':
      case 'ArrowDown':
      case 'ArrowLeft':
      case 'ArrowRight':
        this.hapticFeedback('light');
        // Navigate to next/previous focusable element
        break;
      case 'Enter':
      case ' ':
        this.hapticFeedback('medium');
        // Activate current element
        break;
      case 'Escape':
        // Close modal or go back
        break;
    }
    
    return null;
  }

  // Audio descriptions for media content
  async announceMediaState(state: 'playing' | 'paused' | 'stopped' | 'loading', title?: string): Promise<void> {
    if (!this.settings.autoplayAudioDescriptions && !this.screenReaderEnabled) return;
    
    const messages = {
      playing: `Now playing${title ? `: ${title}` : ''}`,
      paused: 'Playback paused',
      stopped: 'Playback stopped',
      loading: 'Loading audio content',
    };
    
    await this.announce(messages[state]);
  }

  // Emergency accessibility features
  async enableEmergencyAccessibility(): Promise<void> {
    console.log('🚨 Enabling emergency accessibility mode');
    
    await this.updateSettings({
      screenReaderEnabled: true,
      voiceAnnouncementsEnabled: true,
      hapticFeedbackEnabled: true,
      highContrastEnabled: true,
      largeTextEnabled: true,
      fontSizeMultiplier: 1.5,
      touchTargetSizeMultiplier: 1.5,
      colorTheme: 'high_contrast',
    });
    
    await this.announce('Emergency accessibility mode activated. All accessibility features are now enabled.', 'high');
    await this.hapticFeedback('heavy');
  }

  // Settings persistence
  private async loadSettings(): Promise<void> {
    try {
      const storedSettings = await AsyncStorage.getItem('accessibility_settings');
      if (storedSettings) {
        this.settings = { ...this.settings, ...JSON.parse(storedSettings) };
      }
    } catch (error) {
      console.error('❌ Failed to load accessibility settings:', error);
    }
  }

  private async saveSettings(): Promise<void> {
    try {
      await AsyncStorage.setItem('accessibility_settings', JSON.stringify(this.settings));
    } catch (error) {
      console.error('❌ Failed to save accessibility settings:', error);
    }
  }

  // Listener management
  addListener(callback: (settings: AccessibilitySettings) => void): () => void {
    this.listeners.add(callback);
    
    // Immediately call with current settings
    callback(this.settings);
    
    return () => {
      this.listeners.delete(callback);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(callback => {
      try {
        callback(this.settings);
      } catch (error) {
        console.error('❌ Accessibility listener error:', error);
      }
    });
  }

  // Get quick accessibility report
  getAccessibilityReport(): string {
    const features = [];
    if (this.settings.screenReaderEnabled) features.push('Screen Reader');
    if (this.settings.highContrastEnabled) features.push('High Contrast');
    if (this.settings.largeTextEnabled) features.push('Large Text');
    if (this.settings.hapticFeedbackEnabled) features.push('Haptic Feedback');
    if (this.settings.voiceAnnouncementsEnabled) features.push('Voice Announcements');
    if (this.settings.keyboardNavigationEnabled) features.push('Keyboard Navigation');
    
    return features.length > 0 
      ? `Accessibility features active: ${features.join(', ')}`
      : 'No accessibility features currently active';
  }
}

// Export singleton instance
export const accessibilityService = AccessibilityService.getInstance();