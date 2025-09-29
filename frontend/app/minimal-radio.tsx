import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Minimal working version - bypasses all complex state dependencies
const MinimalRadioApp = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [stationInfo, setStationInfo] = useState({
    name: 'Kagema FM',
    location: 'Nairobi, Kenya',
    frequency: '101.5 FM',
    streamUrl: 'http://ice1.somafm.com/groovesalad-256-mp3'
  });
  const [newsArticles, setNewsArticles] = useState([]);
  const [musicTracks, setMusicTracks] = useState([]);
  const [audio, setAudio] = useState(null);

  useEffect(() => {
    loadContent();
    initializeAudio();
  }, []);

  const initializeAudio = () => {
    try {
      // Initialize HTML5 Audio for web
      const audioElement = new Audio();
      audioElement.crossOrigin = "anonymous";
      setAudio(audioElement);
      console.log('✅ Audio initialized for minimal app');
    } catch (error) {
      console.error('Audio initialization error:', error);
    }
  };

  const loadContent = async () => {
    try {
      setIsLoading(true);
      console.log('🔄 Loading content for minimal app...');

      // Load personalized content directly
      const response = await fetch('/api/personalized-content/multilingual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: { latitude: -1.286389, longitude: 36.817223 },
          preferences: {
            interests: ['radio', 'music', 'news'],
            favorite_genres: ['general'],
            location: 'Nairobi',
            age_group: 'adult',
            preferred_language: 'auto'
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Content loaded successfully:', data);

        // Update station info
        if (data.radio_streams?.main_station) {
          setStationInfo({
            name: data.radio_streams.main_station.name,
            location: data.location_info?.city + ', ' + data.location_info?.country || 'Nairobi, Kenya',
            frequency: data.radio_streams.main_station.frequency,
            streamUrl: data.radio_streams.main_station.streamUrl
          });
        }

        // Update news
        if (data.news?.articles) {
          setNewsArticles(data.news.articles);
        }

        // Update music
        if (data.music?.tracks) {
          setMusicTracks(data.music.tracks);
        }
      } else {
        console.error('Failed to load content:', response.status);
      }
    } catch (error) {
      console.error('Content loading error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlay = async () => {
    if (!audio || !stationInfo.streamUrl) return;

    try {
      setIsLoading(true);
      
      if (isPlaying) {
        // Pause
        audio.pause();
        setIsPlaying(false);
        console.log('⏸️ Radio paused');
      } else {
        // Play
        audio.src = stationInfo.streamUrl;
        await audio.play();
        setIsPlaying(true);
        console.log('▶️ Radio playing:', stationInfo.streamUrl);

        // Update media session
        if ('mediaSession' in navigator) {
          navigator.mediaSession.metadata = new MediaMetadata({
            title: stationInfo.name,
            artist: 'Live Radio',
            album: stationInfo.location,
          });
        }
      }
    } catch (error) {
      console.error('Playback error:', error);
      Alert.alert('Playback Error', 'Unable to connect to radio stream.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Kagema FM</Text>
        <Text style={styles.subtitle}>Minimal Radio Player</Text>
      </View>

      {/* Radio Player */}
      <View style={styles.playerContainer}>
        <View style={styles.stationInfo}>
          <Text style={styles.stationName}>{stationInfo.name}</Text>
          <Text style={styles.stationLocation}>{stationInfo.location}</Text>
          <Text style={styles.stationFreq}>{stationInfo.frequency}</Text>
        </View>

        <TouchableOpacity 
          style={[styles.playButton, isPlaying && styles.playButtonActive]}
          onPress={handlePlay}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Ionicons 
              name={isPlaying ? "pause" : "play"} 
              size={32} 
              color="#fff" 
            />
          )}
        </TouchableOpacity>
      </View>

      {/* News Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📰 News ({newsArticles.length})</Text>
        {newsArticles.slice(0, 3).map((article, index) => (
          <View key={index} style={styles.newsItem}>
            <Text style={styles.newsTitle}>{article.title}</Text>
            <Text style={styles.newsSource}>{article.source}</Text>
          </View>
        ))}
      </View>

      {/* Music Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎵 Music ({musicTracks.length})</Text>
        {musicTracks.slice(0, 3).map((track, index) => (
          <View key={index} style={styles.musicItem}>
            <Text style={styles.trackName}>{track.name}</Text>
            <Text style={styles.artistName}>{track.artists?.join(', ')}</Text>
          </View>
        ))}
      </View>

      <TouchableOpacity style={styles.refreshButton} onPress={loadContent}>
        <Text style={styles.refreshText}>🔄 Refresh Content</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ff6b6b',
  },
  subtitle: {
    fontSize: 16,
    color: '#ccc',
    marginTop: 5,
  },
  playerContainer: {
    backgroundColor: '#2d2d54',
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    marginBottom: 20,
  },
  stationInfo: {
    alignItems: 'center',
    marginBottom: 20,
  },
  stationName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  stationLocation: {
    fontSize: 16,
    color: '#ccc',
    marginTop: 5,
  },
  stationFreq: {
    fontSize: 14,
    color: '#ff6b6b',
    marginTop: 5,
  },
  playButton: {
    backgroundColor: '#ff6b6b',
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  playButtonActive: {
    backgroundColor: '#4CAF50',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
  },
  newsItem: {
    backgroundColor: '#2d2d54',
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  newsTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  newsSource: {
    color: '#ccc',
    fontSize: 12,
    marginTop: 5,
  },
  musicItem: {
    backgroundColor: '#2d2d54',
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  trackName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  artistName: {
    color: '#ccc',
    fontSize: 12,
    marginTop: 5,
  },
  refreshButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20,
  },
  refreshText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default MinimalRadioApp;