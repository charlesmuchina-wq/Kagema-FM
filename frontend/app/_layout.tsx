import { Stack } from 'expo-router';
import { ThemeProvider } from './theme-context';

export default function RootLayout() {
  return (
    <ThemeProvider>
      <Stack
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="favorites" />
        <Stack.Screen name="search" />
        <Stack.Screen name="map" />
        <Stack.Screen name="settings" />
        <Stack.Screen name="stations-browser" />
      </Stack>
    </ThemeProvider>
  );
}
