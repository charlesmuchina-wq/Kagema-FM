import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  TextStyle,
  AccessibilityInfo,
  Platform,
  Dimensions,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';
import * as Haptics from 'expo-haptics';

const { width: screenWidth } = Dimensions.get('window');

// Minimum touch target sizes (Apple HIG and Material Design)
const MIN_TOUCH_TARGET_SIZE = Platform.OS === 'ios' ? 44 : 48;
const COMFORTABLE_TOUCH_TARGET_SIZE = Platform.OS === 'ios' ? 48 : 52;

interface AccessibilityConfig {
  role?: 'button' | 'link' | 'text' | 'image' | 'header' | 'radiogroup' | 'checkbox';
  label?: string;
  hint?: string;
  state?: {
    selected?: boolean;
    disabled?: boolean;
    expanded?: boolean;
    checked?: boolean;
  };
  actions?: Array<{
    name: string;
    label: string;
  }>;
}

interface AccessibleTouchableProps {
  children: React.ReactNode;
  onPress: () => void;
  style?: ViewStyle;
  disabled?: boolean;
  accessibility: AccessibilityConfig;
  hapticFeedback?: 'light' | 'medium' | 'heavy' | 'selection';
  minTouchTarget?: boolean;
  testID?: string;
}

export const AccessibleTouchable: React.FC<AccessibleTouchableProps> = ({
  children,
  onPress,
  style,
  disabled = false,
  accessibility,
  hapticFeedback = 'light',
  minTouchTarget = true,
  testID,
}) => {
  const { colors } = useTheme();

  const handlePress = async () => {
    if (disabled) return;
    
    // Haptic feedback
    if (hapticFeedback && Platform.OS !== 'web') {
      const feedbackMap = {
        light: Haptics.ImpactFeedbackStyle.Light,
        medium: Haptics.ImpactFeedbackStyle.Medium,
        heavy: Haptics.ImpactFeedbackStyle.Heavy,
        selection: Haptics.SelectionFeedbackStyle,
      };
      
      if (hapticFeedback === 'selection') {
        await Haptics.selectionAsync();
      } else {
        await Haptics.impactAsync(feedbackMap[hapticFeedback]);
      }
    }
    
    onPress();
  };

  const touchableStyle: ViewStyle = StyleSheet.flatten([
    {
      minHeight: minTouchTarget ? MIN_TOUCH_TARGET_SIZE : undefined,
      minWidth: minTouchTarget ? MIN_TOUCH_TARGET_SIZE : undefined,
      alignItems: 'center',
      justifyContent: 'center',
    },
    style,
  ]);

  return (
    <TouchableOpacity
      style={touchableStyle}
      onPress={handlePress}
      disabled={disabled}
      accessible={true}
      accessibilityRole={accessibility.role || 'button'}
      accessibilityLabel={accessibility.label}
      accessibilityHint={accessibility.hint}
      accessibilityState={{
        disabled,
        selected: accessibility.state?.selected,
        expanded: accessibility.state?.expanded,
        checked: accessibility.state?.checked,
      }}
      accessibilityActions={accessibility.actions}
      testID={testID}
      activeOpacity={0.7}
    >
      {children}
    </TouchableOpacity>
  );
};

interface AccessibleTextProps {
  children: string;
  style?: TextStyle;
  role?: 'header' | 'text' | 'label';
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  accessible?: boolean;
}

export const AccessibleText: React.FC<AccessibleTextProps> = ({
  children,
  style,
  role = 'text',
  level,
  accessible = true,
}) => {
  const { colors } = useTheme();

  const getTextStyle = (): TextStyle => {
    const baseStyle: TextStyle = {
      color: colors.text,
    };

    if (role === 'header') {
      const headerSizes = {
        1: { fontSize: 32, fontWeight: 'bold' as const },
        2: { fontSize: 28, fontWeight: 'bold' as const },
        3: { fontSize: 24, fontWeight: '600' as const },
        4: { fontSize: 20, fontWeight: '600' as const },
        5: { fontSize: 18, fontWeight: '500' as const },
        6: { fontSize: 16, fontWeight: '500' as const },
      };
      
      return {
        ...baseStyle,
        ...headerSizes[level || 1],
      };
    }

    return baseStyle;
  };

  return (
    <Text
      style={[getTextStyle(), style]}
      accessible={accessible}
      accessibilityRole={role}
      accessibilityLevel={role === 'header' ? level : undefined}
    >
      {children}
    </Text>
  );
};

interface FocusableContainerProps {
  children: React.ReactNode;
  style?: ViewStyle;
  focusable?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
}

export const FocusableContainer: React.FC<FocusableContainerProps> = ({
  children,
  style,
  focusable = true,
  onFocus,
  onBlur,
}) => {
  const { colors } = useTheme();

  return (
    <View
      style={[
        {
          borderWidth: 2,
          borderColor: 'transparent',
        },
        style,
      ]}
      focusable={focusable}
      onFocus={onFocus}
      onBlur={onBlur}
    >
      {children}
    </View>
  );
};

// Screen reader utilities
export const announceForAccessibility = (message: string) => {
  if (Platform.OS !== 'web') {
    AccessibilityInfo.announceForAccessibility(message);
  }
};

export const setAccessibilityFocus = (reactTag: number) => {
  if (Platform.OS !== 'web') {
    AccessibilityInfo.setAccessibilityFocus(reactTag);
  }
};

// Font scaling helpers
export const getScaledFontSize = (baseFontSize: number): number => {
  // This would typically use a font scale preference
  // For now, we'll use a basic implementation
  return baseFontSize;
};

// High contrast helpers
export const getHighContrastColors = (colors: any) => {
  return {
    ...colors,
    text: colors.background === '#000000' ? '#FFFFFF' : '#000000',
    background: colors.background === '#000000' ? '#FFFFFF' : '#000000',
  };
};

// Touch target size helpers
export const ensureMinimumTouchTarget = (size: { width?: number; height?: number }): ViewStyle => {
  return {
    minWidth: Math.max(size.width || 0, MIN_TOUCH_TARGET_SIZE),
    minHeight: Math.max(size.height || 0, MIN_TOUCH_TARGET_SIZE),
  };
};

// Skip link component for keyboard navigation
interface SkipLinkProps {
  href: string;
  children: string;
}

export const SkipLink: React.FC<SkipLinkProps> = ({ href, children }) => {
  const { colors } = useTheme();

  return (
    <View style={styles.skipLink}>
      <AccessibleTouchable
        onPress={() => {
          // In a real implementation, this would navigate to the target
          console.log('Skip to:', href);
        }}
        accessibility={{
          role: 'link',
          label: children,
          hint: 'Activates to skip to main content',
        }}
        style={{
          backgroundColor: colors.primary,
          padding: 8,
          borderRadius: 4,
        }}
      >
        <Text style={{ color: '#FFFFFF', fontSize: 14 }}>
          {children}
        </Text>
      </AccessibleTouchable>
    </View>
  );
};

const styles = StyleSheet.create({
  skipLink: {
    position: 'absolute',
    top: -100,
    left: 16,
    zIndex: 1000,
    // Will be brought into view when focused
  },
});

// Accessibility testing helper
export const checkAccessibility = (component: React.ReactElement) => {
  // This would run accessibility audits in development
  if (__DEV__) {
    console.log('🔍 Accessibility check for component:', component.type.name);
    
    // Check for missing accessibility labels
    // Check for touch target sizes
    // Check for color contrast
    // etc.
  }
};