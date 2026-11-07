# v0.1.0-test.13 — period recognition and display formats

Local development build, 2026-11-07, continuing from test.12 commit `c142d53`. Not published. Earlier packages and the public test.8 release remain unchanged. After operator acceptance, the intended public release remains **v0.1.0 as a normal release**, with separate publication authorization.

- **Period format** beside the manual Period / half controls and OT switch offers large Number, Ordinal and Quarter buttons with a single highlighted choice. Narrow layouts stack them. Keyboard arrows/Home/End select choices; Enter/Space activates a focused button. Existing installations default to Number.
- Period OCR accepts whole numeric values, correct ordinals and Q-prefixed values in 1–20. For example, 3, 3rd and Q3 all become numeric 3. Case and surrounding whitespace are ignored. Invalid suffixes, arbitrary text, signs, decimals and out-of-range values are rejected without clearing or clamping the period.
- Recognition and display are independent: source 3rd can display as Q3. The OCR card retains raw recognised text and explicitly labels the last accepted numeric period. Other OCR targets retain their existing parsing rules.
- Period remains numeric for exact entry, ± buttons and API/Companion commands. Format changes apply immediately without changing the number or manual/OCR ownership. Ordinals include 11th, 12th and 13th.
- OT overrides the display label. Turning it off restores the chosen format using the current number; OCR never toggles OT. Format persists in live configuration, outside layouts/presets, and survives game reset. Editor, preview and OBS share the formatted label, including transformed period elements.

Optional Free transform, all seven OCR mappings, the dark OCR section at the bottom of Live control, clock behavior, authentication and bounded HTTP action-body handling are preserved. No sliders were added. See the [user guide](USER_GUIDE.md), [OCR guide](OCR_PLAN.md) and [verification](VERIFICATION-v0.1.0-test.13.md).

Live testing read the operator's current 3rd source in an isolated scoreboard and verified all three formats; it did not control ScoreSight or the video source. Physical touchscreen, Windows tray, actual OBS, separate-machine LAN/Companion and venue acceptance remain operator checks.
