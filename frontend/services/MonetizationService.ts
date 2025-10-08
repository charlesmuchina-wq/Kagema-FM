import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// Mock interfaces for AdMob (would be replaced with actual expo-ads-admob)
interface AdMobBannerConfig {
  adUnitId: string;
  size: 'banner' | 'largeBanner' | 'mediumRectangle' | 'fullBanner' | 'leaderboard' | 'smartBanner';
  position: 'top' | 'bottom';
}

interface AdMobInterstitialConfig {
  adUnitId: string;
  testDevices?: string[];
}

interface AdMobRewardedConfig {
  adUnitId: string;
  reward: {
    type: string;
    amount: number;
  };
}

// In-App Purchase interfaces
interface PurchaseProduct {
  id: string;
  title: string;
  description: string;
  price: string;
  type: 'consumable' | 'non-consumable' | 'subscription';
  features: string[];
}

interface SubscriptionPlan {
  id: string;
  name: string;
  price: string;
  duration: 'monthly' | 'yearly';
  features: string[];
  savings?: string;
}

interface MonetizationState {
  isPremium: boolean;
  subscriptionPlan: SubscriptionPlan | null;
  adFreeTrial: boolean;
  adsEnabled: boolean;
  purchaseHistory: string[];
  subscriptionExpiry: number | null;
}

export class MonetizationService {
  private listeners: Set<(state: MonetizationState) => void> = new Set();
  private currentState: MonetizationState = {
    isPremium: false,
    subscriptionPlan: null,
    adFreeTrial: false,
    adsEnabled: true,
    purchaseHistory: [],
    subscriptionExpiry: null
  };

  // AdMob configuration
  private adMobConfig = {
    banner: {
      ios: 'ca-app-pub-3940256099942544/2934735716', // Test ID
      android: 'ca-app-pub-3940256099942544/6300978111', // Test ID
    },
    interstitial: {
      ios: 'ca-app-pub-3940256099942544/4411468910', // Test ID
      android: 'ca-app-pub-3940256099942544/1033173712', // Test ID
    },
    rewarded: {
      ios: 'ca-app-pub-3940256099942544/1712485313', // Test ID
      android: 'ca-app-pub-3940256099942544/5224354917', // Test ID
    }
  };

  // Available products and subscriptions
  public readonly products: PurchaseProduct[] = [
    {
      id: 'kagema_premium_monthly',
      title: 'Kagema FM Premium (Monthly)',
      description: 'Remove ads, unlock sleep timer, and access premium stations',
      price: '$4.99',
      type: 'subscription',
      features: [
        'Ad-free listening experience',
        'Advanced sleep timer with fade-out',
        'Premium radio stations',
        'Unlimited station favorites',
        'High-quality audio streaming',
        'Lock screen controls'
      ]
    },
    {
      id: 'kagema_premium_yearly',
      title: 'Kagema FM Premium (Yearly)',
      description: 'Best value! All premium features for a full year',
      price: '$49.99',
      type: 'subscription',
      features: [
        'All monthly premium features',
        '2 months FREE (save $10)',
        'Priority customer support',
        'Early access to new features',
        'Exclusive premium content',
        'Cross-device sync'
      ]
    },
    {
      id: 'remove_ads',
      title: 'Remove Ads',
      description: 'Enjoy uninterrupted listening without advertisements',
      price: '$2.99',
      type: 'non-consumable',
      features: [
        'Remove all banner ads',
        'Remove all interstitial ads',
        'Uninterrupted radio streaming'
      ]
    },
    {
      id: 'premium_stations_pack',
      title: 'Premium Stations Pack',
      description: 'Access to exclusive high-quality radio stations',
      price: '$1.99',
      type: 'non-consumable',
      features: [
        'Access to 50+ premium stations',
        'HD audio quality',
        'Exclusive music channels'
      ]
    }
  ];

  public readonly subscriptionPlans: SubscriptionPlan[] = [
    {
      id: 'kagema_premium_monthly',
      name: 'Monthly Premium',
      price: '$4.99/month',
      duration: 'monthly',
      features: [
        'Ad-free experience',
        'Sleep timer',
        'Premium stations',
        'HD audio quality'
      ]
    },
    {
      id: 'kagema_premium_yearly', 
      name: 'Yearly Premium',
      price: '$49.99/year',
      duration: 'yearly',
      savings: 'Save $10',
      features: [
        'All monthly features',
        '2 months FREE',
        'Priority support',
        'Early access features'
      ]
    }
  ];

  constructor() {
    this.initializeMonetization();
  }

  private async initializeMonetization(): Promise<void> {
    try {
      // Load saved monetization state
      await this.loadMonetizationState();
      
      // Initialize AdMob (mock implementation)
      await this.initializeAdMob();
      
      // Initialize In-App Purchases (mock implementation)
      await this.initializeIAP();
      
      // Check subscription status
      await this.checkSubscriptionStatus();
      
      console.log('💰 Monetization service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize monetization service:', error);
    }
  }

