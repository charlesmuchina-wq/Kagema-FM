/**
 * AudioPlayerContext — a single, app-wide radio player.
 *
 * Previously `useAudioPlayer()` was called locally inside home.tsx only, so its
 * playback state (the loaded Audio.Sound, current station, isPlaying, volume,
 * metadata) lived on that one screen. Any other screen that wanted to start a
 * station would have created its OWN independent Audio.Sound instance, causing
 * overlapping audio and a "Now Playing" card that didn't reflect what was
 * actually playing.
 *
 * This provider calls the hook exactly once, high in the tree, and shares that
 * single instance with every screen through context. Playing a station from the
 * browser, search, or favorites now controls the same player the home card
 * shows — so play / stop / switch behave consistently everywhere.
 */
import React, { createContext, useContext } from 'react';
import { useAudioPlayer } from '../hooks/useAudioPlayer';

type AudioPlayerContextValue = ReturnType<typeof useAudioPlayer>;

const AudioPlayerContext = createContext<AudioPlayerContextValue | undefined>(
  undefined
);

export function AudioPlayerProvider({ children }: { children: React.ReactNode }) {
  const player = useAudioPlayer();
  return (
    <AudioPlayerContext.Provider value={player}>
      {children}
    </AudioPlayerContext.Provider>
  );
}

export function useAudioPlayerContext(): AudioPlayerContextValue {
  const context = useContext(AudioPlayerContext);
  if (context === undefined) {
    throw new Error(
      'useAudioPlayerContext must be used within an AudioPlayerProvider'
    );
  }
  return context;
}
