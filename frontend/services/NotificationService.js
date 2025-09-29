import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';

// Configure how notifications are handled when the app is in the foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

class NotificationService {
  constructor() {
    this.init();
  }

  async init() {
    try {
      // Request permissions for notifications
      const { status } = await Notifications.requestPermissionsAsync();
      if (status !== 'granted') {
        console.log('Notification permissions not granted');
        return;
      }

      console.log('✅ Notification service initialized');
    } catch (error) {
      console.error('Notification service initialization error:', error);
    }
  }

  async sendRadioNotification(stationName, showName) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: `🎵 ${stationName}`,
          body: `Now Playing: ${showName}`,
          data: { 
            type: 'radio',
            station: stationName,
            show: showName 
          },
        },
        trigger: null, // Show immediately
      });

      console.log('📻 Radio notification sent');
    } catch (error) {
      console.error('Radio notification error:', error);
    }
  }

  async sendConnectivityNotification(connectionType) {
    try {
      const messages = {
        satellite: '🛰️ Connected to satellite network',
        offline: '📴 Offline mode enabled',
        cellular: '📶 Connected via cellular',
        wifi: '📶 Connected via WiFi'
      };

      await Notifications.scheduleNotificationAsync({
        content: {
          title: 'Kagema FM - Connectivity',
          body: messages[connectionType] || 'Connection status updated',
          data: { 
            type: 'connectivity',
            connectionType 
          },
        },
        trigger: null,
      });

      console.log('📡 Connectivity notification sent');
    } catch (error) {
      console.error('Connectivity notification error:', error);
    }
  }

  async sendRegionalStationNotification(region, stationName) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: `🌍 New Regional Station`,
          body: `${stationName} is now available for ${region}`,
          data: { 
            type: 'regional_station',
            region,
            stationName 
          },
        },
        trigger: null,
      });

      console.log('🎯 Regional station notification sent');
    } catch (error) {
      console.error('Regional station notification error:', error);
    }
  }
}

export default new NotificationService();