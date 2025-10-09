import * as Location from 'expo-location';
import { useState, useEffect } from 'react';
import { Alert, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export const useLocation = () => {
  const [location, setLocation] = useState(null);
  const [locationInfo, setLocationInfo] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [loading, setLoading] = useState(true);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMsg('Permission to access location was denied');
        setLoading(false);
        return false;
      }
      return true;
    } catch (error) {
      console.error('Error requesting location permission:', error);
      setErrorMsg('Failed to request location permission');
      setLoading(false);
      return false;
    }
  };

  const getCurrentLocation = async () => {
    try {
      setLoading(true);
      const hasPermission = await requestLocationPermission();
      
      if (!hasPermission) {
        return;
      }

      // Check if we have a cached location (less than 10 minutes old)
      const cachedLocation = await AsyncStorage.getItem('cachedLocation');
      if (cachedLocation) {
        const { location: loc, timestamp, locationInfo: info } = JSON.parse(cachedLocation);
        if (Date.now() - timestamp < 600000) { // 10 minutes
          setLocation(loc);
          setLocationInfo(info);
          setLoading(false);
          return;
        }
      }

      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        timeout: 15000,
        maximumAge: 10000,
      });

      setLocation(currentLocation);
      
      // Get location info (city, country)
      const locInfo = await getLocationInfo(
        currentLocation.coords.latitude,
        currentLocation.coords.longitude
      );
      setLocationInfo(locInfo);

      // Cache the location
      await AsyncStorage.setItem('cachedLocation', JSON.stringify({
        location: currentLocation,
        locationInfo: locInfo,
        timestamp: Date.now()
      }));

      setErrorMsg(null);
    } catch (error) {
      console.error('Error getting current location:', error);
      setErrorMsg('Failed to get current location');
      
      // Use fallback location (Nairobi)
      const fallbackLocation = {
        coords: {
          latitude: -1.2921,
          longitude: 36.8219
        }
      };
      const fallbackInfo = {
        city: 'Nairobi',
        region: 'Nairobi County',
        country: 'Kenya'
      };
      
      setLocation(fallbackLocation);
      setLocationInfo(fallbackInfo);
    } finally {
      setLoading(false);
    }
  };

  const getLocationInfo = async (latitude, longitude) => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/googlemaps/reverse-geocode`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude, longitude }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Extract location info from Google Maps response
        if (data.address && data.address.formatted_address) {
          const addressComponents = data.address.address_components || [];
          
          let city = '';
          let region = '';
          let country = '';
          
          for (const component of addressComponents) {
            const types = component.types;
            if (types.includes('locality')) {
              city = component.long_name;
            } else if (types.includes('administrative_area_level_1')) {
              region = component.long_name;
            } else if (types.includes('country')) {
              country = component.long_name;
            }
          }
          
          return {
            city: city || 'Unknown City',
            region: region || 'Unknown Region',
            country: country || 'Unknown Country',
            formatted_address: data.address.formatted_address
          };
        } else {
          throw new Error('Invalid geocoding response format');
        }
      } else {
        throw new Error('Failed to geocode location');
      }
    } catch (error) {
      console.log('Geocoding service unavailable, using fallback based on coordinates');
      
      // Simple coordinate-based fallback
      let fallbackLocation = { city: 'Unknown', region: 'Unknown', country: 'Unknown' };
      
      // Kenya coordinates
      if (latitude >= -4.5 && latitude <= 4.5 && longitude >= 33.5 && longitude <= 42) {
        fallbackLocation = { city: 'Nairobi', region: 'Nairobi County', country: 'Kenya' };
      }
      // Brazil coordinates
      else if (latitude >= -33.8 && latitude <= 5.3 && longitude >= -74 && longitude <= -32) {
        fallbackLocation = { city: 'São Paulo', region: 'São Paulo', country: 'Brazil' };
      }
      // US coordinates
      else if (latitude >= 24.4 && latitude <= 49.4 && longitude >= -125 && longitude <= -66.9) {
        fallbackLocation = { city: 'New York', region: 'New York', country: 'United States' };
      }
      // Europe coordinates
      else if (latitude >= 35 && latitude <= 71 && longitude >= -10 && longitude <= 40) {
        fallbackLocation = { city: 'London', region: 'England', country: 'United Kingdom' };
      }
      
      return fallbackLocation;
    }
  };

  const watchLocation = async () => {
    try {
      const hasPermission = await requestLocationPermission();
      
      if (!hasPermission) {
        return null;
      }

      const subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.Balanced,
          timeInterval: 30000,
          distanceInterval: 100,
        },
        (newLocation) => {
          setLocation(newLocation);
          // Update location info when location changes significantly
          getLocationInfo(
            newLocation.coords.latitude,
            newLocation.coords.longitude
          ).then(setLocationInfo);
        }
      );

      return subscription;
    } catch (error) {
      console.error('Error watching location:', error);
      setErrorMsg('Failed to watch location changes');
      return null;
    }
  };

  useEffect(() => {
    getCurrentLocation();
  }, []);

  return { 
    location, 
    locationInfo, 
    errorMsg, 
    loading, 
    getCurrentLocation, 
    watchLocation 
  };
};

export default useLocation;