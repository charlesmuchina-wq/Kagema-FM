import { Stack } from 'expo-router';
import { ThemeProvider } from './theme-context';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { Ionicons } from '@expo/vector-icons';

// Keep the splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    ...Ionicons.font,
  });

  useEffect(() => {
    if (fontsLoaded || fontError) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded, fontError]);

  if (!fontsLoaded && !fontError) {
    return null;
  }

  return (
    <ThemeProvider>
      <Stack
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="home" />
        <Stack.Screen name="globe" />
        <Stack.Screen name="search" />
        <Stack.Screen name="analytics" />
        <Stack.Screen name="feedback" />
        <Stack.Screen name="country-explorer" />
        <Stack.Screen name="favorites" />
        <Stack.Screen name="map" />
        <Stack.Screen name="settings" />
        <Stack.Screen name="stations-browser" />
      </Stack>
    </ThemeProvider>
  );
}
