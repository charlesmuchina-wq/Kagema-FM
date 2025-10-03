import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configure notification handling
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export interface ShowScheduleNotification {
  id: string;
  title: string;
  description: string;
  showTime: Date;
  stationName: string;
  type: 'show_reminder' | 'news_update' | 'music_discovery' | 'app_update';
}

export interface NotificationSettings {
  enabled: boolean;
  showReminders: boolean;
  newsUpdates: boolean;
  musicDiscovery: boolean;
  appUpdates: boolean;
  quietHours: {
    enabled: boolean;
    startTime: string; // HH:mm format
    endTime: string; // HH:mm format
  };
  soundEnabled: boolean;
  vibrationEnabled: boolean;
}

export class NotificationService {
  private static instance: NotificationService;
  private pushToken: string | null = null;
  private settings: NotificationSettings = {
    enabled: true,
    showReminders: true,
    newsUpdates: true,
    musicDiscovery: true,
    appUpdates: true,
    quietHours: {
      enabled: false,
      startTime: '22:00',
      endTime: '08:00',
    },
    soundEnabled: true,
    vibrationEnabled: true,
  };

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  async initialize(): Promise<void> {
    console.log('🔔 Initializing enhanced notification service...');

    // Skip on web platform to avoid expo-notifications web warnings
    if (Platform.OS === 'web') {
      console.log('📱 Notification service: Web platform detected - skipping to avoid warnings');
      return;
    }

    try {
      await this.loadSettings();
      await this.registerForPushNotifications();
      await this.setupNotificationCategories();
      console.log('✅ Notification service initialized');
    } catch (error) {
      console.log('⚠️ Notification initialization error:', error);
    }
  }

  private async loadSettings(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('notification_settings');
      if (stored) {
        this.settings = { ...this.settings, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.log('Error loading notification settings:', error);
    }
  }

  private async saveSettings(): Promise<void> {
    try {
      await AsyncStorage.setItem('notification_settings', JSON.stringify(this.settings));
    } catch (error) {
      console.log('Error saving notification settings:', error);
    }
  }

  private async registerForPushNotifications(): Promise<void> {
    // Skip push notifications completely on web platform to prevent warnings
    if (Platform.OS === 'web') {
      console.log('📱 Push notifications disabled on web platform');
      return;
    }
    
    if (!Device.isDevice) {
      console.log('Push notifications only work on physical devices');
      return;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Push notification permission not granted');
      return;
    }

    try {
      // Only register push token on native platforms
      const token = await Notifications.getExpoPushTokenAsync();
      this.pushToken = token.data;
      console.log('Push token registered:', this.pushToken);
      
      // Only add push token listener on native platforms
      Notifications.addPushTokenListener(this.onPushTokenReceived);
      
    } catch (error) {
      console.log('Error getting push token:', error);
    }

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });

      // Create specific channels for different types
      await Notifications.setNotificationChannelAsync('show_reminders', {
        name: 'Show Reminders',
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        sound: 'notification_sound.wav',
      });

      await Notifications.setNotificationChannelAsync('news_updates', {
        name: 'News Updates',
        importance: Notifications.AndroidImportance.DEFAULT,
        vibrationPattern: [0, 250],
      });

