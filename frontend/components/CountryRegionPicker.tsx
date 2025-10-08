// Step 2: Create the nested Pickers - SwiftUI-style implementation for React Native
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Platform,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { Region, Country, Language, RegionsData, LanguagesData, CountrySelection, CountryPickerProps, LocationInfo } from '../models/RegionModels';

// Data loading service
class RegionDataService {
  private static regionsData: RegionsData | null = null;
  private static languagesData: LanguagesData | null = null;

  static async loadRegions(): Promise<RegionsData> {
    if (this.regionsData) {
      return this.regionsData;
    }

    try {
      // In a real iOS app, this would be loaded from Bundle.main
      // For React Native, we'll import the JSON directly
      const regionsModule = require('../data/regions.json');
      this.regionsData = regionsModule as RegionsData;
      return this.regionsData;
    } catch (error) {
      console.error('Failed to load regions data:', error);
      // Fallback data
      return {
        regions: [
          {
            id: 'worldwide',
            name: 'Worldwide',
            emoji: '🌍',
            radioSource: 'radio.net',
            countries: [
              {
                id: 'worldwide',
                name: 'All Countries',
                emoji: '🌍',
                radioSource: 'radio.net'
              }
            ]
          }
        ]
      };
    }
  }

  static async loadLanguages(): Promise<LanguagesData> {
    if (this.languagesData) {
      return this.languagesData;
    }

    try {
      const languagesModule = require('../data/languages.json');
      this.languagesData = languagesModule as LanguagesData;
      return this.languagesData;
    } catch (error) {
      console.error('Failed to load languages data:', error);
      // Fallback data
      return {
        languages: [
          {
            id: 'english',
            name: 'English',
            nativeName: 'English',
            code: 'en',
            emoji: '🇺🇸',
            radioSources: ['radio.net']
          }
        ]
      };
    }
  }

  static async detectUserLocation(): Promise<LocationInfo> {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({});
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords;
            
            // Call backend for reverse geocoding
            const response = await fetch('/api/googlemaps/reverse-geocode', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ latitude, longitude })
            });

            if (response.ok) {
              const data = await response.json();
              if (data.address?.address_components) {
                const countryComponent = data.address.address_components.find(
                  (component: any) => component.types.includes('country')
                );
                
                resolve({
                  country: countryComponent?.long_name,
                  latitude,
                  longitude
                });
                return;
              }
            }
            
            resolve({ latitude, longitude });
          } catch (error) {
            console.error('Geocoding failed:', error);
            resolve({ latitude: position.coords.latitude, longitude: position.coords.longitude });
          }
        },
        (error) => {
          console.log('Location detection failed:', error);
          resolve({});
        },
        { timeout: 5000, enableHighAccuracy: false }
      );
    });
  }

  static findCountryByName(regionsData: RegionsData, countryName: string): { region: Region; country: Country } | null {
    // Country name mapping for common variations
    const countryMapping: { [key: string]: string } = {
      'United States': 'United States',
      'USA': 'United States', 
      'US': 'United States',
      'United Kingdom': 'United Kingdom',
      'UK': 'United Kingdom',
      'Great Britain': 'United Kingdom',
      'Deutschland': 'Germany',
      'Brasil': 'Brazil'
    };

    const normalizedName = countryMapping[countryName] || countryName;

    for (const region of regionsData.regions) {
      for (const country of region.countries) {
        if (country.name === normalizedName || country.name.includes(normalizedName)) {
          return { region, country };
        }
      }
    }
    return null;
  }
}

