import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Animated,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width, height } = Dimensions.get('window');

const WelcomePage = () => {
  const [currentFeature, setCurrentFeature] = useState(0);
  const fadeAnim = new Animated.Value(0);
  const slideAnim = new Animated.Value(50);

  useEffect(() => {
    // Animate welcome screen
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      })
    ]).start();

    // Auto-rotate features
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: 'radio-outline',
      title: 'Live Radio Streaming',
      description: 'Access international radio stations with crystal-clear quality and real-time streaming.',
      color: '#FF6B6B'
    },
    {
      icon: 'mic-outline',
      title: 'Voice Commands',
      description: 'Control your radio experience hands-free with intelligent voice recognition.',
      color: '#4ECDC4'
    },
    {
      icon: 'location-outline',
      title: 'Regional Content',
      description: 'Discover local stations and content based on your geographic location.',
      color: '#45B7D1'
    },
    {
      icon: 'car-outline',
      title: 'Car Mode',
      description: 'Automotive-optimized interface with large controls for safe driving.',
      color: '#F7DC6F'
    },
    {
      icon: 'cloud-offline-outline',
      title: 'Offline Mode',
      description: 'Download and enjoy content even when you\'re not connected to the internet.',
      color: '#BB8FCE'
    },
    {
      icon: 'globe-outline',
      title: 'Multi-language Support',
      description: 'Available in multiple languages including English, Swahili, and Portuguese.',
      color: '#82E0AA'
    }
  ];

  const handleGetStarted = () => {
    router.push('/');
  };

  const handleLearnMore = () => {
    router.push('/?tab=settings'); // Navigate to settings tab to show features
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: '#000',
    },
    gradientBackground: {
      flex: 1,
    },
    scrollContainer: {
      flexGrow: 1,
    },
    logoSection: {
      alignItems: 'center',
      paddingTop: 60,
      paddingBottom: 40,
      paddingHorizontal: 20,
    },
    logo: {
      width: 120,
      height: 120,
      borderRadius: 60,
      backgroundColor: '#FF6B6B',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 20,
      shadowColor: '#FF6B6B',
      shadowOffset: {
        width: 0,
        height: 10,
      },
      shadowOpacity: 0.3,
      shadowRadius: 20,
      elevation: 10,
    },
    appTitle: {
      fontSize: 32,
      fontWeight: 'bold',
      color: '#FFFFFF',
      textAlign: 'center',
      marginBottom: 8,
    },
    appSubtitle: {
      fontSize: 18,
      color: '#B0B0B0',
      textAlign: 'center',
      fontWeight: '300',
    },
    tagline: {
      fontSize: 16,
      color: '#FF6B6B',
      textAlign: 'center',
      fontStyle: 'italic',
      marginTop: 8,
    },
    featuresSection: {
      paddingHorizontal: 20,
      paddingVertical: 40,
    },
    sectionTitle: {
      fontSize: 24,
      fontWeight: '600',
      color: '#FFFFFF',
      textAlign: 'center',
      marginBottom: 30,
    },
    featureCarousel: {
      height: 280,
      marginBottom: 30,
    },
    featureCard: {
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
      borderRadius: 20,
      padding: 30,
      alignItems: 'center',
      justifyContent: 'center',
      marginHorizontal: 10,
      borderWidth: 1,
      borderColor: 'rgba(255, 255, 255, 0.2)',
      backdropFilter: 'blur(10px)',
    },
    featureIcon: {
      width: 80,
      height: 80,
      borderRadius: 40,
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 20,
    },
    featureTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: '#FFFFFF',
      textAlign: 'center',
      marginBottom: 12,
    },
    featureDescription: {
      fontSize: 14,
      color: '#B0B0B0',
      textAlign: 'center',
      lineHeight: 20,
    },
    indicatorContainer: {
      flexDirection: 'row',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 20,
    },
    indicator: {
      width: 8,
      height: 8,
      borderRadius: 4,
      backgroundColor: 'rgba(255, 255, 255, 0.3)',
      marginHorizontal: 4,
    },
    activeIndicator: {
      backgroundColor: '#FF6B6B',
      width: 24,
    },
    statsSection: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      paddingHorizontal: 40,
      paddingVertical: 30,
    },
    statItem: {
      alignItems: 'center',
    },
    statNumber: {
      fontSize: 28,
      fontWeight: 'bold',
      color: '#FF6B6B',
      marginBottom: 4,
    },
    statLabel: {
      fontSize: 12,
      color: '#B0B0B0',
      textAlign: 'center',
    },
    ctaSection: {
      paddingHorizontal: 30,
      paddingVertical: 40,
      alignItems: 'center',
    },
    ctaTitle: {
      fontSize: 22,
      fontWeight: '600',
      color: '#FFFFFF',
      textAlign: 'center',
      marginBottom: 8,
    },
    ctaSubtitle: {
      fontSize: 14,
      color: '#B0B0B0',
      textAlign: 'center',
      marginBottom: 30,
      lineHeight: 20,
    },
    buttonContainer: {
      width: '100%',
    },
    primaryButton: {
      backgroundColor: '#FF6B6B',
      borderRadius: 25,
      paddingVertical: 16,
      paddingHorizontal: 40,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: 15,
      shadowColor: '#FF6B6B',
      shadowOffset: {
        width: 0,
        height: 5,
      },
      shadowOpacity: 0.3,
      shadowRadius: 10,
      elevation: 5,
    },
    secondaryButton: {
      backgroundColor: 'transparent',
      borderRadius: 25,
      paddingVertical: 16,
      paddingHorizontal: 40,
      borderWidth: 1.5,
      borderColor: '#FFFFFF',
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonText: {
      fontSize: 16,
      fontWeight: '600',
      marginLeft: 8,
    },
    primaryButtonText: {
      color: '#FFFFFF',
    },
    secondaryButtonText: {
      color: '#FFFFFF',
    },
    footer: {
      paddingHorizontal: 20,
      paddingVertical: 20,
      alignItems: 'center',
      borderTopWidth: 1,
      borderTopColor: 'rgba(255, 255, 255, 0.1)',
    },
    footerText: {
      fontSize: 12,
      color: '#666',
      textAlign: 'center',
      lineHeight: 18,
    },
    privacyLink: {
      color: '#FF6B6B',
      textDecorationLine: 'underline',
    }
  });

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <LinearGradient
        colors={['#000000', '#1a1a1a', '#2d1b32', '#000000']}
        locations={[0, 0.3, 0.7, 1]}
        style={styles.gradientBackground}
      >
        <ScrollView
          style={styles.scrollContainer}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 20 }}
        >
          {/* Logo and Title Section */}
          <Animated.View 
            style={[
              styles.logoSection,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }]
              }
            ]}
          >
            <View style={styles.logo}>
              <Ionicons name="radio" size={60} color="#FFFFFF" />
            </View>
            <Text style={styles.appTitle}>Kagema FM</Text>
            <Text style={styles.appSubtitle}>Enhanced</Text>
            <Text style={styles.tagline}>Your Complete Radio Experience</Text>
          </Animated.View>

          {/* Features Carousel */}
          <View style={styles.featuresSection}>
            <Text style={styles.sectionTitle}>Discover Amazing Features</Text>
            
            <View style={styles.featureCarousel}>
              <Animated.View style={[styles.featureCard, { opacity: fadeAnim }]}>
                <View style={[styles.featureIcon, { backgroundColor: features[currentFeature].color + '40' }]}>
                  <Ionicons 
                    name={features[currentFeature].icon as any} 
                    size={40} 
                    color={features[currentFeature].color} 
                  />
                </View>
                <Text style={styles.featureTitle}>{features[currentFeature].title}</Text>
                <Text style={styles.featureDescription}>{features[currentFeature].description}</Text>
              </Animated.View>
            </View>

            {/* Feature Indicators */}
            <View style={styles.indicatorContainer}>
              {features.map((_, index) => (
                <TouchableOpacity 
                  key={index}
                  onPress={() => setCurrentFeature(index)}
                >
                  <View 
                    style={[
                      styles.indicator,
                      index === currentFeature && styles.activeIndicator
                    ]} 
                  />
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Stats Section */}
          <View style={styles.statsSection}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>1000+</Text>
              <Text style={styles.statLabel}>Radio Stations</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>50+</Text>
              <Text style={styles.statLabel}>Countries</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>24/7</Text>
              <Text style={styles.statLabel}>Live Streaming</Text>
            </View>
          </View>

          {/* Call to Action */}
          <Animated.View 
            style={[
              styles.ctaSection,
              { opacity: fadeAnim }
            ]}
          >
            <Text style={styles.ctaTitle}>Ready to Start Listening?</Text>
            <Text style={styles.ctaSubtitle}>
              Join thousands of users worldwide enjoying premium radio streaming with advanced features and personalized content.
            </Text>
            
            <View style={styles.buttonContainer}>
              <TouchableOpacity style={styles.primaryButton} onPress={handleGetStarted}>
                <Ionicons name="play-circle" size={24} color="#FFFFFF" />
                <Text style={[styles.buttonText, styles.primaryButtonText]}>
                  Get Started
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.secondaryButton} onPress={handleLearnMore}>
                <Ionicons name="information-circle-outline" size={24} color="#FFFFFF" />
                <Text style={[styles.buttonText, styles.secondaryButtonText]}>
                  Learn More
                </Text>
              </TouchableOpacity>
            </View>
          </Animated.View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              By continuing, you agree to our{' '}
              <Text style={styles.privacyLink}>Terms of Service</Text>{' '}
              and{' '}
              <Text style={styles.privacyLink}>Privacy Policy</Text>
              {'\n\n'}
              © 2024 Kagema FM. All rights reserved.
              {'\n'}
              Compliant with FCC, GDPR, Kenya DPA & LGPD regulations.
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
};

export default WelcomePage;