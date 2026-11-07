# v0.1.0-test.17 — shot presets and team-name controls

Local development build from test.16 (`1ab76d5`); do not publish. After acceptance, the intended public version remains **v0.1.0**, a normal release.

- The shot card now places **Duration presets**, **Applies immediately** and large **14s / 24s / 30s** buttons directly after its quick-adjustment row. The existing automatic-resume explanation sits directly below these buttons. A divider then introduces **Clock setup**, with Seconds, Output format and Auto-hide/status. The full-width **Set shot clock** button stays last. Setup help is **Duration applies with Set. Output format applies immediately.**
- Both Live **Home team / Away team** controls have bold 21 px labels and full-width name inputs at least 64 px high, with 24 px text, more spacing and a clear focus border. Scoreboard overlay name typography, sizes and positions are unchanged.
- Existing name validation, 32-character input limit, commit behavior and active-edit polling protection remain. Names stay editable while scores/fouls follow OCR. Shot presets still apply immediately, resume only if match time is internally running and respect OCR ownership. Match presets remain pending until Set. Both quick rows are unchanged. No new basketball rules or clock logic.

See [verification](VERIFICATION-v0.1.0-test.17.md) and the [user guide](USER_GUIDE.md). Physical touchscreen, actual OBS, tray and venue acceptance remain operator checks. Earlier builds and the published release are preserved.