  private async loadMonetizationState(): Promise<void> {
    try {
      const savedState = await AsyncStorage.getItem('monetizationState');
      if (savedState) {
        const state = JSON.parse(savedState);
        this.currentState = { ...this.currentState, ...state };
        console.log('💾 Loaded monetization state:', this.currentState);
      }
    } catch (error) {
      console.error('❌ Failed to load monetization state:', error);
    }
  }

  private async saveMonetizationState(): Promise<void> {
    try {
      await AsyncStorage.setItem('monetizationState', JSON.stringify(this.currentState));
    } catch (error) {
      console.error('❌ Failed to save monetization state:', error);
    }
  }

  private async initializeAdMob(): Promise<void> {
    try {
      // Mock AdMob initialization
      console.log('📱 Initializing AdMob...');
      
      // In real implementation, would do:
      // await AdMob.setRequestConfiguration({
      //   debugGeography: AdMob.DebugGeography.EEA,
      //   maxAdContentRating: AdMob.MaxAdContentRating.PG,
      //   tagForChildDirectedTreatment: false,
      //   tagForUnderAgeOfConsent: false,
      //   testDeviceIdentifiers: ['EMULATOR'],
      // });
      
      console.log('✅ AdMob initialized');
    } catch (error) {
      console.error('❌ AdMob initialization failed:', error);
    }
  }

  private async initializeIAP(): Promise<void> {
    try {
      // Mock In-App Purchase initialization
      console.log('💳 Initializing In-App Purchases...');
      
      // In real implementation, would do:
      // await InAppPurchases.connectAsync();
      // const products = await InAppPurchases.getProductsAsync(this.products.map(p => p.id));
      
      console.log('✅ In-App Purchases initialized');
    } catch (error) {
      console.error('❌ IAP initialization failed:', error);
    }
  }

  private async checkSubscriptionStatus(): Promise<void> {
    try {
      // Check if user has active subscription
      if (this.currentState.subscriptionExpiry) {
        const now = Date.now();
        if (now > this.currentState.subscriptionExpiry) {
          // Subscription expired
          this.currentState.isPremium = false;
          this.currentState.subscriptionPlan = null;
          this.currentState.subscriptionExpiry = null;
          await this.saveMonetizationState();
          
          console.log('⏰ Subscription expired');
        } else {
          console.log('✅ Active subscription found');
        }
      }

      // Check trial status
      await this.checkTrialStatus();
    } catch (error) {
      console.error('❌ Failed to check subscription status:', error);
    }
  }

  private async checkTrialStatus(): Promise<void> {
    try {
      const trialStart = await AsyncStorage.getItem('trialStartDate');
      if (trialStart) {
        const startDate = parseInt(trialStart);
        const now = Date.now();
        const trialDuration = 7 * 24 * 60 * 60 * 1000; // 7 days

        if (now - startDate < trialDuration) {
          this.currentState.adFreeTrial = true;
          this.currentState.adsEnabled = false;
        } else {
          this.currentState.adFreeTrial = false;
          this.currentState.adsEnabled = !this.currentState.isPremium;
        }
      }
    } catch (error) {
      console.error('❌ Failed to check trial status:', error);
    }
  }

  /**
   * Start free trial
   */
  async startFreeTrial(): Promise<boolean> {
    try {
      const trialStart = await AsyncStorage.getItem('trialStartDate');
      if (trialStart) {
        console.log('⚠️ Trial already started');
        return false;
      }

      await AsyncStorage.setItem('trialStartDate', Date.now().toString());
      this.currentState.adFreeTrial = true;
      this.currentState.adsEnabled = false;
      
      await this.saveMonetizationState();
      this.notifyListeners();
      
      console.log('🎉 Free trial started');
      return true;
    } catch (error) {
      console.error('❌ Failed to start trial:', error);
      return false;
    }
  }

  /**
   * Show banner ad
   */
  async showBannerAd(config: Partial<AdMobBannerConfig> = {}): Promise<boolean> {
    if (!this.shouldShowAds()) {
      console.log('🚫 Ads disabled for premium user');
      return false;
    }

    try {
      const adUnitId = Platform.OS === 'ios' 
        ? this.adMobConfig.banner.ios 
        : this.adMobConfig.banner.android;

      const bannerConfig: AdMobBannerConfig = {
        adUnitId,
        size: 'banner',
        position: 'bottom',
        ...config
      };

      // Mock banner ad display
      console.log('📱 Showing banner ad:', bannerConfig);
      
      // In real implementation:
      // await AdMobBanner.setAdUnitID(bannerConfig.adUnitId);
      // await AdMobBanner.requestAdAsync();
      
      return true;
    } catch (error) {
      console.error('❌ Failed to show banner ad:', error);
      return false;
    }
  }

