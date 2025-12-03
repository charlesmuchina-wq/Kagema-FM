import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function GlobeWebScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.title}>🌍 Interactive 3D Globe</Text>
        <View style={styles.placeholder} />
      </View>

      <View style={styles.globeFrame}>
        <iframe
          src="/globe.html"
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
          }}
          title="3D Radio Stations Globe"
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#FFFFFF',
    marginTop: 20,
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#8B92B0',
    textAlign: 'center',
    marginBottom: 20,
  },
  info: {
    fontSize: 14,
    color: '#8B92B0',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 40,
  },
  button: {
    backgroundColor: '#1E88E5',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 12,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
