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
      title: "Aviso de Responsabilidade de Plataforma e Licenciamento",
      content: "AVISO IMPORTANTE: Kagema FM é apenas uma plataforma de integração e agregação de rádio. Não possuímos, operamos ou transmitimos qualquer conteúdo de rádio.\n\nRESPONSABILIDADE DAS ESTAÇÕES: Cada estação de rádio possui suas próprias licenças de transmissão e responsabilidades de conformidade. As estações são responsáveis por manter licenças adequadas e garantir conformidade com regulamentações locais.\n\nISENÇÃO DA PLATAFORMA: Kagema FM serve apenas como plataforma técnica de integração. Não controlamos ou aprovamos conteúdo das estações e não somos responsáveis por falhas de conformidade.\n\nAo usar este serviço, você reconhece que tem idade legal (18+) e entende que a conformidade é responsabilidade das estações individuais, não da plataforma Kagema FM.",
      warningContent: "AVISO: Esta transmissão pode conter conteúdo maduro. As estações de rádio são responsáveis por todo o conteúdo e conformidade regulamentar."
    } : {
      title: "Platform and Licensing Responsibility Notice", 
      content: "IMPORTANT DISCLAIMER: Kagema FM is a radio integration platform and aggregator service only. We do not own, operate, or broadcast any radio content.\n\nSTATION RESPONSIBILITY: Each radio station holds their own broadcasting licenses and compliance responsibilities. Stations are solely responsible for maintaining proper licenses and ensuring content compliance with local regulations.\n\nPLATFORM DISCLAIMER: Kagema FM serves only as a technical integration platform. We do not control or approve station content and are not liable for station compliance failures.\n\nBy using this service, you acknowledge that you are of legal age (18+) and understand that content compliance is the sole responsibility of individual stations, not the Kagema FM platform.",
      warningContent: "WARNING: This radio stream may contain mature content. Radio stations are responsible for all content and regulatory compliance."
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