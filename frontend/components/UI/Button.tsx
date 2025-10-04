import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  View,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';
import { shadowStyles } from '../../utils/shadowStyles';
import { Ionicons } from '@expo/vector-icons';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: keyof typeof Ionicons.glyphMap;
  iconPosition?: 'left' | 'right';
  style?: ViewStyle;
  textStyle?: TextStyle;
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  icon,
  iconPosition = 'left',
  style,
  textStyle,
  fullWidth = false,
}) => {
  const { colors } = useTheme();

  const getButtonStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 12,
      ...shadowStyles.button,
    };

    // Size styles
    const sizeStyles = {
      small: {
        paddingHorizontal: 16,
        paddingVertical: 8,
        minHeight: 36,
      },
      medium: {
        paddingHorizontal: 24,
        paddingVertical: 12,
        minHeight: 44,
      },
      large: {
        paddingHorizontal: 32,
        paddingVertical: 16,
        minHeight: 52,
      },
    };

    // Variant styles
    const variantStyles = {
      primary: {
        backgroundColor: colors.primary,
      },
      secondary: {
        backgroundColor: colors.accent,
      },
      outline: {
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderColor: colors.primary,
      },
      ghost: {
        backgroundColor: 'transparent',
      },
      danger: {
        backgroundColor: colors.error,
      },
    };

    // Disabled styles
    const disabledStyle = disabled || loading ? {
      opacity: 0.6,
    } : {};

    // Full width style
    const widthStyle = fullWidth ? { width: '100%' } : {};

    return {
      ...baseStyle,
      ...sizeStyles[size],
      ...variantStyles[variant],
      ...disabledStyle,
      ...widthStyle,
    };
  };

  const getTextStyle = (): TextStyle => {
    const baseTextStyle: TextStyle = {
      fontWeight: '600',
    };

    // Size text styles
    const sizeTextStyles = {
      small: {
        fontSize: 14,
      },
      medium: {
        fontSize: 16,
      },
      large: {
        fontSize: 18,
      },
    };

    // Variant text styles
    const variantTextStyles = {
      primary: {
        color: '#FFFFFF',
      },
      secondary: {
        color: '#FFFFFF',
      },
      outline: {
        color: colors.primary,
      },
      ghost: {
        color: colors.primary,
      },
      danger: {
        color: '#FFFFFF',
      },
    };

    return {
      ...baseTextStyle,
      ...sizeTextStyles[size],
      ...variantTextStyles[variant],
    };
  };

  const iconSize = {
    small: 16,
    medium: 20,
    large: 24,
  }[size];

  const iconColor = {
    primary: '#FFFFFF',
    secondary: '#FFFFFF',
    outline: colors.primary,
    ghost: colors.primary,
    danger: '#FFFFFF',
  }[variant];

  return (
    <TouchableOpacity
      style={[getButtonStyle(), style]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      {loading && (
        <ActivityIndicator
          size="small"
          color={iconColor}
          style={{ marginRight: title ? 8 : 0 }}
        />
      )}
      
      {!loading && icon && iconPosition === 'left' && (
        <Ionicons
          name={icon}
          size={iconSize}
          color={iconColor}
          style={{ marginRight: title ? 8 : 0 }}
        />
      )}
      
      {title && (
        <Text style={[getTextStyle(), textStyle]}>
          {title}
        </Text>
      )}
      
      {!loading && icon && iconPosition === 'right' && (
        <Ionicons
          name={icon}
          size={iconSize}
          color={iconColor}
          style={{ marginLeft: title ? 8 : 0 }}
        />
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  // Add any additional styles here if needed
});