  /**
   * Show interstitial ad
   */
  async showInterstitialAd(): Promise<boolean> {
    if (!this.shouldShowAds()) {
      console.log('🚫 Ads disabled for premium user');
      return false;
    }

    try {
      const adUnitId = Platform.OS === 'ios' 
        ? this.adMobConfig.interstitial.ios 
        : this.adMobConfig.interstitial.android;

      // Mock interstitial ad display
      console.log('📱 Showing interstitial ad');
      
      // In real implementation:
      // await AdMobInterstitial.setAdUnitID(adUnitId);
      // await AdMobInterstitial.requestAdAsync();
      // await AdMobInterstitial.showAdAsync();
      
      return true;
    } catch (error) {
      console.error('❌ Failed to show interstitial ad:', error);
      return false;
    }
  }

  /**
   * Show rewarded ad
   */
  async showRewardedAd(): Promise<{ success: boolean; reward?: any }> {
    try {
      const adUnitId = Platform.OS === 'ios' 
        ? this.adMobConfig.rewarded.ios 
        : this.adMobConfig.rewarded.android;

      // Mock rewarded ad display
      console.log('🎁 Showing rewarded ad');
      
      // In real implementation:
      // await AdMobRewarded.setAdUnitID(adUnitId);
      // await AdMobRewarded.requestAdAsync();
      // const result = await AdMobRewarded.showAdAsync();
      
      // Mock reward
      return {
        success: true,
        reward: { type: 'ad_free_time', amount: 30 } // 30 minutes ad-free
      };
    } catch (error) {
      console.error('❌ Failed to show rewarded ad:', error);
      return { success: false };
    }
  }

  /**
   * Purchase product
   */
  async purchaseProduct(productId: string): Promise<{ success: boolean; transaction?: any }> {
    try {
      const product = this.products.find(p => p.id === productId);
      if (!product) {
        console.error('❌ Product not found:', productId);
        return { success: false };
      }

      // Mock purchase process
      console.log('💳 Processing purchase:', product.title);
      
      // In real implementation:
      // const result = await InAppPurchases.purchaseItemAsync(productId);
      
      // Mock successful purchase
      this.currentState.purchaseHistory.push(productId);
      
      if (product.type === 'subscription') {
        await this.activateSubscription(productId);
      } else if (productId === 'remove_ads') {
        this.currentState.adsEnabled = false;
      }
      
      await this.saveMonetizationState();
      this.notifyListeners();
      
      console.log('✅ Purchase completed:', productId);
      return { success: true };
    } catch (error) {
      console.error('❌ Purchase failed:', error);
      return { success: false };
    }
  }

  /**
   * Restore purchases
   */
  async restorePurchases(): Promise<boolean> {
    try {
      console.log('🔄 Restoring purchases...');
      
      // Mock restore process
      // In real implementation:
      // const history = await InAppPurchases.getPurchaseHistoryAsync();
      
      console.log('✅ Purchases restored');
      return true;
    } catch (error) {
      console.error('❌ Failed to restore purchases:', error);
      return false;
    }
  }

  private async activateSubscription(subscriptionId: string): Promise<void> {
    const plan = this.subscriptionPlans.find(p => p.id === subscriptionId);
    if (!plan) return;

    this.currentState.isPremium = true;
    this.currentState.subscriptionPlan = plan;
    this.currentState.adsEnabled = false;
    
    // Set expiry date
    const now = Date.now();
    const duration = plan.duration === 'monthly' 
      ? 30 * 24 * 60 * 60 * 1000  // 30 days
      : 365 * 24 * 60 * 60 * 1000; // 365 days
    
    this.currentState.subscriptionExpiry = now + duration;
  }

  /**
   * Check if ads should be shown
   */
  shouldShowAds(): boolean {
    return this.currentState.adsEnabled && 
           !this.currentState.isPremium && 
           !this.currentState.adFreeTrial;
  }

  /**
   * Get current monetization state
   */
  getState(): MonetizationState {
    return { ...this.currentState };
  }

  /**
   * Check if user has premium access
   */
  isPremium(): boolean {
    return this.currentState.isPremium || this.currentState.adFreeTrial;
  }

  /**
   * Get days remaining in subscription/trial
   */
  getDaysRemaining(): number {
    const expiry = this.currentState.subscriptionExpiry;
    if (!expiry) return 0;
    
    const now = Date.now();
    const remaining = expiry - now;
    return Math.max(0, Math.ceil(remaining / (24 * 60 * 60 * 1000)));
  }

  /**
   * Add monetization state listener
   */
  addListener(callback: (state: MonetizationState) => void): () => void {
    this.listeners.add(callback);
    
    return () => {
      this.listeners.delete(callback);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(callback => {
      try {
        callback({ ...this.currentState });
      } catch (error) {
        console.error('❌ Monetization listener error:', error);
      }
    });
  }

  /**
   * Clean up resources
   */
  async cleanup(): Promise<void> {
    try {
      this.listeners.clear();
      
      // In real implementation:
      // await InAppPurchases.disconnectAsync();
      
      console.log('🧹 Monetization service cleaned up');
    } catch (error) {
      console.error('❌ Monetization cleanup error:', error);
    }
  }
}

// Export singleton instance
export const monetizationService = new MonetizationService();
export default MonetizationService;