The one play/stop control: a `lp-play-button` disc in `primary` with an `on-primary` icon and the word "Play" or "Stop" beneath it in `lp-title`.

**You provide:** `playing` (start state), `onToggle(playing)`, and `labels: {play, stop}` in the listener's language. Call `setPlaying(v)` on the returned element when the stream state changes elsewhere.

- One per screen, centred, the largest thing on it. Never shrink it below `lp-play-button`.
- The word always shows; the icon alone is not enough. The shape changes too (triangle, square), so the state never rests on colour.
- Pressed is `primary-dark`, not opacity. A tap only: no long-press or double-tap behaviour.
- In React Native set `accessibilityRole="button"`, `accessibilityLabel` to the same word, and fire a sound and a vibration on each toggle.
