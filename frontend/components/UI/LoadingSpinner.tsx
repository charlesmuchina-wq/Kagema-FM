import React from 'react';
import {
  View,
  ActivityIndicator,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

interface LoadingSpinnerProps {
  size?: 'small' | 'large';
  message?: string;
  overlay?: boolean;
  style?: ViewStyle;
  messageStyle?: TextStyle;
  color?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'large',
  message,
  overlay = false,
  style,
  messageStyle,
  color,
}) => {
  const { colors } = useTheme();

  const spinnerColor = color || colors.primary;

  const containerStyle = overlay
    ? [styles.overlayContainer, { backgroundColor: colors.background + 'DD' }]
    : [styles.inlineContainer];

  return (
    <View style={[containerStyle, style]}>
      <ActivityIndicator 
        size={size} 
        color={spinnerColor}
        style={styles.spinner}
      />
      {message && (
        <Text style={[
          styles.message,
          { color: colors.text },
          messageStyle
        ]}>
          {message}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  overlayContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  inlineContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  spinner: {
    marginBottom: 12,
  },
  message: {
    fontSize: 16,
    textAlign: 'center',
    marginTop: 8,
  },
});