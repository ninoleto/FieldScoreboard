# v0.1.0-test.15 — final clock panels

Local development build from test.14 (`b6427dd`); do not publish. The intended public version after acceptance remains **v0.1.0**, a normal release.

- Both clocks now have exactly **−5s / −1s / +1s / +5s** immediately beneath Start / Resume, Pause, Stop and Reset. Matching large buttons wrap to 2×2 on narrow screens.
- A divided **Clock setup** section follows. Match: Minutes, Seconds, Direction and Output format. Shot: Seconds, Output format, 14s/24s/30s presets, Auto-hide and explanatory/status text. Each card ends with a full-width blue Set button, aligned on desktop.
- Output formats moved from Scoreboard display into their clock cards and still apply immediately. Duration/direction wait for Set; one-unit setup steppers and immediate shot presets retain their behavior. Foul display preferences remain beneath the live preview; Both clocks and the final OCR section remain separate.
- Quick adjustments use existing independent clock actions. Countdown completes at zero; adjustments beyond seven days reject without changing the value. Running/paused behavior, OCR restrictions, shot reset/presets, immediate preference persistence and layout-draft protection remain.
- Footer: **Field Scoreboard · Free & open source · Windows & Linux**. Developer project-separation rules remain intact.

See [verification](VERIFICATION-v0.1.0-test.15.md) and [user guide](USER_GUIDE.md). Seven-field OCR, period formats, optional Free transform and the HTTP transport fix are preserved. No sliders. Physical touchscreen, actual OBS, tray, real capture, LAN/Companion and venue checks remain operator work.
