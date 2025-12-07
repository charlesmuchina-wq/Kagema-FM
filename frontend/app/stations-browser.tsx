import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  FlatList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Picker } from '@react-native-picker/picker';

interface Country {
  code: string;
  name: string;
  stationCount?: number;
}

interface Division {
  id: string;
  name: string;
  level: number;
  type: string;
  subdivisions?: Division[];
}

interface Station {
  id: string;
  name: string;
  call_sign?: string;
  standardized_name?: string;
  stream_url: string;
  country: string;
  division_level1?: string;
  division_level2?: string;
  quality_score: number;
}

const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://radio-uifix.preview.emergentagent.com';

export default function StationsBrowserScreen() {
  const [loading, setLoading] = useState(false);
  const [countries, setCountries] = useState<string[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [selectedDivisionL1, setSelectedDivisionL1] = useState<string>('');
  const [selectedDivisionL2, setSelectedDivisionL2] = useState<string>('');
  const [stations, setStations] = useState<Station[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMode, setFilterMode] = useState<'country' | 'division' | 'search'>('country');

  useEffect(() => {
    fetchCountries();
  }, []);

  useEffect(() => {
    if (selectedCountry) {
      fetchDivisions(selectedCountry);
      fetchStationsByCountry(selectedCountry);
    }
  }, [selectedCountry]);

  useEffect(() => {
    if (selectedDivisionL1) {
      fetchStationsByDivision(selectedDivisionL1);
    }
  }, [selectedDivisionL1]);

  useEffect(() => {
    if (selectedDivisionL2) {
      fetchStationsByDivision(selectedDivisionL2);
    }
  }, [selectedDivisionL2]);

  const fetchCountries = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/divisions/countries`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setCountries(data.data.countries);
      }
    } catch (error) {
      console.error('Error fetching countries:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDivisions = async (countryCode: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/divisions/${countryCode}/hierarchy`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setDivisions(data.data.divisions || []);
      }
    } catch (error) {
      console.error('Error fetching divisions:', error);
      setDivisions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStationsByCountry = async (countryCode: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/stations?country=${countryCode}&limit=100`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setStations(data.data.stations || []);
      }
    } catch (error) {
      console.error('Error fetching stations:', error);
      setStations([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStationsByDivision = async (divisionId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/stations/by-division/${divisionId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setStations(data.data.stations || []);
      }
    } catch (error) {
      console.error('Error fetching stations by division:', error);
      setStations([]);
    } finally {
      setLoading(false);
    }
  };

  const searchStations = async (query: string) => {
    if (!query.trim()) {
      setStations([]);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/stations/search?q=${encodeURIComponent(query)}&limit=50`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setStations(data.data.stations || []);
      }
    } catch (error) {
      console.error('Error searching stations:', error);
      setStations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = () => {
    searchStations(searchQuery);
  };

  const resetFilters = () => {
    setSelectedCountry('');
    setSelectedDivisionL1('');
    setSelectedDivisionL2('');
    setSearchQuery('');
    setStations([]);
    setDivisions([]);
  };

  const renderStation = ({ item }: { item: Station }) => (
    <TouchableOpacity
      style={styles.stationCard}
      onPress={() => {
        // Play station or navigate to details
        console.log('Selected station:', item);
      }}
    >
      <View style={styles.stationHeader}>
        <Text style={styles.stationName} numberOfLines={1}>
          {item.standardized_name || item.name}
        </Text>
        {item.quality_score > 0 && (
          <View style={styles.qualityBadge}>
            <Text style={styles.qualityText}>{item.quality_score}</Text>
          </View>
        )}
      </View>
      
      {item.call_sign && (
        <Text style={styles.callSign}>{item.call_sign}</Text>
      )}
      
      <View style={styles.stationMeta}>
        <Text style={styles.metaText} numberOfLines={1}>
          {item.country}
          {item.division_level1 && ` • ${item.division_level1}`}
          {item.division_level2 && ` • ${item.division_level2}`}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen 
        options={{
          title: 'Browse Stations',
          headerShown: true,
        }}
      />

      <ScrollView style={styles.content}>
        {/* Filter Mode Selector */}
        <View style={styles.filterModeContainer}>
          <TouchableOpacity
            style={[styles.modeButton, filterMode === 'country' && styles.modeButtonActive]}
            onPress={() => setFilterMode('country')}
          >
            <Text style={[styles.modeButtonText, filterMode === 'country' && styles.modeButtonTextActive]}>
              By Country
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.modeButton, filterMode === 'division' && styles.modeButtonActive]}
            onPress={() => setFilterMode('division')}
          >
            <Text style={[styles.modeButtonText, filterMode === 'division' && styles.modeButtonTextActive]}>
              By Division
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.modeButton, filterMode === 'search' && styles.modeButtonActive]}
            onPress={() => setFilterMode('search')}
          >
            <Text style={[styles.modeButtonText, filterMode === 'search' && styles.modeButtonTextActive]}>
              Search
            </Text>
          </TouchableOpacity>
        </View>

        {/* Search Mode */}
        {filterMode === 'search' && (
          <View style={styles.searchContainer}>
            <TextInput
              style={styles.searchInput}
              placeholder="Search by station name or call sign..."
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearchSubmit}
              returnKeyType="search"
            />
            <TouchableOpacity
              style={styles.searchButton}
              onPress={handleSearchSubmit}
            >
              <Text style={styles.searchButtonText}>Search</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Country Mode */}
        {filterMode === 'country' && (
          <View style={styles.pickerContainer}>
            <Text style={styles.label}>Select Country</Text>
            <View style={styles.pickerWrapper}>
              <Picker
                selectedValue={selectedCountry}
                onValueChange={(value) => setSelectedCountry(value)}
                style={styles.picker}
              >
                <Picker.Item label="Choose a country..." value="" />
                {countries.map((country) => (
                  <Picker.Item key={country} label={country} value={country} />
                ))}
              </Picker>
            </View>
          </View>
        )}

        {/* Division Mode */}
        {filterMode === 'division' && (
          <>
            {/* Country Picker */}
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Select Country</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={selectedCountry}
                  onValueChange={(value) => {
                    setSelectedCountry(value);
                    setSelectedDivisionL1('');
                    setSelectedDivisionL2('');
                  }}
                  style={styles.picker}
                >
                  <Picker.Item label="Choose a country..." value="" />
                  {countries.map((country) => (
                    <Picker.Item key={country} label={country} value={country} />
                  ))}
                </Picker>
              </View>
            </View>

            {/* Level 1 Division Picker */}
            {selectedCountry && divisions.length > 0 && (
              <View style={styles.pickerContainer}>
                <Text style={styles.label}>Select State/Province (Level 1)</Text>
                <View style={styles.pickerWrapper}>
                  <Picker
                    selectedValue={selectedDivisionL1}
                    onValueChange={(value) => {
                      setSelectedDivisionL1(value);
                      setSelectedDivisionL2('');
                    }}
                    style={styles.picker}
                  >
                    <Picker.Item label="All divisions..." value="" />
                    {divisions.map((div) => (
                      <Picker.Item 
                        key={div.id} 
                        label={`${div.name} (${div.type})`} 
                        value={div.id} 
                      />
                    ))}
                  </Picker>
                </View>
              </View>
            )}

            {/* Level 2 Division Picker */}
            {selectedDivisionL1 && (() => {
              const parentDivision = divisions.find(d => d.id === selectedDivisionL1);
              return parentDivision?.subdivisions && parentDivision.subdivisions.length > 0 ? (
                <View style={styles.pickerContainer}>
                  <Text style={styles.label}>Select County/District (Level 2)</Text>
                  <View style={styles.pickerWrapper}>
                    <Picker
                      selectedValue={selectedDivisionL2}
                      onValueChange={(value) => setSelectedDivisionL2(value)}
                      style={styles.picker}
                    >
                      <Picker.Item label="All sub-divisions..." value="" />
                      {parentDivision.subdivisions.map((subdiv) => (
                        <Picker.Item 
                          key={subdiv.id} 
                          label={`${subdiv.name} (${subdiv.type})`} 
                          value={subdiv.id} 
                        />
                      ))}
                    </Picker>
                  </View>
                </View>
              ) : null;
            })()}
          </>
        )}

        {/* Reset Button */}
        {(selectedCountry || searchQuery) && (
          <TouchableOpacity style={styles.resetButton} onPress={resetFilters}>
            <Text style={styles.resetButtonText}>Reset Filters</Text>
          </TouchableOpacity>
        )}

        {/* Results Section */}
        <View style={styles.resultsContainer}>
          <Text style={styles.resultsHeader}>
            {loading ? 'Loading...' : `${stations.length} Stations Found`}
          </Text>

          {loading ? (
            <ActivityIndicator size="large" color="#FF6B35" style={styles.loader} />
          ) : (
            <FlatList
              data={stations}
              renderItem={renderStation}
              keyExtractor={(item) => item.id}
              scrollEnabled={false}
              ListEmptyComponent={
                <Text style={styles.emptyText}>
                  {filterMode === 'search' && !searchQuery
                    ? 'Enter a search query to find stations'
                    : !selectedCountry
                    ? 'Select a country to view stations'
                    : 'No stations found for this selection'}
                </Text>
              }
            />
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  content: {
    flex: 1,
  },
  filterModeContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  modeButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#1A1F3A',
    alignItems: 'center',
  },
  modeButtonActive: {
    backgroundColor: '#FF6B35',
  },
  modeButtonText: {
    fontSize: 14,
    color: '#8B92B0',
    fontWeight: '600',
  },
  modeButtonTextActive: {
    color: '#FFFFFF',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    height: 48,
    backgroundColor: '#1A1F3A',
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#FFFFFF',
  },
  searchButton: {
    backgroundColor: '#FF6B35',
    paddingHorizontal: 24,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  pickerContainer: {
    padding: 16,
    paddingBottom: 8,
  },
  label: {
    fontSize: 14,
    color: '#8B92B0',
    marginBottom: 8,
    fontWeight: '600',
  },
  pickerWrapper: {
    backgroundColor: '#1A1F3A',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    color: '#FFFFFF',
    height: 48,
  },
  resetButton: {
    margin: 16,
    marginTop: 8,
    padding: 12,
    backgroundColor: '#2A2F4A',
    borderRadius: 8,
    alignItems: 'center',
  },
  resetButtonText: {
    color: '#FF6B35',
    fontSize: 14,
    fontWeight: '600',
  },
  resultsContainer: {
    padding: 16,
    paddingTop: 8,
  },
  resultsHeader: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 16,
  },
  loader: {
    marginTop: 32,
  },
  emptyText: {
    textAlign: 'center',
    color: '#8B92B0',
    fontSize: 14,
    marginTop: 32,
    lineHeight: 20,
  },
  stationCard: {
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  stationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  stationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    flex: 1,
  },
  qualityBadge: {
    backgroundColor: '#FF6B35',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginLeft: 8,
  },
  qualityText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
  },
  callSign: {
    fontSize: 14,
    color: '#FF6B35',
    fontWeight: '700',
    marginBottom: 8,
  },
  stationMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    fontSize: 12,
    color: '#8B92B0',
    flex: 1,
  },
});
