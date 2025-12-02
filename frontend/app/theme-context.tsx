import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type ThemeMode = 'batik' | 'dark' | 'light';

interface Theme {
  mode: ThemeMode;
  colors: {
    background: string;
    surface: string;
    primary: string;
    secondary: string;
    text: string;
    textSecondary: string;
    border: string;
    accent: string;
    error: string;
    success: string;
  };
}

const THEMES: Record<ThemeMode, Theme> = {
  batik: {
    mode: 'batik',
    colors: {
      background: '#000000',
      surface: '#1A1A1A',
      primary: '#FFFFFF',
      secondary: '#888888',
      text: '#FFFFFF',
      textSecondary: '#888888',
      border: '#FFFFFF',
      accent: '#FF6B35',
      error: '#FF0000',
      success: '#00FF00',
    },
  },
  dark: {
    mode: 'dark',
    colors: {
      background: '#121212',
      surface: '#1E1E1E',
      primary: '#BB86FC',
      secondary: '#03DAC6',
      text: '#FFFFFF',
      textSecondary: '#B0B0B0',
      border: '#333333',
      accent: '#FF6B35',
      error: '#CF6679',
      success: '#4CAF50',
    },
  },
  light: {
    mode: 'light',
    colors: {
      background: '#FFFFFF',
      surface: '#F5F5F5',
      primary: '#6200EE',
      secondary: '#03DAC6',
      text: '#000000',
      textSecondary: '#666666',
      border: '#E0E0E0',
      accent: '#FF6B35',
      error: '#B00020',
      success: '#4CAF50',
    },
  },
};

interface ThemeContextType {
  theme: Theme;
  setThemeMode: (mode: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeMode, setThemeModeState] = useState<ThemeMode>('batik');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadThemePreference();
  }, []);

  const loadThemePreference = async () => {
    try {
      const savedTheme = await AsyncStorage.getItem('theme_mode');
      if (savedTheme && (savedTheme === 'batik' || savedTheme === 'dark' || savedTheme === 'light')) {
        setThemeModeState(savedTheme as ThemeMode);
      }
    } catch (error) {
      console.error('Error loading theme:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setThemeMode = async (mode: ThemeMode) => {
    try {
      await AsyncStorage.setItem('theme_mode', mode);
      setThemeModeState(mode);
    } catch (error) {
      console.error('Error saving theme:', error);
    }
  };

  const toggleTheme = () => {
    const modes: ThemeMode[] = ['batik', 'dark', 'light'];
    const currentIndex = modes.indexOf(themeMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setThemeMode(modes[nextIndex]);
  };

  if (isLoading) {
    return null; // or a loading spinner
  }

  const theme = THEMES[themeMode];

  return (
    <ThemeContext.Provider value={{ theme, setThemeMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// Helper function to get theme-aware styles
export function getThemedStyles(theme: Theme) {
  return {
    container: {
      backgroundColor: theme.colors.background,
    },
    surface: {
      backgroundColor: theme.colors.surface,
      borderColor: theme.colors.border,
    },
    text: {
      color: theme.colors.text,
    },
    textSecondary: {
      color: theme.colors.textSecondary,
    },
    button: {
      backgroundColor: theme.colors.primary,
    },
    buttonText: {
      color: theme.mode === 'light' ? '#FFFFFF' : theme.colors.background,
    },
    accent: {
      backgroundColor: theme.colors.accent,
    },
    border: {
      borderColor: theme.colors.border,
    },
  };
}
