A message that stays until he dismisses it; it replaces toasts. A `surface` card with a `border-thick` outline in `status-error` or `status-info`, an icon and title in `lp-button`, a body in `lp-body`, and an OK button at least `lp-touch-target` tall in `primary` with an `on-primary` label.

**You provide:** `kind` (`error` or `info`), `title`, `body`, `okLabel`, `onDismiss`.

- Never auto-dismiss. One at a time, placed above the NowPlayingCard so nothing else moves.
- Plain words, one idea per line, and speak the same words aloud.
- If the app can recover by itself (a dropped stream), say so: "Trying again. The radio will start by itself."
