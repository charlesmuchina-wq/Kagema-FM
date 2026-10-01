A full-width station button, at least `lp-button-height` tall: a position number, the station name in `lp-button`, a `lp-label` line beneath, and a play icon.

**You provide:** `name`, `meta` (country or language), `number` (his fixed position, 1 to 6), `playing`, `onSelect`, and `labels: {playing}`.

- Five or six rows, chosen for him, always in the same order, `lp-touch-gap` apart. The number lets him ask for "station three".
- The playing row carries a `lp-focus-ring` outline in `text-primary`, a check icon, and the word "Playing" in place of `meta`. Never signal it by `primary` alone.
- One tap plays. No swipe actions, no long-press menu, no favourite star on the row.
- Long names wrap to a second line and the row grows.
