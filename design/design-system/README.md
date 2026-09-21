Kagema FM is a world-radio mobile app (Expo, React Native), being redesigned so that a 100-year-old listener in Kenya with low vision can turn on his radio by himself. **The logo is the benchmark for the design**: a deep red dragon on warm cream. Four themes follow from that. **Dragon** is the brand as the logo sets it, red on cream, and is the default. **High contrast (cream)** and **High contrast (dark)** are the two builds to test with him. **Batik** records the app exactly as the code has it today (black, navy, Dragon Orange) and is there for reference while the app is migrated, not for new work. When you build anything for him, read "Designing for low vision" first; it overrides the sections below wherever they differ.

## Designing for low vision

The redesign has one purpose: a 100-year-old man with low vision must be able to turn on his radio by himself. Judge every screen by that.

**Colour.** Use a high-contrast theme. `high-contrast` is the logo's own world, near-black and deep red on cream; `high-contrast-dark` is light text on black, for eyes that suffer from glare. Which one he sees better is not known yet: try both with him and keep the winner. In both, every text colour is at least 7:1 on `background` and on `surface`. Surfaces are solid, never translucent, and are set apart by a `border-secondary` outline at `border-medium` or thicker, because surface and ground are close in tone. Labels on a `primary` fill are always `on-primary`. Never rely on colour alone: every state has a word and an icon. No text over photographs, no gradients behind text, no `opacity-muted` or `opacity-disabled` on anything he must read.

**Type.** Use the Large print group only: `lp-display` 48, `lp-title` 34, `lp-button` 28, `lp-body` 24, and nothing below `lp-label` 20. Weight 500 or heavier; no italics, no all-caps sentences, no tight tracking. Left-aligned, short lines, one idea per line. In React Native leave `allowFontScaling` on and do not cap `maxFontSizeMultiplier`, so the phone's own large-text setting still enlarges everything; let layouts wrap and scroll rather than truncate. Station names never end in an ellipsis.

**Touch.** Everything tappable is at least `lp-touch-target` (72px) with `lp-touch-gap` between neighbours; buttons and list rows are `lp-button-height`; the play/stop button is `lp-play-button` wide, centred, the biggest thing on the screen. Taps only: no swipes, long-presses, double-taps, pinches or drag handles. The 3D globe and the map are not for him. Accept a tap that lands slowly or slides a little.

**Structure.** One job per screen. Home is: what is playing, one play/stop button, and a short list of his stations (five or six, chosen for him) as full-width rows. Search, the globe, analytics and settings live behind one clearly labelled "More" row for whoever helps him. The same thing is always in the same place. Nothing times out, auto-advances or disappears; no toasts: messages stay until he dismisses them. Every icon has a text label beside it.

**Sound and touch feedback.** He may hear better than he sees: say the station name aloud when it starts, confirm play and stop with a distinct sound and a vibration, and speak errors in plain words ("No internet. Trying again."). Give every control an `accessibilityLabel` and `accessibilityRole` so TalkBack can read the app; the repository currently sets none. Keep the screen awake while the radio plays, and resume the last station on launch so that opening the app is enough.

**Components.** Build Home from the Large print components: MessageBanner (only when needed), NowPlayingCard, PlayButton, five or six StationRows, one MoreRow, in that order, top to bottom.

**Focus and state.** The selected or playing row carries a `lp-focus-ring` outline in `text-primary` plus the word "Playing"; do not signal it by colour alone. Motion is limited to a simple fade of 150ms; respect the system's reduce-motion setting.

**Language.** Labels must be short enough to fit at `lp-button` size in the language he reads; which language that is has not been stated, so ask before writing copy.

These sizes and colours are proposals made for him, not values from the code. Check them with him, on his phone, in his light, and change whatever he cannot see.

## Colour

- The brand is two colours taken from the logo: the red `primary` on the cream `background`. Everything else is a warm neutral. Build new work in the Dragon theme.
- `primary` is for the play button, the active tab, links and the one action that matters on a screen; pressed is `primary-dark`; labels on it are `on-primary`. One red focal point per view. Red is the brand, so it is never the only sign of an error: `status-error` always carries an icon and the word.
- Every screen sits on `background`. Cards, tiles and the now-playing card are `surface` with a `border-secondary` outline; chips and quiet fills are `surface-light`.
- `secondary` is for the second action beside a red one, and never outweighs it.
- The four `accent-*` colours exist only to tell feature tiles apart: each tile takes one as its 2px border and icon disc, with an `on-primary` icon.
- Text is `text-primary` for titles and copy and `text-secondary` for taglines and metadata. `text-disabled` and `text-hint` are dim on purpose: never put information a person needs in them.
- Borders: `border-secondary` by default, `border-primary` when selected or focused, `border-accent` on the now-playing card.
- Status colours always come with an icon or a word: `status-success` connected, `status-warning` buffering, `status-error` failed, `status-info` notices.
- The red and cream were measured from the logo JPEG (`#8d140f`, `#e9d9c0`), not supplied as brand values; replace them if the logo's designer has exact ones.
- Batik only: the app today is white text on black with an orange `primary`; its white-on-orange labels are 2.8:1 and its hint text 2.6:1. Those are the source's values, kept exact and flagged, and are reasons to migrate.

