/**
 * Design Tokens - Single Source of Truth for Visual Design
 * 
 * This file contains all design values used throughout the app.
 * Any change here propagates automatically to all components.
 */

export const DESIGN_TOKENS = {
  /**
   * Color Palette
   * Consistent colors across the entire app
   */
  colors: {
    // Primary Colors
    primary: '#FF6B35',           // Dragon Orange
    primaryDark: '#E85A2A',
    primaryLight: '#FF8B5D',
    
    // Secondary Colors
    secondary: '#1E88E5',         // Sky Blue
    secondaryDark: '#1565C0',
    secondaryLight: '#42A5F5',
    
    // Accent Colors
    accent: {
      cyan: '#00BCD4',
      purple: '#9C27B0',
      green: '#4CAF50',
      indigo: '#4A5AE8',
    },
    
    // Background & Surfaces
    background: '#000000',         // Pure Black (Batik theme)
    surface: 'rgba(26, 31, 58, 0.95)',
    surfaceLight: 'rgba(139, 146, 176, 0.1)',
    
    // Text Colors
    text: {
      primary: '#FFFFFF',
      secondary: '#8B92B0',
      disabled: '#5A5F7A',
      hint: '#4A4F6A',
    },
    
    // Border Colors
    border: {
      primary: 'rgba(255, 107, 53, 0.5)',
      secondary: 'rgba(139, 146, 176, 0.2)',
      accent: 'rgba(255, 107, 53, 0.3)',
    },
    
    // Status Colors
    status: {
      success: '#4CAF50',
      warning: '#FFC107',
      error: '#F44336',
      info: '#2196F3',
    },
    
    // Overlay & Shadow
    overlay: 'rgba(0, 0, 0, 0.7)',
    shadow: '#000000',
  },
  
  /**
   * Spacing System
   * Based on 8pt grid for consistency
   */
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    xxxl: 64,
  },
  
  /**
   * Typography Scale
   * Font sizes following a modular scale
   */
  typography: {
    // Font Sizes
    size: {
      xs: 10,
      sm: 12,
      md: 14,
      lg: 16,
      xl: 18,
      xxl: 20,
      xxxl: 24,
      display: 32,
      hero: 40,
    },
    
    // Font Weights
    weight: {
      regular: '400' as const,
      medium: '500' as const,
      semibold: '600' as const,
      bold: '700' as const,
      extrabold: '800' as const,
    },
    
    // Line Heights (relative to font size)
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
      loose: 2,
    },
    
    // Letter Spacing
    letterSpacing: {
      tight: -0.5,
      normal: 0,
      wide: 0.5,
      wider: 1,
      widest: 2,
    },
  },
  
  /**
   * Border Radius
   * Consistent rounded corners
   */
  borderRadius: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    xxl: 24,
    round: 999, // Fully rounded (pills, circles)
  },
  
  /**
   * Border Widths
   */
  borderWidth: {
    thin: 1,
    medium: 2,
    thick: 3,
  },
  
  /**
   * Elevation & Shadow
   * Consistent depth perception
   */
  elevation: {
    none: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0,
      shadowRadius: 0,
      elevation: 0,
    },
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 4,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.2,
      shadowRadius: 12,
      elevation: 6,
    },
    xl: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.25,
      shadowRadius: 16,
      elevation: 8,
    },
  },
  
  /**
   * Icon Sizes
   * Consistent icon sizing
   */
  iconSize: {
    xs: 16,
    sm: 20,
    md: 24,
    lg: 32,
    xl: 40,
    xxl: 48,
    xxxl: 64,
  },
  
  /**
   * Layout Dimensions
   * Common layout measurements
   */
  layout: {
    // Container widths
    containerPadding: 20,
    maxContentWidth: 1200,
    
    // Touch targets (minimum for accessibility)
    minTouchTarget: 44,
    
    // Component heights
    buttonHeight: {
      sm: 32,
      md: 44,
      lg: 56,
    },
    inputHeight: {
      sm: 36,
      md: 48,
      lg: 60,
    },
    
    // Feature tile
    tileHeight: 180,
    tileMinWidth: 140,
  },
  
  /**
   * Animation Timings
   * Consistent animation durations
   */
  animation: {
    duration: {
      fast: 150,
      normal: 300,
      slow: 500,
    },
    easing: {
      default: 'ease-in-out',
      enter: 'ease-out',
      exit: 'ease-in',
    },
  },
  
  /**
   * Z-Index Scale
   * Consistent layering
   */
  zIndex: {
    background: -1,
    base: 0,
    content: 10,
    header: 100,
    overlay: 500,
    modal: 1000,
    popover: 1500,
    tooltip: 2000,
    toast: 3000,
  },
  
  /**
   * Opacity Values
   * Consistent transparency levels
   */
  opacity: {
    disabled: 0.4,
    muted: 0.6,
    semiTransparent: 0.8,
    almostOpaque: 0.95,
  },
} as const;

/**
 * Helper type for accessing design tokens
 */
export type DesignTokens = typeof DESIGN_TOKENS;

/**
 * Utility function to get spacing value
 */
export const getSpacing = (multiplier: number): number => {
  return DESIGN_TOKENS.spacing.md * multiplier;
};

/**
 * Utility function to create responsive spacing
 */
export const responsiveSpacing = {
  horizontal: DESIGN_TOKENS.spacing.lg,
  vertical: DESIGN_TOKENS.spacing.md,
  section: DESIGN_TOKENS.spacing.xl,
};

/**
 * Common component styles using design tokens
 */
export const commonStyles = {
  // Card style
  card: {
    backgroundColor: DESIGN_TOKENS.colors.surface,
    borderRadius: DESIGN_TOKENS.borderRadius.lg,
    padding: DESIGN_TOKENS.spacing.lg,
    ...DESIGN_TOKENS.elevation.md,
  },
  
  // Button style
  button: {
    borderRadius: DESIGN_TOKENS.borderRadius.md,
    paddingHorizontal: DESIGN_TOKENS.spacing.lg,
    paddingVertical: DESIGN_TOKENS.spacing.md,
    minHeight: DESIGN_TOKENS.layout.minTouchTarget,
  },
  
  // Input style
  input: {
    borderRadius: DESIGN_TOKENS.borderRadius.md,
    paddingHorizontal: DESIGN_TOKENS.spacing.md,
    paddingVertical: DESIGN_TOKENS.spacing.sm,
    borderWidth: DESIGN_TOKENS.borderWidth.thin,
    minHeight: DESIGN_TOKENS.layout.inputHeight.md,
  },
};

export default DESIGN_TOKENS;
