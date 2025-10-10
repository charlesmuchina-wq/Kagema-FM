import React, { useState, useEffect, useMemo } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  FlatList,
  TextInput,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';

interface Country {
  id: string;
  name: string;
  emoji: string;
  musicSources: string[];
  primaryGenres: string[];
  language: string;
  radioSource?: string;
}

interface Region {
  id: string;
  name: string;
  emoji: string;
  countries: Country[];
}

interface RegionsData {
  metadata: {
    total_countries: number;
    excluded_countries: string[];
    last_updated: string;
    version: string;
  };
  musicSources: Record<string, string>;
  regions: Region[];
}

interface ComprehensiveCountryPickerProps {
  selectedCountry?: Country;
  onSelectCountry: (country: Country) => void;
  visible: boolean;
  onClose: () => void;
  showMusicSources?: boolean;
  showGenres?: boolean;
}

export const ComprehensiveCountryPicker: React.FC<ComprehensiveCountryPickerProps> = ({
  selectedCountry,
  onSelectCountry,
  visible,
  onClose,
  showMusicSources = true,
  showGenres = true,
}) => {
  const { colors, isDark } = useTheme();
  const [regionsData, setRegionsData] = useState<RegionsData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'regions' | 'countries' | 'search'>('regions');

  // Load comprehensive regions data
  useEffect(() => {
    const loadRegionsData = async () => {
      try {
        setLoading(true);
        // Load the comprehensive regions data
        const regionsModule = await import('../../data/complete_regions.json');
        setRegionsData(regionsModule as RegionsData);
      } catch (error) {
        console.error('Error loading comprehensive regions data:', error);
        // Fallback to basic regions
        const fallbackRegions = await import('../../data/regions.json');
        setRegionsData(fallbackRegions as RegionsData);
      } finally {
        setLoading(false);
      }
    };

    if (visible) {
      loadRegionsData();
    }
  }, [visible]);

  // Get all countries for search
  const allCountries = useMemo(() => {
    if (!regionsData) return [];
    
    return regionsData.regions.flatMap((region) =>
      region.countries.map((country) => ({
        ...country,
        regionName: region.name,
        regionEmoji: region.emoji,
      }))
    ).sort((a, b) => a.name.localeCompare(b.name));
  }, [regionsData]);

  // Filter countries based on search
  const filteredCountries = useMemo(() => {
    if (!searchQuery.trim()) return allCountries;
    
    const query = searchQuery.toLowerCase();
    return allCountries.filter(
      (country) =>
        country.name.toLowerCase().includes(query) ||
        country.language.toLowerCase().includes(query) ||
        country.primaryGenres.some((genre) => genre.toLowerCase().includes(query))
    );
  }, [allCountries, searchQuery]);

  // Get countries for selected region
  const regionCountries = useMemo(() => {
    if (!regionsData || !selectedRegion) return [];
    
    const region = regionsData.regions.find((r) => r.id === selectedRegion);
    return region ? region.countries.sort((a, b) => a.name.localeCompare(b.name)) : [];
  }, [regionsData, selectedRegion]);

  const handleCountrySelect = (country: Country) => {
    onSelectCountry(country);
    onClose();
  };

  const handleRegionSelect = (regionId: string) => {
    setSelectedRegion(regionId);
    setViewMode('countries');
  };

  const resetToRegions = () => {
    setSelectedRegion(null);
    setViewMode('regions');
    setSearchQuery('');
  };

  const toggleSearchMode = () => {
    if (viewMode === 'search') {
      setViewMode('regions');
      setSearchQuery('');
    } else {
      setViewMode('search');
    }
  };

  const renderCountryItem = ({ item: country }: { item: Country & { regionName?: string; regionEmoji?: string } }) => (
    <TouchableOpacity
      style={[styles.countryItem, { backgroundColor: colors.cardBackground }]}
      onPress={() => handleCountrySelect(country)}
    >
      <View style={styles.countryHeader}>
        <Text style={styles.countryEmoji}>{country.emoji}</Text>
        <View style={styles.countryInfo}>
          <Text style={[styles.countryName, { color: colors.text }]}>{country.name}</Text>
          <Text style={[styles.countryLanguage, { color: colors.textSecondary }]}>
            {country.language}
            {country.regionName && ` • ${country.regionEmoji} ${country.regionName}`}
          </Text>
        </View>
        <View style={styles.countryStats}>
          <Text style={[styles.statsText, { color: colors.textSecondary }]}>
            {country.musicSources.length} sources
          </Text>
        </View>
      </View>
      
      {showGenres && (
        <View style={styles.genresContainer}>
          {country.primaryGenres.slice(0, 4).map((genre, index) => (
            <View key={genre} style={[styles.genrePill, { backgroundColor: colors.primary + '20' }]}>
              <Text style={[styles.genreText, { color: colors.primary }]}>
                {genre.replace('_', ' ')}
              </Text>
            </View>
          ))}
          {country.primaryGenres.length > 4 && (
            <Text style={[styles.moreGenres, { color: colors.textSecondary }]}>
              +{country.primaryGenres.length - 4} more
            </Text>
          )}
        </View>
      )}

      {showMusicSources && (
        <View style={styles.sourcesContainer}>
          <Text style={[styles.sourcesLabel, { color: colors.textSecondary }]}>Music Sources:</Text>
          <View style={styles.sourcesList}>
            {country.musicSources.slice(0, 3).map((source) => (
              <Text key={source} style={[styles.sourceItem, { color: colors.text }]}>
                {source.replace('_', ' ')}
              </Text>
            ))}
            {country.musicSources.length > 3 && (
              <Text style={[styles.moreSources, { color: colors.primary }]}>
                +{country.musicSources.length - 3} more
              </Text>
            )}
          </View>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderRegionItem = ({ item: region }: { item: Region }) => (
    <TouchableOpacity
      style={[styles.regionItem, { backgroundColor: colors.cardBackground }]}
      onPress={() => handleRegionSelect(region.id)}
    >
      <Text style={styles.regionEmoji}>{region.emoji}</Text>
      <View style={styles.regionInfo}>
        <Text style={[styles.regionName, { color: colors.text }]}>{region.name}</Text>
        <Text style={[styles.regionCount, { color: colors.textSecondary }]}>
          {region.countries.length} countries
        </Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
    </TouchableOpacity>
  );

  const renderHeader = () => (
    <View style={[styles.header, { backgroundColor: colors.cardBackground }]}>
      <View style={styles.headerTop}>
        {viewMode !== 'regions' && (
          <TouchableOpacity onPress={resetToRegions} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
        )}
        
        <Text style={[styles.title, { color: colors.text }]}>
          {viewMode === 'regions' && 'Select Region'}
          {viewMode === 'countries' && regionsData?.regions.find(r => r.id === selectedRegion)?.name}
          {viewMode === 'search' && 'Search Countries'}
        </Text>
        
        <TouchableOpacity onPress={toggleSearchMode} style={styles.searchButton}>
          <Ionicons 
            name={viewMode === 'search' ? "close" : "search"} 
            size={24} 
            color={colors.text} 
          />
        </TouchableOpacity>
        
        <TouchableOpacity onPress={onClose} style={styles.closeButton}>
          <Ionicons name="close" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {viewMode === 'search' && (
        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color={colors.textSecondary} style={styles.searchIcon} />
          <TextInput
            style={[styles.searchInput, { 
              backgroundColor: colors.background, 
              color: colors.text,
              borderColor: colors.border 
            }]}
            placeholder="Search by country, language, or music genre..."
            placeholderTextColor={colors.textSecondary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoFocus
          />
        </View>
      )}

      {regionsData && (
        <View style={styles.statsContainer}>
          <Text style={[styles.statsText, { color: colors.textSecondary }]}>
            {regionsData.metadata.total_countries} countries available • 
            Excludes: {regionsData.metadata.excluded_countries.join(', ')}
          </Text>
        </View>
      )}
    </View>
  );

  if (!visible) return null;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        {renderHeader()}
        
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
              Loading countries...
            </Text>
          </View>
        ) : (
          <FlatList
            data={
              viewMode === 'regions' 
                ? regionsData?.regions || []
                : viewMode === 'search'
                ? filteredCountries
                : regionCountries
            }
            renderItem={
              viewMode === 'regions' 
                ? renderRegionItem 
                : renderCountryItem
            }
            keyExtractor={(item) => item.id}
            style={styles.list}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>
    </Modal>
  );
};

const { height } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  backButton: {
    marginRight: 15,
  },
  title: {
    flex: 1,
    fontSize: 20,
    fontWeight: '600',
  },
  searchButton: {
    marginLeft: 15,
  },
  closeButton: {
    marginLeft: 15,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  searchIcon: {
    position: 'absolute',
    left: 15,
    zIndex: 1,
  },
  searchInput: {
    flex: 1,
    height: 40,
    borderRadius: 20,
    paddingLeft: 45,
    paddingRight: 15,
    borderWidth: 1,
    fontSize: 16,
  },
  statsContainer: {
    marginTop: 10,
  },
  statsText: {
    fontSize: 12,
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
  },
  list: {
    flex: 1,
  },
  listContent: {
    padding: 15,
  },
  regionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    marginBottom: 10,
    borderRadius: 12,
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  regionEmoji: {
    fontSize: 32,
    marginRight: 15,
  },
  regionInfo: {
    flex: 1,
  },
  regionName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 2,
  },
  regionCount: {
    fontSize: 14,
  },
  countryItem: {
    padding: 15,
    marginBottom: 10,
    borderRadius: 12,
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  countryHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  countryEmoji: {
    fontSize: 28,
    marginRight: 12,
    marginTop: 2,
  },
  countryInfo: {
    flex: 1,
  },
  countryName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  countryLanguage: {
    fontSize: 14,
  },
  countryStats: {
    alignItems: 'flex-end',
  },
  genresContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
    alignItems: 'center',
  },
  genrePill: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    marginRight: 6,
    marginBottom: 4,
  },
  genreText: {
    fontSize: 11,
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  moreGenres: {
    fontSize: 11,
    fontStyle: 'italic',
  },
  sourcesContainer: {
    marginTop: 8,
  },
  sourcesLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  sourcesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  sourceItem: {
    fontSize: 12,
    marginRight: 12,
    textTransform: 'capitalize',
  },
  moreSources: {
    fontSize: 12,
    fontWeight: '500',
  },
});

export default ComprehensiveCountryPicker;