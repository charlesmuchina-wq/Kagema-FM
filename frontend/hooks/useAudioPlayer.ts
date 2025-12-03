import { useState, useEffect, useRef } from 'react';
import { Audio, AVPlaybackStatus } from 'expo-av';
import { Platform } from 'react-native';

interface Station {
  id: string;
  name: string;
  stream_url: string;
  call_sign?: string;
  standard_display_name?: string;
  country?: string;
}

interface NowPlayingMetadata {
  title: string;
  artist: string;
  album?: string;
  artwork?: string;
}

interface UseAudioPlayerReturn {
  isPlaying: boolean;
  isLoading: boolean;
  isBuffering: boolean;
  volume: number;
  currentStation: Station | null;
  nowPlayingMetadata: NowPlayingMetadata | null;
  error: string | null;
  playStation: (station: Station) => Promise<void>;
  pause: () => Promise<void>;
  resume: () => Promise<void>;
  stop: () => Promise<void>;
  setVolume: (volume: number) => Promise<void>;
  togglePlayPause: () => Promise<void>;
}

export const useAudioPlayer = (): UseAudioPlayerReturn => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [volume, setVolumeState] = useState(1.0);
  const [currentStation, setCurrentStation] = useState<Station | null>(null);
  const [nowPlayingMetadata, setNowPlayingMetadata] = useState<NowPlayingMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const soundRef = useRef<Audio.Sound | null>(null);
  const metadataIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize audio session
  useEffect(() => {
    const initAudio = async () => {
      try {
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: false,
          playsInSilentModeIOS: true,
          staysActiveInBackground: true,
          shouldDuckAndroid: true,
          playThroughEarpieceAndroid: false,
        });
      } catch (err) {
        console.error('Failed to initialize audio:', err);
      }
    };

    initAudio();

    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync();
      }
      if (metadataIntervalRef.current) {
        clearInterval(metadataIntervalRef.current);
      }
    };
  }, []);

  // Playback status update handler
  const onPlaybackStatusUpdate = (status: AVPlaybackStatus) => {
    if (status.isLoaded) {
      setIsPlaying(status.isPlaying);
      setIsBuffering(status.isBuffering);
      
      if (status.error) {
        console.error('Playback error:', status.error);
        setError('Playback error occurred');
      }
    } else {
      if (status.error) {
        console.error('Loading error:', status.error);
        setError('Failed to load stream');
      }
    }
  };

  // Fetch now playing metadata
  const fetchNowPlayingMetadata = async (station: Station) => {
    try {
      // In a real implementation, this would fetch from an API or parse ICY metadata
      // For now, we'll use the station information as metadata
      setNowPlayingMetadata({
        title: station.standard_display_name || station.name,
        artist: station.call_sign || station.country || 'Live Radio',
        album: 'Dragon KARAU AI Radio',
      });
      
      // TODO: Implement ICY metadata parsing for actual song info
      // This would parse the stream metadata to get current song/show info
    } catch (err) {
      console.error('Failed to fetch metadata:', err);
    }
  };

  // Start metadata polling
  const startMetadataPolling = (station: Station) => {
    // Initial fetch
    fetchNowPlayingMetadata(station);
    
    // Poll every 30 seconds for updated metadata
    if (metadataIntervalRef.current) {
      clearInterval(metadataIntervalRef.current);
    }
    
    metadataIntervalRef.current = setInterval(() => {
      fetchNowPlayingMetadata(station);
    }, 30000);
  };

  // Stop metadata polling
  const stopMetadataPolling = () => {
    if (metadataIntervalRef.current) {
      clearInterval(metadataIntervalRef.current);
      metadataIntervalRef.current = null;
    }
  };

  // Play a station
  const playStation = async (station: Station) => {
    try {
      setIsLoading(true);
      setError(null);

      // Stop current playback
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }

      // Create new sound instance
      const { sound } = await Audio.Sound.createAsync(
        { uri: station.stream_url },
        { 
          shouldPlay: true, 
          volume: volume,
          isLooping: false 
        },
        onPlaybackStatusUpdate
      );

      soundRef.current = sound;
      setCurrentStation(station);
      setIsPlaying(true);
      
      // Start metadata polling
      startMetadataPolling(station);
      
      console.log('✅ Playing station:', station.name);
    } catch (err) {
      console.error('❌ Failed to play station:', err);
      setError('Failed to play station. Please try another stream.');
      setIsPlaying(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Pause playback
  const pause = async () => {
    try {
      if (soundRef.current) {
        await soundRef.current.pauseAsync();
        setIsPlaying(false);
        stopMetadataPolling();
      }
    } catch (err) {
      console.error('Failed to pause:', err);
    }
  };

  // Resume playback
  const resume = async () => {
    try {
      if (soundRef.current) {
        await soundRef.current.playAsync();
        setIsPlaying(true);
        if (currentStation) {
          startMetadataPolling(currentStation);
        }
      }
    } catch (err) {
      console.error('Failed to resume:', err);
    }
  };

  // Stop playback
  const stop = async () => {
    try {
      if (soundRef.current) {
        await soundRef.current.stopAsync();
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }
      setIsPlaying(false);
      setCurrentStation(null);
      setNowPlayingMetadata(null);
      stopMetadataPolling();
    } catch (err) {
      console.error('Failed to stop:', err);
    }
  };

  // Set volume
  const setVolume = async (newVolume: number) => {
    try {
      const clampedVolume = Math.max(0, Math.min(1, newVolume));
      if (soundRef.current) {
        await soundRef.current.setVolumeAsync(clampedVolume);
      }
      setVolumeState(clampedVolume);
    } catch (err) {
      console.error('Failed to set volume:', err);
    }
  };

  // Toggle play/pause
  const togglePlayPause = async () => {
    if (isPlaying) {
      await pause();
    } else if (currentStation) {
      await resume();
    }
  };

  return {
    isPlaying,
    isLoading,
    isBuffering,
    volume,
    currentStation,
    nowPlayingMetadata,
    error,
    playStation,
    pause,
    resume,
    stop,
    setVolume,
    togglePlayPause,
  };
};
