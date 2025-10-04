import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

interface PrivacyPolicyContentProps {
  language: string;
  jurisdiction: 'global' | 'us' | 'eu' | 'kenya' | 'brazil';
}

export const PrivacyPolicyContent: React.FC<PrivacyPolicyContentProps> = ({
  language = 'en',
  jurisdiction = 'global'
}) => {
  const { colors } = useTheme();

  const getPrivacyContent = () => {
    const currentDate = new Date().toLocaleDateString();
    
    const content = {
      en: {
        title: 'Privacy Policy',
        lastUpdated: `Last Updated: ${currentDate}`,
        sections: {
          introduction: {
            title: '1. Introduction',
            content: `Kagema FM respects your privacy and is committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information when you use our radio streaming application.

${jurisdiction === 'us' ? '• FCC Compliance: We adhere to Federal Communications Commission regulations regarding broadcast content and user data protection.' : ''}
${jurisdiction === 'eu' ? '• GDPR Compliance: We comply with the General Data Protection Regulation for all EU users.' : ''}
${jurisdiction === 'kenya' ? '• Kenya Data Protection Act: We follow Kenya\'s data protection laws and regulations.' : ''}
${jurisdiction === 'brazil' ? '• LGPD Compliance: We comply with Lei Geral de Proteção de Dados Pessoais (Brazilian Data Protection Law).' : ''}`
          },
          dataCollection: {
            title: '2. Information We Collect',
            content: `• Location Data: We may collect your approximate location to provide regional content and radio stations
• Usage Analytics: Anonymous data about app usage, listening preferences, and feature interactions
• Device Information: Device type, operating system, and technical specifications
• Audio Preferences: Your favorite stations, listening history, and audio settings
• Voice Commands: Processed locally and not stored on our servers (when using voice features)

${jurisdiction === 'eu' ? 'Legal Basis (GDPR): We process data based on legitimate interests, consent, and contract performance.' : ''}
${jurisdiction === 'brazil' ? 'Legal Basis (LGPD): We process data for legitimate interests, consent fulfillment, and service execution.' : ''}`
          },
          dataUse: {
            title: '3. How We Use Your Data',
            content: `• Personalized Content: Recommend radio stations and content based on your location and preferences
• Service Improvement: Analyze usage patterns to enhance app performance and features
• Regional Compliance: Ensure content compliance with local broadcasting regulations
• Customer Support: Respond to user inquiries and provide technical assistance

${jurisdiction === 'us' ? 'FCC Notice: Content recommendations comply with equal time and fairness doctrine requirements.' : ''}
${jurisdiction === 'kenya' ? 'Broadcasting Compliance: Content selection follows Kenya Broadcasting Corporation guidelines.' : ''}`
          },
          dataSharing: {
            title: '4. Data Sharing and Third Parties',
            content: `We do not sell your personal data. Limited sharing occurs with:
• Radio Content Providers: Anonymous listening statistics for content licensing
• Analytics Services: Aggregated, non-identifiable usage data
• Cloud Service Providers: Encrypted data storage and processing
• Legal Authorities: Only when required by law or court order

${jurisdiction === 'eu' ? 'GDPR Rights: You have the right to access, rectify, erase, restrict, and port your data.' : ''}
${jurisdiction === 'brazil' ? 'LGPD Rights: You have rights to confirmation, access, correction, anonymization, and deletion of your data.' : ''}`
          },
          userRights: {
            title: '5. Your Privacy Rights',
            content: `You have the following rights regarding your personal data:
• Access: Request copies of your personal data
• Correction: Request correction of inaccurate or incomplete data  
• Deletion: Request deletion of your personal data
• Restriction: Request restriction of processing
• Objection: Object to processing based on legitimate interests
• Portability: Request transfer of your data to another service

${jurisdiction === 'eu' ? 'To exercise GDPR rights, contact our Data Protection Officer at privacy@kagemafm.com' : ''}
${jurisdiction === 'kenya' ? 'To exercise rights under Kenya Data Protection Act, contact us at privacy@kagemafm.com' : ''}
${jurisdiction === 'brazil' ? 'To exercise LGPD rights, contact our Data Protection Officer at privacy@kagemafm.com' : ''}`
          },
          dataSecurity: {
            title: '6. Data Security',
            content: `We implement industry-standard security measures:
• End-to-end encryption for data transmission
• Secure cloud storage with access controls
• Regular security audits and vulnerability assessments
• Employee training on data protection best practices
• Incident response procedures for data breaches

${jurisdiction === 'eu' ? 'GDPR Breach Notification: We will notify authorities within 72 hours of any data breach.' : ''}
${jurisdiction === 'brazil' ? 'LGPD Breach Notification: We follow Brazilian authority notification requirements for data incidents.' : ''}`
          },
          contact: {
            title: '7. Contact Information',
            content: `For privacy-related inquiries:
• Email: privacy@kagemafm.com
• Address: Kagema FM Privacy Office
• Phone: +254-XXX-XXXX (Kenya) | +55-XXX-XXXX (Brazil)

${jurisdiction === 'eu' ? 'EU Representative: European Privacy Office, privacy-eu@kagemafm.com' : ''}
${jurisdiction === 'us' ? 'FCC Compliance Officer: fcc-compliance@kagemafm.com' : ''}`
          }
        }
      },
      sw: {
        title: 'Sera ya Faragha',
        lastUpdated: `Imesasishwa Mwisho: ${currentDate}`,
        sections: {
          introduction: {
            title: '1. Utangulizi',
            content: 'Kagema FM inaheshimu faragha yako na imejitolea kulinda data yako ya kibinafsi. Sera hii ya faragha inaeleza jinsi tunavyokusanya, kutumia, na kulinda maelezo yako unapotumia programu yetu ya kusikiliza redio.'
          },
          dataCollection: {
            title: '2. Maelezo Tunayokusanya',
            content: '• Data ya Mahali: Tunaweza kukusanya mahali pako pa karibu kutoa maudhui ya kikanda na vituo vya redio\n• Takwimu za Matumizi: Data isiyo ya kitambulisho kuhusu matumizi ya programu\n• Maelezo ya Kifaa: Aina ya kifaa, mfumo wa uendeshaji, na vipimo vya kiufundi'
          },
          // Add more Swahili translations as needed
          contact: {
            title: '7. Maelezo ya Mawasiliano',
            content: 'Kwa maswali yanayohusiana na faragha:\n• Barua pepe: privacy@kagemafm.com\n• Anwani: Kagema FM Privacy Office\n• Simu: +254-XXX-XXXX'
          }
        }
      },
      pt: {
        title: 'Política de Privacidade',
        lastUpdated: `Última Atualização: ${currentDate}`,
        sections: {
          introduction: {
            title: '1. Introdução',
            content: 'A Kagema FM respeita sua privacidade e está comprometida em proteger seus dados pessoais. Esta política de privacidade explica como coletamos, usamos e protegemos suas informações quando você usa nosso aplicativo de streaming de rádio.'
          },
          dataCollection: {
            title: '2. Informações que Coletamos',
            content: '• Dados de Localização: Podemos coletar sua localização aproximada para fornecer conteúdo regional e estações de rádio\n• Análises de Uso: Dados anônimos sobre uso do aplicativo\n• Informações do Dispositivo: Tipo de dispositivo, sistema operacional e especificações técnicas'
          },
          userRights: {
            title: '5. Seus Direitos de Privacidade (LGPD)',
            content: 'Você tem os seguintes direitos sobre seus dados pessoais:\n• Confirmação da existência de tratamento\n• Acesso aos dados\n• Correção de dados incompletos ou inexatos\n• Anonimização, bloqueio ou eliminação\n• Portabilidade dos dados'
          },
          contact: {
            title: '7. Informações de Contato',
            content: 'Para consultas relacionadas à privacidade:\n• Email: privacy@kagemafm.com\n• Endereço: Kagema FM Privacy Office\n• Telefone: +55-XXX-XXXX (Brasil)'
          }
        }
      }
    };

    return content[language as keyof typeof content] || content.en;
  };

  const content = getPrivacyContent();

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      padding: 16,
    },
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
      marginBottom: 8,
      textAlign: 'center',
    },
    lastUpdated: {
      fontSize: 12,
      color: colors.textSecondary,
      textAlign: 'center',
      marginBottom: 24,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      marginTop: 20,
      marginBottom: 12,
    },
    sectionContent: {
      fontSize: 14,
      color: colors.text,
      lineHeight: 20,
      marginBottom: 16,
    },
    jurisdictionBadge: {
      backgroundColor: colors.primary,
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 16,
      alignSelf: 'flex-start',
      marginBottom: 16,
    },
    jurisdictionText: {
      color: colors.background,
      fontSize: 12,
      fontWeight: '600',
    }
  });

  const getJurisdictionLabel = () => {
    const labels = {
      us: 'FCC Compliant',
      eu: 'GDPR Compliant', 
      kenya: 'Kenya DPA Compliant',
      brazil: 'LGPD Compliant',
      global: 'Global Privacy Standards'
    };
    return labels[jurisdiction];
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>{content.title}</Text>
      <Text style={styles.lastUpdated}>{content.lastUpdated}</Text>
      
      <View style={styles.jurisdictionBadge}>
        <Text style={styles.jurisdictionText}>{getJurisdictionLabel()}</Text>
      </View>

      {Object.entries(content.sections).map(([key, section]) => (
        <View key={key}>
          <Text style={styles.sectionTitle}>{section.title}</Text>
          <Text style={styles.sectionContent}>{section.content}</Text>
        </View>
      ))}
    </ScrollView>
  );
};