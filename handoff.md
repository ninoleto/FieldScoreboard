# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.17**, local development build on `ocr/scoresight-match-clock`, starting from clean test.16 commit `1ab76d5`. Earlier source history/packages and production settings are preserved. Field Timer was untouched.

**Do not publish test.17. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged until separately authorized publication.

Read [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.17.md) and [verification](docs/VERIFICATION-v0.1.0-test.17.md). Historical verification files remain intact.

## Completed change

- Shot card order: title/status/time, transport, −5s/−1s/+1s/+5s, **Duration presets / Applies immediately**, 14s/24s/30s, resume explanation directly beneath, divider/Clock setup, Seconds/Output format, Auto-hide/status, final full-width Set. Setup help now says **Duration applies with Set. Output format applies immediately.** Old duplicate placements are removed.
- Both Live team names have bold 21 px labels, full-width inputs at least 64 px high with 24 px text, comfortable gaps/padding and a clear focus border. This does not change overlay name styling. Existing validation, input limits, change events and active-input polling protection are unchanged; names remain editable during score/foul OCR.
- Changes are limited to HTML/CSS and version metadata. App/renderer/OCR JavaScript, clock/API logic and persistence schemas are unchanged. Immediate shot presets, automatic resume, OCR guards, pending match presets, quick rows, Font-picker Bold, seven OCR fields, optional Free transform, period/OT, display draft protection and the HTTP transport fix remain. No automatic basketball rules or sliders.

## Source and verification

`ui_shot_presets.py` extends the native clock suite with order, sizing and all three presets while main is paused/running. OCR tests assert disabled presets and existing API rejection. `test_team_names_ui.py` checks sizes, mouse/touch emulation/keyboard, long names, trim/empty validation, real background updates during active selection/typing, OCR availability and unchanged preview/overlay styling. See [test.17 verification](docs/VERIFICATION-v0.1.0-test.17.md) for completed regression/package evidence and historical checks reused for unchanged implementations.

Go tests/vet/Linux race, JavaScript checks, full offline UI, native clock/name/display and seven-field OCR/period suites passed. All five widths, mouse/emulated touch/keyboard and native 200%/400% zoom were checked; narrow/desktop screenshots were inspected. Extracted Windows/Linux HTTP/restart and 1,500-request transport suites passed with no reset recurrence. Archives passed integrity, inventory, embedded-assets, checksums, secret and documentation checks. Final documentation-only packaging preserves tested executable bytes. Windows/Linux/source ZIPs plus `SHA256SUMS.txt` are under `releases/v0.1.0-test.17/` outside the checkout; earlier builds remain intact. No new physical touchscreen or OBS acceptance is claimed.

## Remaining checks and next steps

- Operator acceptance on the physical touchscreen and actual OBS, especially the reordered shot presets and enlarged name fields, using a separate portable configuration.
- Windows tray, real seven-field changes/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain unverified by automation. Preserve the scoped 2026-11-06 test.9 home OCR and test.8 Linux OBS Flatpak reports.
- Keep the test.10 intermittent connection reset and test.11 reproduction/fix in history; investigate any recurrence without hiding failures with retries.
- After acceptance, prepare **v0.1.0 normal release** with refreshed version/docs and separately authorized publication. Do not publish this build or create another public test/prerelease by default.
- Future optional work remains verified source freshness/confidence policy, multiple OCR sources and automatic sport rules. Preserve manual fallback, compatibility and authentication boundaries.