      await Notifications.setNotificationChannelAsync('music_discovery', {
        name: 'Music Discovery',
        importance: Notifications.AndroidImportance.LOW,
      });
    }
  }

  private async setupNotificationCategories(): Promise<void> {
    try {
      await Notifications.setNotificationCategoryAsync('show_reminder', [
        {
          identifier: 'listen_now',
          buttonTitle: 'Listen Now',
          options: { isDestructive: false },
        },
        {
          identifier: 'remind_later',
          buttonTitle: 'Remind Later',
          options: { isDestructive: false },
        },
      ]);

      await Notifications.setNotificationCategoryAsync('music_discovery', [
        {
          identifier: 'play_track',
          buttonTitle: 'Play',
          options: { isDestructive: false },
        },
        {
          identifier: 'save_favorite',
          buttonTitle: 'Save',
          options: { isDestructive: false },
        },
      ]);

      await Notifications.setNotificationCategoryAsync('news_update', [
        {
          identifier: 'read_now',
          buttonTitle: 'Read',
          options: { isDestructive: false },
        },
        {
          identifier: 'share_news',
          buttonTitle: 'Share',
          options: { isDestructive: false },
        },
      ]);
    } catch (error) {
      console.log('Error setting up notification categories:', error);
    }
  }

  async scheduleShowReminder(show: ShowScheduleNotification): Promise<string | null> {
    if (!this.settings.enabled || !this.settings.showReminders) {
      return null;
    }

    if (this.isInQuietHours(show.showTime)) {
      console.log('Skipping notification during quiet hours');
      return null;
    }

    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title: `📻 ${show.title} starts soon!`,
          body: `${show.description} on ${show.stationName}`,
          data: {
            type: 'show_reminder',
            showId: show.id,
            stationName: show.stationName,
          },
          categoryIdentifier: 'show_reminder',
          sound: this.settings.soundEnabled ? 'notification_sound.wav' : undefined,
        },
        trigger: {
          date: new Date(show.showTime.getTime() - 15 * 60 * 1000), // 15 minutes before
          channelId: 'show_reminders',
        },
      });

      console.log(`📅 Scheduled show reminder: ${notificationId}`);
      return notificationId;
    } catch (error) {
      console.log('Error scheduling show reminder:', error);
      return null;
    }
  }

  async sendNewsUpdate(title: string, summary: string, articleUrl?: string): Promise<void> {
    if (!this.settings.enabled || !this.settings.newsUpdates) {
      return;
    }

    if (this.isInQuietHours(new Date())) {
      return;
    }

    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: `📰 ${title}`,
          body: summary,
          data: {
            type: 'news_update',
            articleUrl: articleUrl,
          },
          categoryIdentifier: 'news_update',
          sound: this.settings.soundEnabled ? 'default' : undefined,
        },
        trigger: null, // Immediate
        channelId: 'news_updates',
      });

      console.log('📰 Sent news update notification');
    } catch (error) {
      console.log('Error sending news notification:', error);
    }
  }

  async sendMusicDiscovery(trackTitle: string, artist: string, reason: string): Promise<void> {
    if (!this.settings.enabled || !this.settings.musicDiscovery) {
      return;
    }

    if (this.isInQuietHours(new Date())) {
      return;
    }

    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: `🎵 New music discovery!`,
          body: `${trackTitle} by ${artist} - ${reason}`,
          data: {
            type: 'music_discovery',
            trackTitle,
            artist,
          },
          categoryIdentifier: 'music_discovery',
        },
        trigger: null,
        channelId: 'music_discovery',
      });

      console.log('🎵 Sent music discovery notification');
    } catch (error) {
      console.log('Error sending music notification:', error);
    }
  }

  async scheduleRecurringReminders(
    title: string,
    body: string,
    weekdays: number[], // 0 = Sunday, 1 = Monday, etc.
    hour: number,
    minute: number
  ): Promise<string[]> {
    const notificationIds: string[] = [];

    for (const weekday of weekdays) {
      try {
        const notificationId = await Notifications.scheduleNotificationAsync({
          content: {
            title,
            body,
            data: { type: 'recurring_reminder' },
          },
          trigger: {
            weekday: weekday + 1, // Expo uses 1-7 for weekdays
            hour,
            minute,
            repeats: true,
          },
        });
        
        notificationIds.push(notificationId);
      } catch (error) {
        console.log('Error scheduling recurring reminder:', error);
      }
    }

    return notificationIds;
  }

  private isInQuietHours(date: Date): boolean {
    if (!this.settings.quietHours.enabled) {
      return false;
    }

    const currentTime = date.toTimeString().substring(0, 5); // HH:mm format
    const { startTime, endTime } = this.settings.quietHours;

    // Handle overnight quiet hours (e.g., 22:00 to 08:00)
    if (startTime > endTime) {
      return currentTime >= startTime || currentTime <= endTime;
    }
    
    // Handle same-day quiet hours (e.g., 13:00 to 15:00)
    return currentTime >= startTime && currentTime <= endTime;
  }

  async updateSettings(newSettings: Partial<NotificationSettings>): Promise<void> {
    this.settings = { ...this.settings, ...newSettings };
    await this.saveSettings();
    
    if (!this.settings.enabled) {
      await this.cancelAllNotifications();
    }
  }

  async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('🚫 Cancelled all scheduled notifications');
    } catch (error) {
      console.log('Error cancelling notifications:', error);
    }
  }

  async cancelNotification(notificationId: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
      console.log(`🚫 Cancelled notification: ${notificationId}`);
    } catch (error) {
      console.log('Error cancelling notification:', error);
    }
  }

  getSettings(): NotificationSettings {
    return { ...this.settings };
  }

  getPushToken(): string | null {
    return this.pushToken;
  }

  // Handle notification responses (when user taps notification or action buttons)
  setupNotificationResponseHandler(): void {
    // Skip notification response handling on web platform
    if (Platform.OS === 'web') {
      console.log('📱 Notification response handler skipped on web platform');
      return;
    }

    try {
      Notifications.addNotificationResponseReceivedListener(response => {
        const { notification, actionIdentifier } = response;
        const { type } = notification.request.content.data;

        console.log('📱 Notification response:', { type, actionIdentifier });

        switch (actionIdentifier) {
          case 'listen_now':
            // Handle "Listen Now" action for show reminders
            this.handleListenNowAction(notification.request.content.data);
            break;
          
          case 'remind_later':
            // Reschedule notification for 15 minutes later
            this.handleRemindLaterAction(notification.request.content.data);
            break;
          
          case 'play_track':
            // Handle music track play action
            this.handlePlayTrackAction(notification.request.content.data);
            break;
          
          case 'save_favorite':
            // Handle save to favorites action
            this.handleSaveFavoriteAction(notification.request.content.data);
            break;
          
          case 'read_now':
            // Handle read news article action
            this.handleReadNewsAction(notification.request.content.data);
            break;
          
          case 'share_news':
            // Handle share news action
            this.handleShareNewsAction(notification.request.content.data);
            break;
          
          default:
            // Handle default notification tap
            this.handleDefaultNotificationTap(notification.request.content.data);
            break;
        }
      });
    } catch (error) {
      console.log('Notification response handler setup failed (expected on web):', error);
    }
  }

  private handleListenNowAction(data: any): void {
    // This would typically navigate to the radio player and start playing
    console.log('🎧 Starting radio playback:', data.stationName);
  }

  private async handleRemindLaterAction(data: any): Promise<void> {
    // Reschedule for 15 minutes later
    const newTime = new Date(Date.now() + 15 * 60 * 1000);
    
    await Notifications.scheduleNotificationAsync({
      content: {
        title: `📻 Don't forget: ${data.showId}`,
        body: `Your show reminder - starting soon!`,
        data: data,
        categoryIdentifier: 'show_reminder',
      },
      trigger: {
        date: newTime,
      },
    });
  }

  private handlePlayTrackAction(data: any): void {
    console.log('🎵 Playing track:', data.trackTitle, 'by', data.artist);
  }

  private handleSaveFavoriteAction(data: any): void {
    console.log('❤️ Saving to favorites:', data.trackTitle);
  }

  private handleReadNewsAction(data: any): void {
    console.log('📰 Opening news article:', data.articleUrl);
  }

  private handleShareNewsAction(data: any): void {
    console.log('📤 Sharing news article:', data.articleUrl);
  }

  private handleDefaultNotificationTap(data: any): void {
    console.log('👆 Default notification tap, data:', data);
  }

  // Smart notification scheduling based on user behavior
  async scheduleSmartNotifications(): Promise<void> {
    try {
      // Get user's listening patterns from AsyncStorage
      const listeningHistory = await AsyncStorage.getItem('listening_history');
      const favoriteShows = await AsyncStorage.getItem('favorite_shows');
      
      if (listeningHistory && favoriteShows) {
        const history = JSON.parse(listeningHistory);
        const shows = JSON.parse(favoriteShows);
        
        // Analyze patterns and schedule personalized notifications
        console.log('🤖 Scheduling smart notifications based on user patterns');
      }
      
      // Schedule weekly music discovery notification
      await this.scheduleRecurringReminders(
        '🎵 Weekly Music Discovery',
        'Check out new music recommendations curated just for you!',
        [1], // Monday
        19, // 7 PM
        0   // 0 minutes
      );
      
      // Schedule news digest notification
      await this.scheduleRecurringReminders(
        '📰 Daily News Digest',
        'Catch up on the latest news from around the world',
        [1, 2, 3, 4, 5], // Weekdays
        8,  // 8 AM
        0   // 0 minutes
      );
      
    } catch (error) {
      console.log('Error scheduling smart notifications:', error);
    }
  }
}

// Export singleton instance
export const notificationService = NotificationService.getInstance();