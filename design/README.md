# Kagema FM design

Design source for the low-vision redesign, exported from the Claude design system and Home mockup on 2026-09-21.

- `design-system/README.md` — the brand book; start with "Designing for low vision".
- `design-system/tokens.json` — every token in four themes: `dragon` (default, logo red on cream), `high-contrast`, `high-contrast-dark`, `batik` (the app as `frontend/constants/designTokens.ts` has it today). `tokens.css` is compiled from it.
- `design-system/components/` — five Large print components (PlayButton, NowPlayingCard, StationRow, MoreRow, MessageBanner) as plain web DOM with a preview and guidelines each. They are a specification to port to React Native, not app code.
- `design-system/assets/Logos/` — the dragon logo, the benchmark for the Dragon theme.
- `mockups/home/` — the Home screen for the low-vision listener in both high-contrast themes (`.dc.html` artboards) and rendered component sheets.

Live, editable copies: design system https://claude.ai/artifact/Y67gBnuT4v3NujxKTx35Za · Home mockup https://claude.ai/artifact/CS4ZArkZrTFWSFkQVkCHdV
