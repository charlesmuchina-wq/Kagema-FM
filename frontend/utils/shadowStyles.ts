import { Platform, ViewStyle } from 'react-native';

export interface ShadowOptions {
  elevation?: number;
  shadowColor?: string;
  shadowOffset?: { width: number; height: number };
  shadowOpacity?: number;
  shadowRadius?: number;
}

/**
 * Creates cross-platform shadow styles that work on both React Native and Web
 * Automatically handles the deprecation of shadow* style props in favor of boxShadow
 */
export const createShadowStyle = (options: ShadowOptions): ViewStyle => {
  const {
    elevation = 4,
    shadowColor = '#000',
    shadowOffset = { width: 0, height: 2 },
    shadowOpacity = 0.1,
    shadowRadius = 4,
  } = options;

  if (Platform.OS === 'web') {
    // Use boxShadow for web platform (new standard)
    return {
      boxShadow: `${shadowOffset.width}px ${shadowOffset.height}px ${shadowRadius}px rgba(${hexToRgb(shadowColor)}, ${shadowOpacity})`,
    } as ViewStyle;
  } else if (Platform.OS === 'android') {
    // Use elevation for Android
    return {
      elevation,
    };
  } else {
    // Use shadow properties for iOS (still supported in React Native)
    return {
      shadowColor,
      shadowOffset,
      shadowOpacity,
      shadowRadius,
    };
  }
};

/**
 * Predefined shadow styles for common use cases
 */
export const shadowStyles = {
  small: createShadowStyle({
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
  }),
  
  medium: createShadowStyle({
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  }),
  
  large: createShadowStyle({
    elevation: 8,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  }),
  
  button: createShadowStyle({
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
  }),
  
  card: createShadowStyle({
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  }),
  
  modal: createShadowStyle({
    elevation: 16,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.25,
    shadowRadius: 16,
  }),
};

/**
 * Helper function to convert hex color to RGB values
 */
function hexToRgb(hex: string): string {
  // Remove # if present
  hex = hex.replace('#', '');
  
  // Handle 3-digit hex codes
  if (hex.length === 3) {
    hex = hex.split('').map(char => char + char).join('');
  }
  
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  return `${r}, ${g}, ${b}`;
}