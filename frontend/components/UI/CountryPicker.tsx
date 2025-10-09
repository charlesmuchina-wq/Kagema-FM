import React, { useState, useMemo, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  TextInput,
  FlatList,
  Dimensions,
  Animated,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../contexts/ThemeContext';
import { AccessibleTouchable, AccessibleText } from './AccessibilityHelpers';
import * as Haptics from 'expo-haptics';

const { height: screenHeight } = Dimensions.get('window');

interface Country {
  code: string;
  name: string;
  flag: string;
  region: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

// Extended country list with regions and coordinates
const COUNTRIES: Country[] = [
  { code: 'US', name: 'United States', flag: '🇺🇸', region: 'North America', coordinates: { latitude: 39.8283, longitude: -98.5795 } },
  { code: 'CA', name: 'Canada', flag: '🇨🇦', region: 'North America', coordinates: { latitude: 56.1304, longitude: -106.3468 } },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽', region: 'North America', coordinates: { latitude: 23.6345, longitude: -102.5528 } },
  { code: 'KE', name: 'Kenya', flag: '🇰🇪', region: 'Africa', coordinates: { latitude: -0.0236, longitude: 37.9062 } },
  { code: 'NG', name: 'Nigeria', flag: '🇳🇬', region: 'Africa', coordinates: { latitude: 9.0820, longitude: 8.6753 } },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦', region: 'Africa', coordinates: { latitude: -30.5595, longitude: 22.9375 } },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷', region: 'South America', coordinates: { latitude: -14.2350, longitude: -51.9253 } },
  { code: 'AR', name: 'Argentina', flag: '🇦🇷', region: 'South America', coordinates: { latitude: -38.4161, longitude: -63.6167 } },
  { code: 'CL', name: 'Chile', flag: '🇨🇱', region: 'South America', coordinates: { latitude: -35.6751, longitude: -71.5430 } },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧', region: 'Europe', coordinates: { latitude: 55.3781, longitude: -3.4360 } },
  { code: 'FR', name: 'France', flag: '🇫🇷', region: 'Europe', coordinates: { latitude: 46.6034, longitude: 1.8883 } },
  { code: 'DE', name: 'Germany', flag: '🇩🇪', region: 'Europe', coordinates: { latitude: 51.1657, longitude: 10.4515 } },
  { code: 'ES', name: 'Spain', flag: '🇪🇸', region: 'Europe', coordinates: { latitude: 40.4637, longitude: -3.7492 } },
  { code: 'IT', name: 'Italy', flag: '🇮🇹', region: 'Europe', coordinates: { latitude: 41.8719, longitude: 12.5674 } },
  { code: 'JP', name: 'Japan', flag: '🇯🇵', region: 'Asia', coordinates: { latitude: 36.2048, longitude: 138.2529 } },
  { code: 'CN', name: 'China', flag: '🇨🇳', region: 'Asia', coordinates: { latitude: 35.8617, longitude: 104.1954 } },
  { code: 'IN', name: 'India', flag: '🇮🇳', region: 'Asia', coordinates: { latitude: 20.5937, longitude: 78.9629 } },
  { code: 'AU', name: 'Australia', flag: '🇦🇺', region: 'Oceania', coordinates: { latitude: -25.2744, longitude: 133.7751 } },
  { code: 'NZ', name: 'New Zealand', flag: '🇳🇿', region: 'Oceania', coordinates: { latitude: -40.9006, longitude: 174.8860 } },
];

const REGIONS = ['All Regions', 'North America', 'South America', 'Europe', 'Africa', 'Asia', 'Oceania'];

interface CountryPickerProps {
  selectedCountry?: string;
  onCountrySelect: (country: Country) => void;
  placeholder?: string;
  showRegionFilter?: boolean;
  currentLocation?: {
    latitude: number;
    longitude: number;
  };
  disabled?: boolean;
}

export const CountryPicker: React.FC<CountryPickerProps> = ({
  selectedCountry,
  onCountrySelect,
  placeholder = 'Select Country',
  showRegionFilter = true,
  currentLocation,
  disabled = false,
}) => {
  const { colors, isDark } = useTheme();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('All Regions');
  const [modalAnimation] = useState(new Animated.Value(0));

  // Get selected country details
  const selectedCountryData = useMemo(() => {
    return COUNTRIES.find(country => country.code === selectedCountry);
  }, [selectedCountry]);

  // Filter countries based on search and region
  const filteredCountries = useMemo(() => {
    let filtered = COUNTRIES;

    // Filter by region
    if (selectedRegion !== 'All Regions') {
      filtered = filtered.filter(country => country.region === selectedRegion);
    }

    // Filter by search text
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(country =>
        country.name.toLowerCase().includes(searchLower) ||
        country.code.toLowerCase().includes(searchLower) ||
        country.region.toLowerCase().includes(searchLower)
      );
    }

    // Sort by distance if current location is available
    if (currentLocation) {
      filtered = filtered.sort((a, b) => {
        if (!a.coordinates || !b.coordinates) return 0;
        
        const distanceA = calculateDistance(
          currentLocation.latitude,
          currentLocation.longitude,
          a.coordinates.latitude,
          a.coordinates.longitude
        );
        
        const distanceB = calculateDistance(
          currentLocation.latitude,
          currentLocation.longitude,
          b.coordinates.latitude,
          b.coordinates.longitude
        );
        
        return distanceA - distanceB;
      });
    }

    return filtered;
  }, [searchText, selectedRegion, currentLocation]);

  // Calculate distance between two points (Haversine formula)
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const openModal = async () => {
    if (disabled) return;
    
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setIsModalVisible(true);
    
    Animated.spring(modalAnimation, {
      toValue: 1,
      useNativeDriver: true,
      tension: 120,
      friction: 8,
    }).start();
  };

  const closeModal = () => {
    Animated.spring(modalAnimation, {
      toValue: 0,
      useNativeDriver: true,
      tension: 120,
      friction: 8,
    }).start(() => {
      setIsModalVisible(false);
      setSearchText('');
      setSelectedRegion('All Regions');
    });
  };

  const handleCountrySelect = async (country: Country) => {
    await Haptics.selectionAsync();
    onCountrySelect(country);
    closeModal();
  };

  const renderCountryItem = ({ item, index }: { item: Country; index: number }) => {
    const isSelected = item.code === selectedCountry;
    const distance = currentLocation && item.coordinates
      ? calculateDistance(
          currentLocation.latitude,
          currentLocation.longitude,
          item.coordinates.latitude,
          item.coordinates.longitude
        )
      : null;

    return (
      <AccessibleTouchable
        onPress={() => handleCountrySelect(item)}
        accessibility={{
          role: 'button',
          label: `${item.name}, ${item.region}`,
          hint: distance ? `${Math.round(distance)} kilometers away` : undefined,
          state: { selected: isSelected },
        }}
        hapticFeedback="selection"
        style={[
          styles.countryItem,
          {
            backgroundColor: isSelected ? colors.primary + '20' : colors.card,
            borderColor: isSelected ? colors.primary : colors.border,
          },
        ]}
      >
        <View style={styles.countryFlag}>
          <Text style={styles.flagText}>{item.flag}</Text>
        </View>
        
        <View style={styles.countryInfo}>
          <AccessibleText style={[styles.countryName, { color: colors.text }]}>
            {item.name}
          </AccessibleText>
          <Text style={[styles.countryRegion, { color: colors.textSecondary }]}>
            {item.region}
            {distance && ` • ${Math.round(distance)}km away`}
          </Text>
        </View>
        
        {isSelected && (
          <Ionicons name="checkmark-circle" size={24} color={colors.primary} />
        )}
      </AccessibleTouchable>
    );
  };

  const renderRegionFilter = ({ item }: { item: string }) => {
    const isSelected = item === selectedRegion;
    
    return (
      <AccessibleTouchable
        onPress={() => setSelectedRegion(item)}
        accessibility={{
          role: 'button',
          label: item,
          state: { selected: isSelected },
        }}
        hapticFeedback="selection"
        style={[
          styles.regionChip,
          {
            backgroundColor: isSelected ? colors.primary : colors.surface,
            borderColor: isSelected ? colors.primary : colors.border,
          },
        ]}
      >
        <Text
          style={[
            styles.regionChipText,
            { color: isSelected ? '#FFFFFF' : colors.text },
          ]}
        >
          {item}
        </Text>
      </AccessibleTouchable>
    );
  };

  const styles = StyleSheet.create({
    trigger: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: colors.surface,
      borderRadius: 12,
      borderWidth: 1,
      borderColor: colors.border,
      paddingHorizontal: 16,
      paddingVertical: 12,
      minHeight: 48,
    },
    triggerContent: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    triggerFlag: {
      fontSize: 24,
      marginRight: 12,
    },
    triggerText: {
      fontSize: 16,
      color: colors.text,
      flex: 1,
    },
    placeholderText: {
      fontSize: 16,
      color: colors.textSecondary,
    },
    modal: {
      flex: 1,
      backgroundColor: colors.background + 'F0',
    },
    modalContent: {
      flex: 1,
      backgroundColor: colors.background,
      borderTopLeftRadius: 20,
      borderTopRightRadius: 20,
      marginTop: 60,
    },
    modalHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: 20,
      paddingVertical: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    modalTitle: {
      fontSize: 20,
      fontWeight: '600',
      color: colors.text,
    },
    searchContainer: {
      paddingHorizontal: 20,
      paddingTop: 16,
      paddingBottom: 8,
    },
    searchInput: {
      backgroundColor: colors.surface,
      borderRadius: 12,
      paddingHorizontal: 16,
      paddingVertical: 12,
      fontSize: 16,
      color: colors.text,
      borderWidth: 1,
      borderColor: colors.border,
    },
    regionFilters: {
      paddingHorizontal: 20,
      paddingBottom: 16,
    },
    regionChip: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 20,
      borderWidth: 1,
      marginRight: 8,
    },
    regionChipText: {
      fontSize: 14,
      fontWeight: '500',
    },
    countryList: {
      flex: 1,
    },
    countryItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 20,
      paddingVertical: 16,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
      borderWidth: 1,
      marginHorizontal: 16,
      marginBottom: 8,
      borderRadius: 12,
    },
    countryFlag: {
      marginRight: 16,
    },
    flagText: {
      fontSize: 28,
    },
    countryInfo: {
      flex: 1,
    },
    countryName: {
      fontSize: 16,
      fontWeight: '500',
      marginBottom: 2,
    },
    countryRegion: {
      fontSize: 14,
    },
    emptyState: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 40,
    },
    emptyStateText: {
      fontSize: 16,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 12,
    },
  });

  return (
    <>
      {/* Country Picker Trigger */}
      <AccessibleTouchable
        onPress={openModal}
        accessibility={{
          role: 'button',
          label: selectedCountryData
            ? `Selected country: ${selectedCountryData.name}`
            : placeholder,
          hint: 'Opens country selection modal',
        }}
        style={[
          styles.trigger,
          disabled && { opacity: 0.6 },
        ]}
        disabled={disabled}
      >
        <View style={styles.triggerContent}>
          {selectedCountryData && (
            <Text style={styles.triggerFlag}>
              {selectedCountryData.flag}
            </Text>
          )}
          <Text
            style={selectedCountryData ? styles.triggerText : styles.placeholderText}
            numberOfLines={1}
          >
            {selectedCountryData ? selectedCountryData.name : placeholder}
          </Text>
        </View>
        <Ionicons
          name={isModalVisible ? 'chevron-up' : 'chevron-down'}
          size={20}
          color={colors.textSecondary}
        />
      </AccessibleTouchable>

      {/* Country Selection Modal */}
      <Modal
        visible={isModalVisible}
        animationType="none"
        transparent={true}
        onRequestClose={closeModal}
      >
        <Animated.View
          style={[
            styles.modal,
            {
              transform: [
                {
                  scale: modalAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0.9, 1],
                  }),
                },
              ],
              opacity: modalAnimation,
            },
          ]}
        >
          <SafeAreaView style={{ flex: 1 }} edges={['top']}>
            <View style={styles.modalContent}>
              {/* Header */}
              <View style={styles.modalHeader}>
                <AccessibleText
                  role="header"
                  level={2}
                  style={styles.modalTitle}
                >
                  Select Country
                </AccessibleText>
                <AccessibleTouchable
                  onPress={closeModal}
                  accessibility={{
                    role: 'button',
                    label: 'Close country picker',
                  }}
                >
                  <Ionicons name="close" size={24} color={colors.text} />
                </AccessibleTouchable>
              </View>

              {/* Search Input */}
              <View style={styles.searchContainer}>
                <TextInput
                  style={styles.searchInput}
                  placeholder="Search countries..."
                  placeholderTextColor={colors.textSecondary}
                  value={searchText}
                  onChangeText={setSearchText}
                  autoCorrect={false}
                  accessibilityLabel="Search countries"
                  accessibilityHint="Type to filter countries by name"
                />
              </View>

              {/* Region Filters */}
              {showRegionFilter && (
                <View style={styles.regionFilters}>
                  <FlatList
                    data={REGIONS}
                    renderItem={renderRegionFilter}
                    keyExtractor={(item) => item}
                    horizontal
                    showsHorizontalScrollIndicator={false}
                  />
                </View>
              )}

              {/* Country List */}
              <FlatList
                data={filteredCountries}
                renderItem={renderCountryItem}
                keyExtractor={(item) => item.code}
                style={styles.countryList}
                showsVerticalScrollIndicator={false}
                ListEmptyComponent={
                  <View style={styles.emptyState}>
                    <Ionicons name="search" size={48} color={colors.textSecondary} />
                    <Text style={styles.emptyStateText}>
                      No countries found matching your search
                    </Text>
                  </View>
                }
              />
            </View>
          </SafeAreaView>
        </Animated.View>
      </Modal>
    </>
  );
};