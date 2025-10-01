import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from 'react-native';

export interface ThemeColors {
  primary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  accent: string;
  error: string;
  success: string;
  warning: string;
  border: string;
  card: string;
  shadow: string;
}

export const lightTheme: ThemeColors = {
  primary: '#ff6b6b',
  background: '#ffffff',
  surface: '#f8f9fa',
  text: '#2c3e50',
  textSecondary: '#7f8c8d',
  accent: '#3498db',
  error: '#e74c3c',
  success: '#27ae60',
  warning: '#f39c12',
  border: '#ecf0f1',
  card: '#ffffff',
  shadow: 'rgba(0,0,0,0.1)'
};

export const darkTheme: ThemeColors = {
  primary: '#ff6b6b',
  background: '#1a1a1a',
  surface: '#2c2c2c',
  text: '#ffffff',
  textSecondary: '#b0b0b0',
  accent: '#3498db',
  error: '#e74c3c',
  success: '#27ae60',
  warning: '#f39c12',
  border: '#404040',
  card: '#2c2c2c',
  shadow: 'rgba(0,0,0,0.3)'
};

interface ThemeContextType {
  colors: ThemeColors;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (dark: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const systemColorScheme = useColorScheme();
  const [isDark, setIsDark] = useState(systemColorScheme === 'dark');
  const [isLoaded, setIsLoaded] = useState(false);

  // Load saved theme preference
  useEffect(() => {
    const loadTheme = async () => {
      try {
        const savedTheme = await AsyncStorage.getItem('theme_preference');
        if (savedTheme !== null) {
          setIsDark(savedTheme === 'dark');
        } else {
          // Use system preference
          setIsDark(systemColorScheme === 'dark');
        }
      } catch (error) {
        console.log('Error loading theme:', error);
      } finally {
        setIsLoaded(true);
      }
    };

    loadTheme();
  }, [systemColorScheme]);

  // Save theme preference
  const saveTheme = async (dark: boolean) => {
    try {
      await AsyncStorage.setItem('theme_preference', dark ? 'dark' : 'light');
    } catch (error) {
      console.log('Error saving theme:', error);
    }
  };

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    saveTheme(newTheme);
  };

  const setTheme = (dark: boolean) => {
    setIsDark(dark);
    saveTheme(dark);
  };

  const colors = isDark ? darkTheme : lightTheme;

  if (!isLoaded) {
    return null; // or a loading spinner
  }

  const value: ThemeContextType = {
    colors,
    isDark,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      {children}
    </ThemeContext.Provider>
  );
};