// Main SwiftUI-style Country Picker Component
export const CountryRegionPicker: React.FC<CountryPickerProps> = ({
  onSelectionChange,
  initialSelection,
  autoDetectLocation = true,
  style
}) => {
  // State management - equivalent to @State in SwiftUI
  const [regionsData, setRegionsData] = useState<RegionsData | null>(null);
  const [languagesData, setLanguagesData] = useState<LanguagesData | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<Country | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(null);
  const [isWorldwide, setIsWorldwide] = useState<boolean>(true);
  const [isLanguageOnly, setIsLanguageOnly] = useState<boolean>(false);
  const [selectionMode, setSelectionMode] = useState<'region' | 'language'>('region');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [locationDetected, setLocationDetected] = useState<boolean>(false);

  // Computed properties - equivalent to computed vars in SwiftUI
  const availableCountries: Country[] = selectedRegion ? selectedRegion.countries : [];
  const availableLanguages: Language[] = languagesData ? languagesData.languages : [];
  const currentSelection: CountrySelection = {
    selectedRegion,
    selectedCountry,
    selectedLanguage,
    isWorldwide,
    isLanguageOnly
  };

  // ViewDidLoad equivalent - onAppear in SwiftUI
  useEffect(() => {
    loadData();
  }, []);

  // Auto-detect location on component mount
  useEffect(() => {
    if (autoDetectLocation && regionsData && !locationDetected) {
      detectAndSetLocation();
    }
  }, [regionsData, autoDetectLocation, locationDetected]);

  // Notify parent of selection changes
  useEffect(() => {
    onSelectionChange(currentSelection);
  }, [selectedRegion, selectedCountry, selectedLanguage, isWorldwide, isLanguageOnly]);

  // Initialize with provided selection
  useEffect(() => {
    if (initialSelection && regionsData) {
      setSelectedRegion(initialSelection.selectedRegion);
      setSelectedCountry(initialSelection.selectedCountry);
      setIsWorldwide(initialSelection.isWorldwide);
    }
  }, [initialSelection, regionsData]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const data = await RegionDataService.loadRegions();
      setRegionsData(data);
      
      // Set default worldwide selection
      if (!initialSelection) {
        setIsWorldwide(true);
        setSelectedRegion(null);
        setSelectedCountry(null);
      }
    } catch (error) {
      console.error('Failed to load regions data:', error);
      Alert.alert('Error', 'Failed to load country data');
    } finally {
      setIsLoading(false);
    }
  };

  const detectAndSetLocation = async () => {
    try {
      const locationInfo = await RegionDataService.detectUserLocation();
      
      if (locationInfo.country && regionsData) {
        const match = RegionDataService.findCountryByName(regionsData, locationInfo.country);
        
        if (match) {
          console.log(`🌍 Auto-detected location: ${match.country.name} in ${match.region.name}`);
          setSelectedRegion(match.region);
          setSelectedCountry(match.country);
          setIsWorldwide(false);
          setLocationDetected(true);
        }
      }
    } catch (error) {
      console.error('Location detection failed:', error);
    }
  };

  // Handle region selection - equivalent to action in SwiftUI
  const handleRegionChange = (regionId: string) => {
    if (regionId === 'worldwide') {
      setIsWorldwide(true);
      setSelectedRegion(null);
      setSelectedCountry(null);
      return;
    }

    const region = regionsData?.regions.find(r => r.id === regionId);
    if (region) {
      setSelectedRegion(region);
      setSelectedCountry(null); // Reset country when region changes
      setIsWorldwide(false);
    }
  };

  // Handle country selection
  const handleCountryChange = (countryId: string) => {
    if (!selectedRegion || countryId === '') {
      setSelectedCountry(null);
      return;
    }

    const country = selectedRegion.countries.find(c => c.id === countryId);
    if (country) {
      setSelectedCountry(country);
      setIsWorldwide(false);
    }
  };

  // Reset to worldwide
  const resetToWorldwide = () => {
    setIsWorldwide(true);
    setSelectedRegion(null);
    setSelectedCountry(null);
  };

  if (isLoading || !regionsData) {
    return (
      <View style={[styles.container, style]}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading regions...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      {/* Title Header */}
      <View style={styles.headerContainer}>
        <Text style={styles.headerTitle}>Search by Region</Text>
        {locationDetected && (
          <Text style={styles.autoDetectedLabel}>📍 Auto-detected</Text>
        )}
      </View>

      {/* Worldwide Option */}
      <TouchableOpacity
        style={[styles.worldwideOption, isWorldwide && styles.worldwideOptionActive]}
        onPress={resetToWorldwide}
      >
        <Text style={[styles.worldwideText, isWorldwide && styles.worldwideTextActive]}>
          🌍 All Regions (Worldwide)
        </Text>
      </TouchableOpacity>

      {/* Region Picker - First Level */}
      <View style={styles.pickerContainer}>
        <Text style={styles.pickerLabel}>Select Region:</Text>
        <View style={styles.pickerWrapper}>
          <Picker
            selectedValue={selectedRegion?.id || 'worldwide'}
            onValueChange={handleRegionChange}
            style={styles.picker}
            itemStyle={Platform.OS === 'ios' ? styles.pickerItemIOS : undefined}
          >
            <Picker.Item 
              label="🌍 All Regions" 
              value="worldwide" 
              key="worldwide"
            />
            {regionsData.regions.map((region) => (
              <Picker.Item
                key={region.id}
                label={`${region.emoji} ${region.name}`}
                value={region.id}
              />
            ))}
          </Picker>
        </View>
      </View>

      {/* Country Picker - Second Level (Nested) */}
      {selectedRegion && !isWorldwide && (
        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>
            Select Country in {selectedRegion.emoji} {selectedRegion.name}:
          </Text>
          <View style={styles.pickerWrapper}>
            <Picker
              selectedValue={selectedCountry?.id || ''}
              onValueChange={handleCountryChange}
              style={styles.picker}
              itemStyle={Platform.OS === 'ios' ? styles.pickerItemIOS : undefined}
            >
              <Picker.Item 
                label={`All ${selectedRegion.name}`} 
                value="" 
                key="all-region"
              />
              {availableCountries.map((country) => (
                <Picker.Item
                  key={country.id}
                  label={`${country.emoji} ${country.name}`}
                  value={country.id}
                />
              ))}
            </Picker>
          </View>
        </View>
      )}

      {/* Current Selection Display */}
      <View style={styles.selectionDisplay}>
        <Text style={styles.selectionTitle}>Current Selection:</Text>
        <Text style={styles.selectionText}>
          {isWorldwide 
            ? '🌍 Worldwide Radio Networks' 
            : selectedCountry 
              ? `${selectedCountry.emoji} ${selectedCountry.name}` 
              : selectedRegion 
                ? `${selectedRegion.emoji} ${selectedRegion.name} (All Countries)`
                : '🌍 Worldwide'
          }
        </Text>
        {!isWorldwide && (selectedCountry || selectedRegion) && (
          <Text style={styles.radioSourceText}>
            Radio Source: {selectedCountry?.radioSource || selectedRegion?.radioSource}
          </Text>
        )}
      </View>
    </View>
  );
};

// SwiftUI-inspired styling
const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    margin: 8,
  },
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  autoDetectedLabel: {
    fontSize: 12,
    color: '#007AFF',
    backgroundColor: '#E8F4FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  worldwideOption: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    alignItems: 'center',
  },
  worldwideOptionActive: {
    borderColor: '#007AFF',
    backgroundColor: '#E8F4FF',
  },
  worldwideText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
  },
  worldwideTextActive: {
    color: '#007AFF',
    fontWeight: '600',
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  pickerWrapper: {
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    overflow: 'hidden',
  },
  picker: {
    height: Platform.OS === 'ios' ? 200 : 50,
    width: '100%',
  },
  pickerItemIOS: {
    fontSize: 16,
    height: 200,
  },
  selectionDisplay: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  selectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  selectionText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  radioSourceText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    fontStyle: 'italic',
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
});

export default CountryRegionPicker;