## Type

- The app sets no font family, so text renders in the device's system face. Do not introduce a brand font.
- Use the scale as named: `hero` 40 and `display` 32 with tight leading and -0.5px tracking for titles; `title-xxl` 20 for station and card names; `body-lg` 16 and `body-md` 14 for copy; `caption-sm` 12 bold for tile titles, tab labels and metadata; `caption-xs` 10 for badges.
- Weights in use are 400, 500, 600, 700, 800. Screens lean on 700 at small sizes; keep that punch.

## Space, shape, depth

- An 8-point grid: `space-xs` 4 through `space-xxxl` 64, base unit `space-md`. Screens pad `container-padding`; cards pad `space-lg`; tiles pad `space-md`.
- Anything tappable is at least `min-touch-target` tall and wide. Buttons are `button-height-md`, inputs `input-height-md`.
- Radii grow with the object: `radius-md` buttons and inputs, `radius-lg` cards, `radius-xl` feature tiles, `radius-round` pills and icon discs.
- Depth is `elevation-sm` to `elevation-xl`, Cards default to `elevation-md`. Shadows are faint in every theme, so separate surfaces with the `surface` fill and a border first.
- Layering follows the `z-*` scale; modals dim the screen with `overlay`.

## Motion

Durations are 150ms fast, 300ms normal, 500ms slow. Ease-out to enter, ease-in to exit, ease-in-out otherwise. Pressed controls drop to 70% opacity. For the low-vision listener a pressed control changes to `primary-dark` or a `text-primary` border instead: nothing he must read ever fades.

## Voice

Short, warm and global. A feature is a two-or-three-word title with a one-line tagline under it. The name is written "Kagema FM" in running text (the logo sets it as KAGEMA·FM, with the line "A Dragon Karau AI"); variants in the code are "Kagema FM Broadcasting" and "Kagema FM International".

## Logo

- Kagema FM has a logo: `kagema-fm-dragon-logo.jpg` in the Logos group. A red dragon coiled around a broadcasting microphone, over the lockup "KAGEMA·FM" with the line "A DRAGON KARAU AI" beneath.
- Use it whole: dragon, name and line together, on its own cream ground. It is a flat raster with the ground baked in, so never recolour it, cut the dragon out, or stretch it. Keep clear space around it of at least the height of the "FM" letters.
- On the Dragon and cream high-contrast themes the logo sits straight on `background`, which matches its own ground. On a dark theme place it as a cream panel with `radius-lg` or larger corners.
- The logo is the benchmark: `primary` and `background` in the Dragon theme are its red and cream.
- Where the logo cannot fit, set "Kagema FM" in plain type in `text-primary`.

## Iconography

Ionicons from `@expo/vector-icons`, outline set, `on-primary` on coloured discs, `text-secondary` when inactive and `primary` when active. Sizes follow `icon-xs` 16 to `icon-xxxl` 64; feature tiles use `icon-lg`. No emoji as icons.

## Not synced

- Components: the repository's seven components (BottomFeatureBar, ContentDisclaimer, ContentDisclaimerModal, CountryExplorerButton, FeatureTile, Globe3D, NowPlayingCard) are React Native and cannot run in a web preview; they were read for values only and none was rebuilt.
- Intentional additions: five Large print components (PlayButton, NowPlayingCard, StationRow, MoreRow, MessageBanner) were written for the low-vision Home screen. They are plain web DOM, a specification to port to React Native, not code from the repository. Their icons are simple drawn shapes standing in for Ionicons `play`, `stop`, `checkmark`, `hourglass`, `warning`, `information-circle`, `menu` and `chevron-forward`; use the Ionicons in the app.
- The repository's three files named `*logo*.jpg` are photographs, not the logo (see Imagery). The logo itself is not in the repository; it was supplied directly.
- `assets/fonts/SpaceMono-Regular.ttf` is committed but never referenced by any screen, so it was left out.
- `app/theme-context.tsx` defines a user-switchable trio (batik, dark, light) with different primaries (white, violet `#BB86FC`, violet `#6200EE`). It disagrees with `designTokens.ts`, which matches what the screens actually hard-code, so only `designTokens.ts` was brought in.
- The Dragon theme takes its red and cream from the logo, which the owner set as the benchmark; its other values were chosen to go with them. It, both high-contrast themes, `on-primary`, the Large print styles and the `lp-*` sizes were added by hand for the low-vision listener; none is in the repository, and the app sets no accessibility labels, roles or font-scaling props today.
- Text styles pair the source's separate size, weight, line-height and tracking scales; the source does not define the pairs. Animation timings have no token family and are described above.
