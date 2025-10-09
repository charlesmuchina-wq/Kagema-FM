import React from 'react';
import { ThemeProvider } from '../contexts/ThemeContext';
import { EnhancedMainApp } from '../components/EnhancedMainApp';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Enhanced Main App Entry Point with Theme Provider
export default function EnhancedMain() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <StatusBar style="auto" />
        <EnhancedMainApp />
      </ThemeProvider>
    </SafeAreaProvider>
  );
}