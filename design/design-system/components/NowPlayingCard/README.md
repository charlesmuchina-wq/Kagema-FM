Says what is on and whether it is working: a `surface` card with a `border-accent` outline at `border-thick`, the station name in `lp-title`, and one state line with an icon and words.

**You provide:** `name`, `state` (`playing`, `buffering`, `error`, `stopped`) and `labels` for the heading and each state in the listener's language.

- Top of Home, above the PlayButton, always in the same place.
- Each state has its own icon and its own sentence; `status-success`, `status-warning` and `status-error` only tint them. Success and error are not separable by hue, so never drop the words.
- Errors are plain sentences ("No internet. Trying again.") and are also spoken aloud. The card never hides or times out.
- The name wraps; it never ends in an ellipsis.
