import AsyncStorage from '@react-native-async-storage/async-storage';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

class ContentDisclaimerService {
  constructor() {
    this.disclaimerKey = '@kagema_fm_disclaimers_acknowledged';
    this.userAgeKey = '@kagema_fm_user_age';
  }

  /**
   * Get content disclaimers for user's location and content types
   */
  async getContentDisclaimers(countryCode, languageCode = 'en', contentTypes = ['radio_streams', 'music', 'news']) {
    try {
      const response = await fetch(`${BACKEND_URL}/api/compliance/disclaimers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          country_code: countryCode,
          language_code: languageCode,
          content_types: contentTypes
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const disclaimers = await response.json();
      return disclaimers;
    } catch (error) {
      console.error('Error fetching content disclaimers:', error);
      // Return default disclaimer if API fails
      return this.getDefaultDisclaimers(countryCode, languageCode);
    }
  }

  /**
   * Check if user has acknowledged disclaimers for today
   */
  async hasUserAcknowledgedToday(countryCode) {
    try {
      const acknowledgmentData = await AsyncStorage.getItem(this.disclaimerKey);
      if (!acknowledgmentData) return false;

      const { acknowledgedDate, country, disclaimerIds } = JSON.parse(acknowledgmentData);
      const today = new Date().toISOString().split('T')[0];
      
      // Check if acknowledged today for the same country
      return acknowledgedDate === today && country === countryCode && disclaimerIds?.length > 0;
    } catch (error) {
      console.error('Error checking disclaimer acknowledgment:', error);
      return false;
    }
  }

  /**
   * Record user acknowledgment of disclaimers
   */
  async acknowledgeDisclaimers(disclaimers, countryCode, userAge, userId = 'default_user') {
    try {
      const disclaimerIds = disclaimers.content_disclaimers.map(d => d.id);
      const timestamp = new Date().toISOString();
      
      // Store locally
      const acknowledgmentData = {
        acknowledgedDate: new Date().toISOString().split('T')[0],
        country: countryCode,
        disclaimerIds,
        userAge,
        timestamp
      };
      
      await AsyncStorage.setItem(this.disclaimerKey, JSON.stringify(acknowledgmentData));
      await AsyncStorage.setItem(this.userAgeKey, userAge.toString());
      
      // Send to backend
      const response = await fetch(`${BACKEND_URL}/api/compliance/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          disclaimer_ids: disclaimerIds,
          user_id: userId,
          timestamp,
          user_age: userAge,
          country_code: countryCode
        })
      });

      if (!response.ok) {
        console.warn('Failed to record disclaimer acknowledgment on server');
      }

      return true;
    } catch (error) {
      console.error('Error acknowledging disclaimers:', error);
      return false;
    }
  }

  /**
   * Get stored user age
   */
  async getUserAge() {
    try {
      const age = await AsyncStorage.getItem(this.userAgeKey);
      return age ? parseInt(age) : null;
    } catch (error) {
      console.error('Error getting user age:', error);
      return null;
    }
  }

  /**
   * Check content compliance for current user
   */
  async checkContentCompliance(countryCode, contentRating = 'mature', userAge = null, currentHour = null) {
    try {
      if (!userAge) {
        userAge = await this.getUserAge();
      }
      
      if (!currentHour) {
        currentHour = new Date().getHours();
      }

      const response = await fetch(`${BACKEND_URL}/api/compliance/check-content?country_code=${countryCode}&content_rating=${contentRating}&user_age=${userAge}&current_hour=${currentHour}`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking content compliance:', error);
      return {
        compliant: true,
        warnings: [],
        blocking_reasons: [],
        age_appropriate: true,
        time_appropriate: true
      };
    }
  }

  /**
   * Determine country code from coordinates
   */
  getCountryCodeFromLocation(latitude, longitude) {
    // Brazil region check
    if (latitude >= -35 && latitude <= 5 && longitude >= -75 && longitude <= -30) {
      return 'BR';
    }
    // Kenya region check  
    if (latitude >= -5 && latitude <= 5 && longitude >= 33 && longitude <= 42) {
      return 'KE';
    }
    // Default to global
    return 'GLOBAL';
  }

  /**
   * Get default disclaimers when API is unavailable
   */
  getDefaultDisclaimers(countryCode, languageCode) {
    const defaultContent = languageCode.startsWith('pt') ? {
      title: "Aviso de Responsabilidade de Conteúdo",
      content: "AVISO IMPORTANTE: Os apresentadores de rádio e ouvintes são os únicos responsáveis por aderir a todos os regulamentos governamentais aplicáveis sobre conteúdo de transmissão. Esta plataforma de rádio é projetada para ouvintes adultos (18+).\n\nAo usar este serviço, você reconhece que tem idade legal e concorda em cumprir todos os regulamentos de conteúdo aplicáveis.",
      warningContent: "AVISO: Esta transmissão de rádio pode conter linguagem explícita, temas maduros e conteúdo destinado apenas a audiências adultas. Recomenda-se discrição do ouvinte."
    } : {
      title: "Content Responsibility Notice", 
      content: "IMPORTANT DISCLAIMER: Radio hosts and listeners are solely responsible for adhering to all applicable local, regional, and national government regulations regarding broadcast content. This radio platform is designed for adult listeners (18+).\n\nBy using this service, you acknowledge that you are of legal age in your jurisdiction and agree to comply with all applicable content regulations.",
      warningContent: "WARNING: This radio stream may contain explicit language, mature themes, and content intended for adult audiences only. Listener discretion is advised."
    };

    return {
      content_disclaimers: [
        {
          id: "general_responsibility",
          title: defaultContent.title,
          content: defaultContent.content,
          severity: "critical",
          applies_to: ["radio_streams", "music", "news", "general_content"]
        },
        {
          id: "explicit_content_warning",
          title: languageCode.startsWith('pt') ? "Aviso de Conteúdo Explícito" : "Explicit Content Warning",
          content: defaultContent.warningContent,
          severity: "warning", 
          applies_to: ["radio_streams", "music"]
        }
      ],
      regional_compliance: {
        country: countryCode === 'BR' ? 'Brazil' : countryCode === 'KE' ? 'Kenya' : 'Global',
        content_rating_system: countryCode === 'BR' ? 'Classificação Indicativa' : countryCode === 'KE' ? 'Kenya Film Classification Board' : 'Generic',
        adult_age_threshold: 18,
        content_warnings_required: true,
        government_regulations: []
      },
      user_acknowledgment_required: true,
      compliance_version: "1.0",
      last_updated: new Date().toISOString()
    };
  }

  /**
   * Clear all disclaimer acknowledgments (for testing or reset)
   */
  async clearAcknowledgments() {
    try {
      await AsyncStorage.removeItem(this.disclaimerKey);
      await AsyncStorage.removeItem(this.userAgeKey);
      return true;
    } catch (error) {
      console.error('Error clearing acknowledgments:', error);
      return false;
    }
  }

  /**
   * Get disclaimer status for debugging
   */
  async getDisclaimerStatus() {
    try {
      const acknowledgmentData = await AsyncStorage.getItem(this.disclaimerKey);
      const userAge = await AsyncStorage.getItem(this.userAgeKey);
      
      return {
        hasAcknowledgment: !!acknowledgmentData,
        acknowledgmentData: acknowledgmentData ? JSON.parse(acknowledgmentData) : null,
        userAge: userAge ? parseInt(userAge) : null
      };
    } catch (error) {
      console.error('Error getting disclaimer status:', error);
      return { hasAcknowledgment: false, acknowledgmentData: null, userAge: null };
    }
  }
}

export default new ContentDisclaimerService();