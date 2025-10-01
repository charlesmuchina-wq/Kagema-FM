import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Alert,
  Share,
  Linking,
  Platform,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import * as Haptics from 'expo-haptics';
import { captureRef } from 'react-native-view-shot';
import { useRef } from 'react';

interface SocialSharingProps {
  visible: boolean;
  onClose: () => void;
  shareData: {
    type: 'radio_station' | 'news_article' | 'music_track' | 'now_playing';
    title: string;
    description?: string;
    url?: string;
    imageUrl?: string;
    metadata?: any;
  };
}

interface SocialPlatform {
  id: string;
  name: string;
  icon: string;
  color: string;
  action: (data: any) => void;
}

export const SocialSharingManager: React.FC<SocialSharingProps> = ({
  visible,
  onClose,
  shareData,
}) => {
  const { colors, isDark } = useTheme();
  const [isSharing, setIsSharing] = useState(false);
  const shareCardRef = useRef<View>(null);

  const generateShareText = () => {
    switch (shareData.type) {
      case 'radio_station':
        return `🎵 Listening to ${shareData.title} on Kagema FM!\n\n${shareData.description || 'Great international radio station'}\n\n#KagemaFM #Radio #Music`;
      case 'now_playing':
        return `🎧 Now playing on Kagema FM: ${shareData.title}\n\n${shareData.description || 'Check out this amazing track!'}\n\n#KagemaFM #NowPlaying #Music`;
      case 'news_article':
        return `📰 Interesting read: ${shareData.title}\n\n${shareData.description || 'Found this on Kagema FM'}\n\n#KagemaFM #News`;
      case 'music_track':
        return `🎵 Great music discovery: ${shareData.title}\n\n${shareData.description || 'Discovered on Kagema FM'}\n\n#KagemaFM #Music #Discovery`;
      default:
        return `Check out Kagema FM - Your International Radio Experience!\n\n${shareData.title}\n\n#KagemaFM #Radio`;
    }
  };

  const generateShareUrl = () => {
    // In a real app, this would be a deep link or web URL
    const baseUrl = 'https://kagema.fm';
    const params = new URLSearchParams({
      type: shareData.type,
      title: shareData.title,
      utm_source: 'share',
      utm_medium: 'social',
      utm_campaign: 'user_share'
    });
    return `${baseUrl}?${params.toString()}`;
  };

  const shareToNative = async () => {
    try {
      setIsSharing(true);
      const shareText = generateShareText();
      const shareUrl = generateShareUrl();
      
      const result = await Share.share({
        message: Platform.OS === 'ios' ? shareText : `${shareText}\n\n${shareUrl}`,
        url: Platform.OS === 'ios' ? shareUrl : undefined,
        title: shareData.title,
      });

      if (result.action === Share.sharedAction) {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Shared!', 'Thank you for sharing Kagema FM!');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to share. Please try again.');
      console.log('Share error:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const shareToTwitter = () => {
    const text = encodeURIComponent(generateShareText());
    const url = encodeURIComponent(generateShareUrl());
    const twitterUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
    
    Linking.openURL(twitterUrl).catch(() => {
      Alert.alert('Error', 'Unable to open Twitter. Please make sure it\'s installed.');
    });
  };

  const shareToFacebook = () => {
    const url = encodeURIComponent(generateShareUrl());
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    
    Linking.openURL(facebookUrl).catch(() => {
      Alert.alert('Error', 'Unable to open Facebook. Please try again in a browser.');
    });
  };

  const shareToWhatsApp = () => {
    const text = encodeURIComponent(`${generateShareText()}\n\n${generateShareUrl()}`);
    const whatsappUrl = `whatsapp://send?text=${text}`;
    
    Linking.openURL(whatsappUrl).catch(() => {
      // Fallback to web WhatsApp
      const webWhatsAppUrl = `https://web.whatsapp.com/send?text=${text}`;
      Linking.openURL(webWhatsAppUrl).catch(() => {
        Alert.alert('Error', 'Unable to open WhatsApp. Please make sure it\'s installed.');
      });
    });
  };

  const shareToTelegram = () => {
    const text = encodeURIComponent(`${generateShareText()}\n\n${generateShareUrl()}`);
    const telegramUrl = `https://t.me/share/url?url=${generateShareUrl()}&text=${encodeURIComponent(generateShareText())}`;
    
    Linking.openURL(telegramUrl).catch(() => {
      Alert.alert('Error', 'Unable to open Telegram. Please make sure it\'s installed.');
    });
  };

  const shareViaEmail = () => {
    const subject = encodeURIComponent(`Check out ${shareData.title} on Kagema FM`);
    const body = encodeURIComponent(`${generateShareText()}\n\n${generateShareUrl()}`);
    const emailUrl = `mailto:?subject=${subject}&body=${body}`;
    
    Linking.openURL(emailUrl).catch(() => {
      Alert.alert('Error', 'No email client found. Please set up email first.');
    });
  };

  const shareViaSMS = () => {
    const text = encodeURIComponent(`${generateShareText()}\n\n${generateShareUrl()}`);
    const smsUrl = Platform.OS === 'ios' 
      ? `sms:&body=${text}`
      : `sms:?body=${text}`;
    
    Linking.openURL(smsUrl).catch(() => {
      Alert.alert('Error', 'Unable to open messaging app.');
    });
  };

  const copyToClipboard = async () => {
    try {
      const shareText = `${generateShareText()}\n\n${generateShareUrl()}`;
      
      if (Platform.OS === 'web') {
        await navigator.clipboard.writeText(shareText);
      } else {
        // For native platforms, you'd use @react-native-clipboard/clipboard
        console.log('Copy to clipboard:', shareText);
      }
      
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      Alert.alert('Copied!', 'Share text copied to clipboard');
    } catch (error) {
      Alert.alert('Error', 'Failed to copy to clipboard');
    }
  };

  const createShareImage = async () => {
    try {
      setIsSharing(true);
      
      if (!shareCardRef.current) {
        Alert.alert('Error', 'Unable to create share image');
        return;
      }

      // Capture the share card as image
      const uri = await captureRef(shareCardRef.current, {
        format: 'png',
        quality: 0.8,
        width: 400,
        height: 600,
      });
      
      // In a real app, you would save this to camera roll or share it
      Alert.alert(
        'Share Image Created',
        'In a full app, this would save the image to your photo library or allow you to share it directly.',
        [
          { text: 'OK' },
          { 
            text: 'Share', 
            onPress: () => {
              // Share the generated image
              Share.share({
                url: uri,
                message: generateShareText(),
              });
            }
          }
        ]
      );
      
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      Alert.alert('Error', 'Failed to create share image');
      console.log('Share image error:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const socialPlatforms: SocialPlatform[] = [
    {
      id: 'native',
      name: 'Share',
      icon: 'share-outline',
      color: colors.primary,
      action: shareToNative,
    },
    {
      id: 'twitter',
      name: 'Twitter',
      icon: 'logo-twitter',
      color: '#1DA1F2',
      action: shareToTwitter,
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: 'logo-facebook',
      color: '#1877F2',
      action: shareToFacebook,
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: 'logo-whatsapp',
      color: '#25D366',
      action: shareToWhatsApp,
    },
    {
      id: 'telegram',
      name: 'Telegram',
      icon: 'paper-plane',
      color: '#0088cc',
      action: shareToTelegram,
    },
    {
      id: 'email',
      name: 'Email',
      icon: 'mail-outline',
      color: '#EA4335',
      action: shareViaEmail,
    },
    {
      id: 'sms',
      name: 'SMS',
      icon: 'chatbubble-outline',
      color: '#34C759',
      action: shareViaSMS,
    },
    {
      id: 'copy',
      name: 'Copy Link',
      icon: 'copy-outline',
      color: colors.text,
      action: copyToClipboard,
    },
  ];

  const renderShareCard = () => (
    <View ref={shareCardRef} style={[styles.shareCard, { backgroundColor: colors.primary }]}>
      <View style={styles.shareCardHeader}>
        <Image
          source={require('../assets/kagema_fm_international_logo.jpg')}
          style={styles.shareCardLogo}
        />
        <Text style={[styles.shareCardBrand, { color: colors.background }]}>
          Kagema FM
        </Text>
      </View>
      
      <View style={styles.shareCardContent}>
        <Text style={[styles.shareCardTitle, { color: colors.background }]}>
          {shareData.title}
        </Text>
        {shareData.description && (
          <Text style={[styles.shareCardDescription, { color: colors.background, opacity: 0.9 }]}>
            {shareData.description}
          </Text>
        )}
        
        <View style={styles.shareCardFooter}>
          <Text style={[styles.shareCardUrl, { color: colors.background, opacity: 0.8 }]}>
            kagema.fm
          </Text>
          <View style={styles.shareCardType}>
            <Ionicons
              name={shareData.type === 'radio_station' ? 'radio' : 'musical-notes'}
              size={16}
              color={colors.background}
            />
          </View>
        </View>
      </View>
      
      <View style={[styles.shareCardGradient, { backgroundColor: colors.background, opacity: 0.1 }]} />
    </View>
  );

  const styles = StyleSheet.create({
    modalOverlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.5)',
      justifyContent: 'flex-end',
    },
    container: {
      backgroundColor: colors.background,
      borderTopLeftRadius: 20,
      borderTopRightRadius: 20,
      paddingBottom: 40,
      maxHeight: '80%',
    },
    header: {
      padding: 20,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
      textAlign: 'center',
    },
    subtitle: {
      fontSize: 14,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 4,
    },
    closeButton: {
      position: 'absolute',
      top: 20,
      right: 20,
      padding: 4,
    },
    sharePreview: {
      padding: 20,
      alignItems: 'center',
    },
    shareCard: {
      width: 200,
      height: 300,
      borderRadius: 16,
      padding: 20,
      position: 'relative',
      overflow: 'hidden',
    },
    shareCardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 20,
    },
    shareCardLogo: {
      width: 32,
      height: 32,
      borderRadius: 16,
      marginRight: 8,
    },
    shareCardBrand: {
      fontSize: 16,
      fontWeight: '600',
    },
    shareCardContent: {
      flex: 1,
      justifyContent: 'center',
    },
    shareCardTitle: {
      fontSize: 18,
      fontWeight: '600',
      textAlign: 'center',
      marginBottom: 8,
    },
    shareCardDescription: {
      fontSize: 14,
      textAlign: 'center',
      lineHeight: 20,
    },
    shareCardFooter: {
      position: 'absolute',
      bottom: 20,
      left: 20,
      right: 20,
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    shareCardUrl: {
      fontSize: 12,
    },
    shareCardType: {
      width: 24,
      height: 24,
      borderRadius: 12,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'rgba(255,255,255,0.2)',
    },
    shareCardGradient: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
    },
    platformsGrid: {
      padding: 20,
    },
    platformsTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
      marginBottom: 16,
    },
    platformsContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
    },
    platformButton: {
      width: '22%',
      aspectRatio: 1,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 12,
      marginBottom: 16,
      backgroundColor: colors.surface,
    },
    platformIcon: {
      marginBottom: 8,
    },
    platformName: {
      fontSize: 12,
      color: colors.text,
      textAlign: 'center',
    },
    specialActionsContainer: {
      paddingHorizontal: 20,
      paddingBottom: 20,
    },
    specialActionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colors.primary,
      borderRadius: 12,
      paddingVertical: 16,
      marginBottom: 12,
    },
    specialActionText: {
      color: colors.background,
      fontSize: 16,
      fontWeight: '600',
      marginLeft: 8,
    },
    loadingContainer: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.3)',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
    loadingText: {
      color: colors.background,
      marginTop: 8,
    },
  });

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.container}>
          <View style={styles.header}>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color={colors.text} />
            </TouchableOpacity>
            <Text style={styles.title}>Share</Text>
            <Text style={styles.subtitle}>Spread the word about Kagema FM</Text>
          </View>

          <View style={styles.sharePreview}>
            {renderShareCard()}
          </View>

          <View style={styles.platformsGrid}>
            <Text style={styles.platformsTitle}>Share to</Text>
            <View style={styles.platformsContainer}>
              {socialPlatforms.map((platform) => (
                <TouchableOpacity
                  key={platform.id}
                  style={styles.platformButton}
                  onPress={() => {
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                    platform.action(shareData);
                  }}
                  disabled={isSharing}
                >
                  <View style={styles.platformIcon}>
                    <Ionicons
                      name={platform.icon as any}
                      size={28}
                      color={platform.color}
                    />
                  </View>
                  <Text style={styles.platformName}>{platform.name}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.specialActionsContainer}>
            <TouchableOpacity
              style={styles.specialActionButton}
              onPress={createShareImage}
              disabled={isSharing}
            >
              <Ionicons name="image" size={20} color={colors.background} />
              <Text style={styles.specialActionText}>Create Share Image</Text>
            </TouchableOpacity>
          </View>
        </View>

        {isSharing && (
          <View style={styles.loadingContainer}>
            <Ionicons name="share" size={48} color={colors.background} />
            <Text style={styles.loadingText}>Preparing share...</Text>
          </View>
        )}
      </View>
    </Modal>
  );
};

// Utility function to trigger sharing from other components
export const shareContent = (data: {
  type: 'radio_station' | 'news_article' | 'music_track' | 'now_playing';
  title: string;
  description?: string;
  url?: string;
  imageUrl?: string;
  metadata?: any;
}) => {
  // This would typically set state in a parent component to show the modal
  console.log('Share content:', data);
};