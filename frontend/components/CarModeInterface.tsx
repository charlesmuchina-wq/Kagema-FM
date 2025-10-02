import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Platform,
  StatusBar,
  Alert,
  Vibration
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import * as Speech from 'expo-speech';
import { useKeepAwake } from 'expo-keep-awake';
import { useIntegration } from '../services/PlatformIntegrationService';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// Automotive UI Constants (following Android Auto guidelines)
const CAR_UI = {
  TOUCH_TARGET_SIZE: 80, // Minimum 76dp for car interfaces
  SPACING: 24, // Minimum 23dp spacing
  LARGE_TOUCH: 100, // For critical controls
  FONT_SIZE: {
    PRIMARY: 24,
    SECONDARY: 18,
    SMALL: 16
  },
  COLORS: {
    PRIMARY: '#FF6B6B',
    SECONDARY: '#4ECDC4',
    BACKGROUND: '#000000',
    SURFACE: '#1A1A1A',
    TEXT_PRIMARY: '#FFFFFF',
    TEXT_SECONDARY: '#CCCCCC',
    ACCENT: '#FFD93D',
    SUCCESS: '#4CAF50',
    WARNING: '#FF9800',
    ERROR: '#F44336'
  }
};

interface CarModeInterfaceProps {
  onExitCarMode: () => void;
  currentStation?: any;
  isPlaying: boolean;
  onPlayPause: () => void;
  onNextStation: () => void;
  onPreviousStation: () => void;
  stations: any[];
  onStationSelect: (station: any) => void;
}

