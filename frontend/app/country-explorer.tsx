import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
  FlatList,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import Constants from 'expo-constants';

const { width, height } = Dimensions.get('window');

// ISO Region mapping for continents
const CONTINENTS = {
  africa: { name: 'Africa', color: '#FF6B6B', code: 'AF' },
  asia: { name: 'Asia', color: '#4ECDC4', code: 'AS' },
  europe: { name: 'Europe', color: '#45B7D1', code: 'EU' },
  north_america: { name: 'North America', color: '#96CEB4', code: 'NA' },
  south_america: { name: 'South America', color: '#FFEAA7', code: 'SA' },
  oceania: { name: 'Oceania', color: '#DFE6E9', code: 'OC' },
};

// Country ISO codes by continent
const COUNTRY_REGIONS = {
  AF: ['DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN', 'UG', 'ZM', 'ZW'],
  AS: ['AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'GE', 'IN', 'ID', 'IR', 'IQ', 'IL', 'JP', 'JO', 'KZ', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV', 'MN', 'MM', 'NP', 'KP', 'OM', 'PK', 'PH', 'QA', 'SA', 'SG', 'KR', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TL', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE'],
  EU: ['AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'XK', 'LV', 'LI', 'LT', 'LU', 'MK', 'MT', 'MD', 'MC', 'ME', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'UA', 'GB'],
  NA: ['AG', 'BS', 'BB', 'BZ', 'CA', 'CR', 'CU', 'DM', 'DO', 'SV', 'GD', 'GT', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'KN', 'LC', 'VC', 'TT', 'US'],
  SA: ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE'],
  OC: ['AU', 'FJ', 'KI', 'MH', 'FM', 'NR', 'NZ', 'PW', 'PG', 'WS', 'SB', 'TO', 'TV', 'VU'],
};

// Country names mapping
const COUNTRY_NAMES: { [key: string]: string } = {
  DZ: 'Algeria', AO: 'Angola', BJ: 'Benin', BW: 'Botswana', BF: 'Burkina Faso',
  BI: 'Burundi', CM: 'Cameroon', CV: 'Cape Verde', CF: 'Central African Republic',
  TD: 'Chad', KM: 'Comoros', CG: 'Congo', CD: 'DR Congo', CI: 'Ivory Coast',
  DJ: 'Djibouti', EG: 'Egypt', GQ: 'Equatorial Guinea', ER: 'Eritrea', ET: 'Ethiopia',
  GA: 'Gabon', GM: 'Gambia', GH: 'Ghana', GN: 'Guinea', GW: 'Guinea-Bissau',
  KE: 'Kenya', LS: 'Lesotho', LR: 'Liberia', LY: 'Libya', MG: 'Madagascar',
  MW: 'Malawi', ML: 'Mali', MR: 'Mauritania', MU: 'Mauritius', MA: 'Morocco',
  MZ: 'Mozambique', NA: 'Namibia', NE: 'Niger', NG: 'Nigeria', RW: 'Rwanda',
  ST: 'Sao Tome', SN: 'Senegal', SC: 'Seychelles', SL: 'Sierra Leone', SO: 'Somalia',
  ZA: 'South Africa', SS: 'South Sudan', SD: 'Sudan', SZ: 'Eswatini', TZ: 'Tanzania',
  TG: 'Togo', TN: 'Tunisia', UG: 'Uganda', ZM: 'Zambia', ZW: 'Zimbabwe',
  AF: 'Afghanistan', AM: 'Armenia', AZ: 'Azerbaijan', BH: 'Bahrain', BD: 'Bangladesh',
  BT: 'Bhutan', BN: 'Brunei', KH: 'Cambodia', CN: 'China', GE: 'Georgia',
  IN: 'India', ID: 'Indonesia', IR: 'Iran', IQ: 'Iraq', IL: 'Israel',
  JP: 'Japan', JO: 'Jordan', KZ: 'Kazakhstan', KW: 'Kuwait', KG: 'Kyrgyzstan',
  LA: 'Laos', LB: 'Lebanon', MY: 'Malaysia', MV: 'Maldives', MN: 'Mongolia',
  MM: 'Myanmar', NP: 'Nepal', KP: 'North Korea', OM: 'Oman', PK: 'Pakistan',
  PH: 'Philippines', QA: 'Qatar', SA: 'Saudi Arabia', SG: 'Singapore', KR: 'South Korea',
  LK: 'Sri Lanka', SY: 'Syria', TW: 'Taiwan', TJ: 'Tajikistan', TH: 'Thailand',
  TL: 'Timor-Leste', TR: 'Turkey', TM: 'Turkmenistan', AE: 'UAE', UZ: 'Uzbekistan',
  VN: 'Vietnam', YE: 'Yemen', AL: 'Albania', AD: 'Andorra', AT: 'Austria',
  BY: 'Belarus', BE: 'Belgium', BA: 'Bosnia', BG: 'Bulgaria', HR: 'Croatia',
  CY: 'Cyprus', CZ: 'Czech Republic', DK: 'Denmark', EE: 'Estonia', FI: 'Finland',
  FR: 'France', DE: 'Germany', GR: 'Greece', HU: 'Hungary', IS: 'Iceland',
  IE: 'Ireland', IT: 'Italy', XK: 'Kosovo', LV: 'Latvia', LI: 'Liechtenstein',
  LT: 'Lithuania', LU: 'Luxembourg', MK: 'North Macedonia', MT: 'Malta', MD: 'Moldova',
  MC: 'Monaco', ME: 'Montenegro', NL: 'Netherlands', NO: 'Norway', PL: 'Poland',
  PT: 'Portugal', RO: 'Romania', RU: 'Russia', SM: 'San Marino', RS: 'Serbia',
  SK: 'Slovakia', SI: 'Slovenia', ES: 'Spain', SE: 'Sweden', CH: 'Switzerland',
  UA: 'Ukraine', GB: 'United Kingdom', AG: 'Antigua', BS: 'Bahamas', BB: 'Barbados',
  BZ: 'Belize', CA: 'Canada', CR: 'Costa Rica', CU: 'Cuba', DM: 'Dominica',
  DO: 'Dominican Republic', SV: 'El Salvador', GD: 'Grenada', GT: 'Guatemala',
  HT: 'Haiti', HN: 'Honduras', JM: 'Jamaica', MX: 'Mexico', NI: 'Nicaragua',
  PA: 'Panama', KN: 'Saint Kitts', LC: 'Saint Lucia', VC: 'Saint Vincent',
  TT: 'Trinidad & Tobago', US: 'United States', AR: 'Argentina', BO: 'Bolivia',
  BR: 'Brazil', CL: 'Chile', CO: 'Colombia', EC: 'Ecuador', GY: 'Guyana',
  PY: 'Paraguay', PE: 'Peru', SR: 'Suriname', UY: 'Uruguay', VE: 'Venezuela',
  AU: 'Australia', FJ: 'Fiji', KI: 'Kiribati', MH: 'Marshall Islands', FM: 'Micronesia',
  NR: 'Nauru', NZ: 'New Zealand', PW: 'Palau', PG: 'Papua New Guinea', WS: 'Samoa',
  SB: 'Solomon Islands', TO: 'Tonga', TV: 'Tuvalu', VU: 'Vanuatu',
};

interface Station {
  id: string;
  name: string;
  country: string;
  genre: string;
  quality_score: number;
  stream_url: string;
}

interface CountryStats {
  code: string;
  name: string;
  count: number;
  continent: string;
}

export default function CountryExplorerScreen() {
  const [activeTab, setActiveTab] = useState<string>('map');
  const [selectedCountry, setSelectedCountry] = useState<string>('all');
  const [selectedContinent, setSelectedContinent] = useState<string>('all');
  const [countries, setCountries] = useState<CountryStats[]>([]);
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://dragon-radio.preview.emergentagent.com';

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedCountry !== 'all') {
      loadStationsByCountry(selectedCountry);
    }
  }, [selectedCountry]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load statistics
      const statsResponse = await fetch(`${backendUrl}/api/dragon-search/stats`);
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Load countries
      const countriesResponse = await fetch(`${backendUrl}/api/dragon-search/filters/countries`);
      const countriesData = await countriesResponse.json();
      
      // Map countries to their continents
      const enrichedCountries = countriesData.countries.map((c: any) => ({
        code: c.code,
        name: COUNTRY_NAMES[c.code] || c.code,
        count: c.count,
        continent: getContinent(c.code),
      }));
      
      setCountries(enrichedCountries);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStationsByCountry = async (countryCode: string) => {
    try {
      const response = await fetch(
        `${backendUrl}/api/dragon-search/stations?country=${countryCode}&limit=50`
      );
      const data = await response.json();
      setStations(data);
    } catch (error) {
      console.error('Error loading stations:', error);
    }
  };

  const getContinent = (countryCode: string): string => {
    for (const [continent, countries] of Object.entries(COUNTRY_REGIONS)) {
      if (countries.includes(countryCode)) {
        return continent;
      }
    }
    return 'UNKNOWN';
  };

  const getContinentColor = (continent: string): string => {
    const continentMap: { [key: string]: string } = {
      AF: '#FF6B6B',
      AS: '#4ECDC4',
      EU: '#45B7D1',
      NA: '#96CEB4',
      SA: '#FFEAA7',
      OC: '#DFE6E9',
    };
    return continentMap[continent] || '#B2BEC3';
  };

  const getFilteredCountries = () => {
    if (selectedContinent === 'all') return countries;
    return countries.filter(c => c.continent === selectedContinent);
  };

  const renderMapView = () => {
    const continents = Object.entries(CONTINENTS);
    
    return (
      <ScrollView style={styles.tabContent}>
        <View style={styles.mapContainer}>
          <Text style={styles.sectionTitle}>🌍 Global Coverage Map</Text>
          <Text style={styles.sectionSubtitle}>
            {stats?.total_stations || 0} stations across {stats?.unique_countries || 0} countries
          </Text>

          {/* Continent Grid */}
          <View style={styles.continentGrid}>
            {continents.map(([key, continent]) => {
              const countriesInContinent = countries.filter(c => c.continent === continent.code);
              const stationsInContinent = countriesInContinent.reduce((sum, c) => sum + c.count, 0);
              
              return (
                <TouchableOpacity
                  key={key}
                  style={[
                    styles.continentCard,
                    { backgroundColor: continent.color },
                    selectedContinent === continent.code && styles.continentCardActive,
                  ]}
                  onPress={() => setSelectedContinent(
                    selectedContinent === continent.code ? 'all' : continent.code
                  )}
                >
                  <Text style={styles.continentName}>{continent.name}</Text>
                  <Text style={styles.continentStats}>
                    {countriesInContinent.length} countries
                  </Text>
                  <Text style={styles.continentStations}>
                    {stationsInContinent} stations
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* ISO Region Legend */}
          <View style={styles.legendContainer}>
            <Text style={styles.legendTitle}>ISO Region Codes:</Text>
            {continents.map(([key, continent]) => (
              <View key={key} style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: continent.color }]} />
                <Text style={styles.legendText}>
                  {continent.code} - {continent.name}
                </Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderCountryListView = () => {
    const filteredCountries = getFilteredCountries();
    
    return (
      <View style={styles.tabContent}>
        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>Filter by Continent:</Text>
          <Picker
            selectedValue={selectedContinent}
            onValueChange={(value) => setSelectedContinent(value)}
            style={styles.picker}
          >
            <Picker.Item label="All Continents" value="all" />
            {Object.entries(CONTINENTS).map(([key, continent]) => (
              <Picker.Item key={key} label={continent.name} value={continent.code} />
            ))}
          </Picker>
        </View>

        <FlatList
          data={filteredCountries}
          keyExtractor={(item) => item.code}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.countryItem,
                selectedCountry === item.code && styles.countryItemActive,
              ]}
              onPress={() => {
                setSelectedCountry(item.code);
                setActiveTab('stations');
              }}
            >
              <View style={styles.countryItemLeft}>
                <View
                  style={[
                    styles.continentIndicator,
                    { backgroundColor: getContinentColor(item.continent) },
                  ]}
                />
                <View>
                  <Text style={styles.countryName}>
                    {item.code}-{item.name}
                  </Text>
                  <Text style={styles.countryRegion}>Region: {item.continent}</Text>
                </View>
              </View>
              <View style={styles.countryItemRight}>
                <Text style={styles.countryCount}>{item.count}</Text>
                <Text style={styles.countryLabel}>stations</Text>
              </View>
            </TouchableOpacity>
          )}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No countries found</Text>
            </View>
          }
        />
      </View>
    );
  };

  const renderStationsView = () => {
    return (
      <View style={styles.tabContent}>
        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>Select Country:</Text>
          <Picker
            selectedValue={selectedCountry}
            onValueChange={(value) => setSelectedCountry(value)}
            style={styles.picker}
          >
            <Picker.Item label="Select a country..." value="all" />
            {countries.map((country) => (
              <Picker.Item
                key={country.code}
                label={`${country.code}-${country.name} (${country.count} stations)`}
                value={country.code}
              />
            ))}
          </Picker>
        </View>

        {selectedCountry !== 'all' && (
          <FlatList
            data={stations}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <View style={styles.stationCard}>
                <View style={styles.stationHeader}>
                  <Text style={styles.stationName}>{item.name}</Text>
                  <View style={[
                    styles.qualityBadge,
                    { backgroundColor: item.quality_score >= 70 ? '#2ECC71' : item.quality_score >= 50 ? '#F39C12' : '#E74C3C' }
                  ]}>
                    <Text style={styles.qualityText}>{item.quality_score}</Text>
                  </View>
                </View>
                <View style={styles.stationDetails}>
                  <Text style={styles.stationGenre}>🎵 {item.genre}</Text>
                  <Text style={styles.stationCountry}>📍 {COUNTRY_NAMES[item.country]}</Text>
                </View>
              </View>
            )}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>
                  {selectedCountry === 'all'
                    ? 'Select a country to view stations'
                    : 'No stations found for this country'}
                </Text>
              </View>
            }
          />
        )}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6C5CE7" />
        <Text style={styles.loadingText}>Loading global data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🌍 Country Explorer</Text>
        <Text style={styles.headerSubtitle}>ISO Region Map & Stations</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'map' && styles.tabActive]}
          onPress={() => setActiveTab('map')}
        >
          <Text style={[styles.tabText, activeTab === 'map' && styles.tabTextActive]}>
            🗺️ Map
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'countries' && styles.tabActive]}
          onPress={() => setActiveTab('countries')}
        >
          <Text style={[styles.tabText, activeTab === 'countries' && styles.tabTextActive]}>
            🌐 Countries
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'stations' && styles.tabActive]}
          onPress={() => setActiveTab('stations')}
        >
          <Text style={[styles.tabText, activeTab === 'stations' && styles.tabTextActive]}>
            📻 Stations
          </Text>
        </TouchableOpacity>
      </View>

      {/* Tab Content */}
      {activeTab === 'map' && renderMapView()}
      {activeTab === 'countries' && renderCountryListView()}
      {activeTab === 'stations' && renderStationsView()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: '#6C5CE7',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#E0E0E0',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  tab: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#6C5CE7',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  tabTextActive: {
    color: '#6C5CE7',
  },
  tabContent: {
    flex: 1,
  },
  mapContainer: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 16,
    color: '#7F8C8D',
    marginBottom: 24,
  },
  continentGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  continentCard: {
    width: (width - 48) / 2,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  continentCardActive: {
    borderWidth: 3,
    borderColor: '#2C3E50',
  },
  continentName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 8,
  },
  continentStats: {
    fontSize: 14,
    color: '#FFF',
    opacity: 0.9,
  },
  continentStations: {
    fontSize: 12,
    color: '#FFF',
    opacity: 0.8,
    marginTop: 4,
  },
  legendContainer: {
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    elevation: 2,
  },
  legendTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  legendColor: {
    width: 24,
    height: 24,
    borderRadius: 4,
    marginRight: 12,
  },
  legendText: {
    fontSize: 14,
    color: '#34495E',
  },
  pickerContainer: {
    backgroundColor: '#FFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  pickerLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 8,
  },
  picker: {
    height: 50,
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
  },
  countryItem: {
    backgroundColor: '#FFF',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  countryItemActive: {
    backgroundColor: '#E8E4F3',
  },
  countryItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  continentIndicator: {
    width: 8,
    height: 40,
    borderRadius: 4,
    marginRight: 12,
  },
  countryName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
  },
  countryRegion: {
    fontSize: 12,
    color: '#7F8C8D',
    marginTop: 4,
  },
  countryItemRight: {
    alignItems: 'flex-end',
  },
  countryCount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6C5CE7',
  },
  countryLabel: {
    fontSize: 12,
    color: '#7F8C8D',
  },
  stationCard: {
    backgroundColor: '#FFF',
    padding: 16,
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  stationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  stationName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    flex: 1,
    marginRight: 8,
  },
  qualityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  qualityText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFF',
  },
  stationDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  stationGenre: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  stationCountry: {
    fontSize: 14,
    color: '#7F8C8D',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center',
  },
});
