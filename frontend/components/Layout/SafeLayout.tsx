import React from 'react';
import {
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  StyleSheet,
  View,
  ViewStyle,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../../contexts/ThemeContext';

interface SafeLayoutProps {
  children: React.ReactNode;
  style?: ViewStyle;
  keyboardAvoiding?: boolean;
  statusBarStyle?: 'auto' | 'inverted' | 'light' | 'dark';
  edges?: ('top' | 'bottom' | 'left' | 'right')[];
  backgroundColor?: string;
}

export const SafeLayout: React.FC<SafeLayoutProps> = ({
  children,
  style,
  keyboardAvoiding = true,
  statusBarStyle = 'auto',
  edges = ['top', 'bottom'],
  backgroundColor,
}) => {
  const { colors, isDark } = useTheme();
  const insets = useSafeAreaInsets();

  // Dynamic status bar style based on theme
  const getStatusBarStyle = () => {
    if (statusBarStyle === 'auto') {
      return isDark ? 'light-content' : 'dark-content';
    }
    return statusBarStyle === 'light' ? 'light-content' : 'dark-content';
  };

  // Create safe area insets based on edges prop
  const getSafeAreaStyle = (): ViewStyle => {
    const safeStyle: ViewStyle = {};
    
    if (edges.includes('top')) {
      safeStyle.paddingTop = insets.top;
    }
    if (edges.includes('bottom')) {
      safeStyle.paddingBottom = insets.bottom;
    }
    if (edges.includes('left')) {
      safeStyle.paddingLeft = insets.left;
    }
    if (edges.includes('right')) {
      safeStyle.paddingRight = insets.right;
    }
    
    return safeStyle;
  };

  const layoutBackgroundColor = backgroundColor || colors.background;

  const content = (
    <View 
      style={[
        styles.container,
        getSafeAreaStyle(),
        { backgroundColor: layoutBackgroundColor },
        style
      ]}
    >
      {children}
    </View>
  );

  return (
    <>
      <StatusBar
        barStyle={getStatusBarStyle()}
        backgroundColor={layoutBackgroundColor}
        translucent={Platform.OS === 'android'}
      />
      {keyboardAvoiding ? (
        <KeyboardAvoidingView
          style={[styles.container, { backgroundColor: layoutBackgroundColor }]}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
        >
          {content}
        </KeyboardAvoidingView>
      ) : (
        content
      )}
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});