export const CarModeInterface: React.FC<CarModeInterfaceProps> = ({
  onExitCarMode,
  currentStation,
  isPlaying,
  onPlayPause,
  onNextStation,
  onPreviousStation,
  stations,
  onStationSelect
}) => {
  useKeepAwake(); // Keep screen awake in car mode
  
  const [isDriving, setIsDriving] = useState(false);
  const [voiceListening, setVoiceListening] = useState(false);
  const [favoriteStations, setFavoriteStations] = useState<string[]>([]);
  const [currentView, setCurrentView] = useState<'player' | 'stations' | 'favorites'>('player');
  const voiceTimeoutRef = useRef<NodeJS.Timeout>();

  const { processVoiceCommand, startVoiceRecognition, stopVoiceRecognition } = useIntegration();

  useEffect(() => {
    // Set immersive car mode
    StatusBar.setHidden(true);
    
    return () => {
      StatusBar.setHidden(false);
      if (voiceTimeoutRef.current) {
        clearTimeout(voiceTimeoutRef.current);
      }
    };
  }, []);

  // Enhanced haptic feedback for car environment
  const carHaptic = () => {
    if (Platform.OS === 'ios') {
      Vibration.vibrate([0, 50]); // Short vibration
    } else {
      Vibration.vibrate(50);
    }
  };

  // Voice command handler
  const handleVoiceCommand = async () => {
    carHaptic();
    setVoiceListening(true);
    
    try {
      await startVoiceRecognition();
      
      // Auto-stop after 5 seconds
      voiceTimeoutRef.current = setTimeout(() => {
        stopVoiceCommand();
      }, 5000);
      
    } catch (error) {
      console.error('Voice command error:', error);
      stopVoiceCommand();
    }
  };

  const stopVoiceCommand = () => {
    setVoiceListening(false);
    stopVoiceRecognition();
    if (voiceTimeoutRef.current) {
      clearTimeout(voiceTimeoutRef.current);
    }
  };

  // Emergency exit with confirmation
  const handleExitCarMode = () => {
    carHaptic();
    Alert.alert(
      "Exit Car Mode",
      "Are you safely parked?",
      [
        { text: "Cancel", style: "cancel" },
        { text: "Exit", onPress: onExitCarMode }
      ]
    );
  };

  // Station management
  const handleStationChange = (station: any) => {
    carHaptic();
    onStationSelect(station);
    Speech.speak(`Now playing ${station.name}`, { rate: 1.2 });
  };

  const toggleFavorite = (stationId: string) => {
    carHaptic();
    setFavoriteStations(prev => 
      prev.includes(stationId) 
        ? prev.filter(id => id !== stationId)
        : [...prev, stationId]
    );
  };

  // Quick action buttons
  const QuickActionButton: React.FC<{
    icon: string;
    onPress: () => void;
    color?: string;
    size?: 'small' | 'medium' | 'large';
    disabled?: boolean;
  }> = ({ icon, onPress, color = CAR_UI.COLORS.PRIMARY, size = 'medium', disabled }) => {
    const buttonSize = size === 'large' ? CAR_UI.LARGE_TOUCH : 
                     size === 'small' ? CAR_UI.TOUCH_TARGET_SIZE - 20 : 
                     CAR_UI.TOUCH_TARGET_SIZE;
    
    return (
      <TouchableOpacity
        style={[
          styles.quickActionButton,
          { 
            width: buttonSize, 
            height: buttonSize,
            backgroundColor: disabled ? CAR_UI.COLORS.SURFACE : color + '20',
            borderColor: disabled ? CAR_UI.COLORS.TEXT_SECONDARY : color,
          }
        ]}
        onPress={onPress}
        disabled={disabled}
        activeOpacity={0.7}
      >
        <Ionicons 
          name={icon as any} 
          size={size === 'large' ? 32 : size === 'small' ? 20 : 28} 
          color={disabled ? CAR_UI.COLORS.TEXT_SECONDARY : color} 
        />
      </TouchableOpacity>
    );
  };

  // Main player view
  const PlayerView = () => (
    <View style={styles.playerContainer}>
      {/* Current Station Info */}
      <View style={styles.stationInfo}>
        <Text style={styles.stationName} numberOfLines={1}>
          {currentStation?.name || 'No Station Selected'}
        </Text>
        <Text style={styles.stationGenre} numberOfLines={1}>
          {currentStation?.genre || 'Select a station'}
        </Text>
      </View>

      {/* Main Controls */}
      <View style={styles.mainControls}>
        <QuickActionButton
          icon="play-skip-back"
          onPress={() => { carHaptic(); onPreviousStation(); }}
          size="large"
        />
        
        <QuickActionButton
          icon={isPlaying ? 'pause' : 'play'}
          onPress={() => { carHaptic(); onPlayPause(); }}
          color={CAR_UI.COLORS.ACCENT}
          size="large"
        />
        
        <QuickActionButton
          icon="play-skip-forward"
          onPress={() => { carHaptic(); onNextStation(); }}
          size="large"
        />
      </View>

      {/* Secondary Controls */}
      <View style={styles.secondaryControls}>
        <QuickActionButton
          icon={favoriteStations.includes(currentStation?.id) ? 'heart' : 'heart-outline'}
          onPress={() => currentStation && toggleFavorite(currentStation.id)}
          color={CAR_UI.COLORS.ERROR}
        />
        
        <QuickActionButton
          icon={voiceListening ? 'mic' : 'mic-outline'}
          onPress={handleVoiceCommand}
          color={voiceListening ? CAR_UI.COLORS.SUCCESS : CAR_UI.COLORS.SECONDARY}
        />
        
        <QuickActionButton
          icon="list"
          onPress={() => { carHaptic(); setCurrentView('stations'); }}
        />
      </View>
    </View>
  );

  // Station list view
  const StationsView = () => (
    <View style={styles.stationsContainer}>
      <View style={styles.viewHeader}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => { carHaptic(); setCurrentView('player'); }}
        >
          <Ionicons name="arrow-back" size={24} color={CAR_UI.COLORS.TEXT_PRIMARY} />
          <Text style={styles.backText}>Player</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.favoritesButton}
          onPress={() => { carHaptic(); setCurrentView('favorites'); }}
        >
          <Ionicons name="heart" size={24} color={CAR_UI.COLORS.ERROR} />
          <Text style={styles.favoritesText}>Favorites</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.stationsList}>
        {stations.slice(0, 6).map((station, index) => (
          <TouchableOpacity
            key={station.id || index}
            style={[
              styles.stationItem,
              currentStation?.id === station.id && styles.activeStation
            ]}
            onPress={() => handleStationChange(station)}
          >
            <View style={styles.stationContent}>
              <Text style={styles.stationItemName} numberOfLines={1}>
                {station.name}
              </Text>
              <Text style={styles.stationItemGenre} numberOfLines={1}>
                {station.genre}
              </Text>
            </View>
            
            <TouchableOpacity
              style={styles.favoriteButton}
              onPress={() => toggleFavorite(station.id)}
            >
              <Ionicons 
                name={favoriteStations.includes(station.id) ? 'heart' : 'heart-outline'} 
                size={20} 
                color={favoriteStations.includes(station.id) ? CAR_UI.COLORS.ERROR : CAR_UI.COLORS.TEXT_SECONDARY} 
              />
            </TouchableOpacity>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  // Favorites view
  const FavoritesView = () => {
    const favoriteStationList = stations.filter(station => favoriteStations.includes(station.id));
    
    return (
      <View style={styles.stationsContainer}>
        <View style={styles.viewHeader}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => { carHaptic(); setCurrentView('stations'); }}
          >
            <Ionicons name="arrow-back" size={24} color={CAR_UI.COLORS.TEXT_PRIMARY} />
            <Text style={styles.backText}>All Stations</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.stationsList}>
          {favoriteStationList.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="heart-outline" size={48} color={CAR_UI.COLORS.TEXT_SECONDARY} />
              <Text style={styles.emptyText}>No favorite stations yet</Text>
            </View>
          ) : (
            favoriteStationList.map((station, index) => (
              <TouchableOpacity
                key={station.id || index}
                style={[
                  styles.stationItem,
                  currentStation?.id === station.id && styles.activeStation
                ]}
                onPress={() => handleStationChange(station)}
              >
                <View style={styles.stationContent}>
                  <Text style={styles.stationItemName} numberOfLines={1}>
                    {station.name}
                  </Text>
                  <Text style={styles.stationItemGenre} numberOfLines={1}>
                    {station.genre}
                  </Text>
                </View>
                
                <TouchableOpacity
                  style={styles.favoriteButton}
                  onPress={() => toggleFavorite(station.id)}
                >
                  <Ionicons name="heart" size={20} color={CAR_UI.COLORS.ERROR} />
                </TouchableOpacity>
              </TouchableOpacity>
            ))
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Status Bar */}
      <View style={styles.statusBar}>
        <View style={styles.statusLeft}>
          <View style={[styles.statusDot, { backgroundColor: isPlaying ? CAR_UI.COLORS.SUCCESS : CAR_UI.COLORS.WARNING }]} />
          <Text style={styles.statusText}>
            {isPlaying ? 'PLAYING' : 'PAUSED'}
          </Text>
        </View>
        
        <TouchableOpacity
          style={styles.exitButton}
          onPress={handleExitCarMode}
        >
          <MaterialIcons name="exit-to-app" size={20} color={CAR_UI.COLORS.TEXT_PRIMARY} />
          <Text style={styles.exitText}>EXIT</Text>
        </TouchableOpacity>
      </View>

      {/* Main Content */}
      <View style={styles.mainContent}>
        {currentView === 'player' && <PlayerView />}
        {currentView === 'stations' && <StationsView />}
        {currentView === 'favorites' && <FavoritesView />}
      </View>

      {/* Voice Listening Indicator */}
      {voiceListening && (
        <View style={styles.voiceOverlay}>
          <View style={styles.voiceIndicator}>
            <Ionicons name="mic" size={32} color={CAR_UI.COLORS.SUCCESS} />
            <Text style={styles.voiceText}>Listening...</Text>
            <TouchableOpacity
              style={styles.voiceCancel}
              onPress={stopVoiceCommand}
            >
              <Text style={styles.voiceCancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: CAR_UI.COLORS.BACKGROUND,
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: CAR_UI.SPACING,
    paddingVertical: 12,
    backgroundColor: CAR_UI.COLORS.SURFACE,
    borderBottomWidth: 1,
    borderBottomColor: CAR_UI.COLORS.PRIMARY,
  },
  statusLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: CAR_UI.FONT_SIZE.SMALL,
    fontWeight: 'bold',
    color: CAR_UI.COLORS.TEXT_PRIMARY,
  },
  exitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: CAR_UI.COLORS.ERROR + '20',
    borderWidth: 1,
    borderColor: CAR_UI.COLORS.ERROR,
  },
  exitText: {
    fontSize: CAR_UI.FONT_SIZE.SMALL,
    fontWeight: 'bold',
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    marginLeft: 4,
  },
  mainContent: {
    flex: 1,
    padding: CAR_UI.SPACING,
  },
  playerContainer: {
    flex: 1,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  stationInfo: {
    alignItems: 'center',
    marginBottom: CAR_UI.SPACING * 2,
  },
  stationName: {
    fontSize: CAR_UI.FONT_SIZE.PRIMARY + 4,
    fontWeight: 'bold',
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    textAlign: 'center',
    marginBottom: 8,
  },
  stationGenre: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    color: CAR_UI.COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
  mainControls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    width: '100%',
    marginBottom: CAR_UI.SPACING * 2,
  },
  secondaryControls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    width: '80%',
  },
  quickActionButton: {
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 50,
    borderWidth: 2,
    margin: CAR_UI.SPACING / 2,
  },
  stationsContainer: {
    flex: 1,
  },
  viewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: CAR_UI.SPACING,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: CAR_UI.COLORS.SURFACE,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    backgroundColor: CAR_UI.COLORS.SURFACE,
  },
  backText: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    marginLeft: 8,
    fontWeight: 'bold',
  },
  favoritesButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    backgroundColor: CAR_UI.COLORS.SURFACE,
  },
  favoritesText: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    marginLeft: 8,
    fontWeight: 'bold',
  },
  stationsList: {
    flex: 1,
  },
  stationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: CAR_UI.SPACING,
    marginBottom: 12,
    borderRadius: 12,
    backgroundColor: CAR_UI.COLORS.SURFACE,
    borderWidth: 2,
    borderColor: 'transparent',
    minHeight: CAR_UI.TOUCH_TARGET_SIZE,
  },
  activeStation: {
    borderColor: CAR_UI.COLORS.PRIMARY,
    backgroundColor: CAR_UI.COLORS.PRIMARY + '10',
  },
  stationContent: {
    flex: 1,
    marginRight: 16,
  },
  stationItemName: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    fontWeight: 'bold',
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    marginBottom: 4,
  },
  stationItemGenre: {
    fontSize: CAR_UI.FONT_SIZE.SMALL,
    color: CAR_UI.COLORS.TEXT_SECONDARY,
  },
  favoriteButton: {
    padding: 12,
    borderRadius: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    color: CAR_UI.COLORS.TEXT_SECONDARY,
    marginTop: 16,
    textAlign: 'center',
  },
  voiceOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceIndicator: {
    backgroundColor: CAR_UI.COLORS.SURFACE,
    borderRadius: 16,
    padding: CAR_UI.SPACING * 2,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: CAR_UI.COLORS.SUCCESS,
  },
  voiceText: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    marginTop: 12,
    marginBottom: 16,
    fontWeight: 'bold',
  },
  voiceCancel: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: CAR_UI.COLORS.ERROR,
  },
  voiceCancelText: {
    fontSize: CAR_UI.FONT_SIZE.SECONDARY,
    color: CAR_UI.COLORS.TEXT_PRIMARY,
    fontWeight: 'bold',
  },
});

export default CarModeInterface;