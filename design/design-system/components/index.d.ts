/** Plain DOM factories: each returns an element to append. No framework. */
export interface PlayButtonProps { /** Start in the playing state. */ playing?: boolean; onToggle?: (playing: boolean) => void; /** Words under the disc. */ labels?: { play?: string; stop?: string }; }
export function PlayButton(props?: PlayButtonProps): HTMLButtonElement & { setPlaying(v: boolean): void };
export interface NowPlayingCardProps { name: string; state?: 'playing' | 'buffering' | 'error' | 'stopped'; labels?: { heading?: string; headingStopped?: string; playing?: string; buffering?: string; error?: string; stopped?: string }; }
export function NowPlayingCard(props: NowPlayingCardProps): HTMLElement;
export interface StationRowProps { name: string; /** Country or language; replaced by the word "Playing" when playing. */ meta?: string; /** 1–6, his fixed position in the list. */ number?: number; playing?: boolean; onSelect?: (row: StationRowProps) => void; labels?: { playing?: string }; }
export function StationRow(props: StationRowProps): HTMLButtonElement;
export interface MoreRowProps { label?: string; hint?: string; onOpen?: () => void; }
export function MoreRow(props?: MoreRowProps): HTMLButtonElement;
export interface MessageBannerProps { kind?: 'error' | 'info'; title: string; body?: string; okLabel?: string; onDismiss?: () => void; }
export function MessageBanner(props: MessageBannerProps): HTMLElement;
