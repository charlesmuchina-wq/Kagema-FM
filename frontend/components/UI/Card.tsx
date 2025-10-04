import React from 'react';
import {
  View,
  ViewStyle,
  TouchableOpacity,
  GestureResponderEvent,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';
import { shadowStyles } from '../../utils/shadowStyles';

interface CardProps {
  children: React.ReactNode;
  onPress?: (event: GestureResponderEvent) => void;
  style?: ViewStyle;
  variant?: 'elevated' | 'outlined' | 'flat';
  padding?: 'none' | 'small' | 'medium' | 'large';
  margin?: 'none' | 'small' | 'medium' | 'large';
  borderRadius?: 'small' | 'medium' | 'large' | 'circular';
  disabled?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  onPress,
  style,
  variant = 'elevated',
  padding = 'medium',
  margin = 'none',
  borderRadius = 'medium',
  disabled = false,
}) => {
  const { colors } = useTheme();

  const getCardStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      backgroundColor: colors.card,
    };

    // Variant styles
    const variantStyles = {
      elevated: {
        ...shadowStyles.card,
      },
      outlined: {
        borderWidth: 1,
        borderColor: colors.border,
      },
      flat: {
        // No shadow or border
      },
    };

    // Padding styles
    const paddingStyles = {
      none: { padding: 0 },
      small: { padding: 12 },
      medium: { padding: 16 },
      large: { padding: 24 },
    };

    // Margin styles
    const marginStyles = {
      none: { margin: 0 },
      small: { margin: 8 },
      medium: { margin: 12 },
      large: { margin: 16 },
    };

    // Border radius styles
    const borderRadiusStyles = {
      small: { borderRadius: 8 },
      medium: { borderRadius: 12 },
      large: { borderRadius: 16 },
      circular: { borderRadius: 9999 },
    };

    // Disabled styles
    const disabledStyle = disabled ? { opacity: 0.6 } : {};

    return {
      ...baseStyle,
      ...variantStyles[variant],
      ...paddingStyles[padding],
      ...marginStyles[margin],
      ...borderRadiusStyles[borderRadius],
      ...disabledStyle,
    };
  };

  const CardComponent = onPress ? TouchableOpacity : View;

  return (
    <CardComponent
      style={[getCardStyle(), style]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={onPress ? 0.8 : 1}
    >
      {children}
    </CardComponent>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  style?: ViewStyle;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, style }) => {
  return (
    <View style={[{ marginBottom: 12 }, style]}>
      {children}
    </View>
  );
};

interface CardContentProps {
  children: React.ReactNode;
  style?: ViewStyle;
}

export const CardContent: React.FC<CardContentProps> = ({ children, style }) => {
  return (
    <View style={[{ flex: 1 }, style]}>
      {children}
    </View>
  );
};

interface CardFooterProps {
  children: React.ReactNode;
  style?: ViewStyle;
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, style }) => {
  return (
    <View style={[{ marginTop: 12 }, style]}>
      {children}
    </View>
  );
};