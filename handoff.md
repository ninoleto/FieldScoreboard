# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.16**, local development build on `ocr/scoresight-match-clock`, starting from clean test.15 commit `65c76c0`. Earlier source history/packages and production settings are preserved. Field Timer was untouched.

**Do not publish test.16. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged until separately authorized publication.

Read [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.16.md) and [verification](docs/VERIFICATION-v0.1.0-test.16.md). Historical verification files remain intact.

## Completed change

- Match **Duration presets: 5 / 8 / 10 / 12 / 20 min** fill pending Minutes and Seconds (0). No live action is sent before Set, including while running; pending direction, immediate output format, shot clock, other game values and OCR ownership stay unchanged. Matching drafts highlight; custom numeric entry and polling protection remain. Set is still last, full width and guarded by manual ownership. Shot presets and quick rows retain test.15 behavior.
- **Bold** is now a large switch in a pinned Font-picker row outside the scrolling list. Toggling leaves the dialog open, and the closed control shows family plus Bold/Regular. Family and weight preserve each other, using the selected layout draft, Save/Discard, profiles and existing persistence. The standalone checkbox is removed. Hidden Font-only controls add no keyboard stops to other dialogs.
- Changes are scoped to HTML/CSS/JavaScript and version metadata; clock/state/API/OCR/renderer logic and persistence schemas are unchanged. Seven OCR mappings, period/OT formats, optional Free transform, background transforms, live display draft protection, authentication and the HTTP transport fix remain. No sliders.

## Source and verification

`ui_duration_presets.py` extends the native clock suite with pending-only/no-live-write tests. `test_font_ui.py` covers scrolling, touch/keyboard/focus, element changes, Save/Discard, profiles, restart and transformed editor/preview/overlay geometry. The existing element suite uses the new Font-picker switch. See [test.16 verification](docs/VERIFICATION-v0.1.0-test.16.md) for completed regression/package evidence and manual limitations. Browser emulation must remain distinct from physical touchscreen and OBS acceptance.

Go tests/vet/Linux race, JavaScript checks, full offline UI, native clock/font/display/background/element and seven-field OCR/period suites passed. All five widths and native 200%/400% zoom were checked; screenshots were inspected. Extracted Windows/Linux HTTP/restart and 1,500-request transport suites passed with no reset recurrence. Archives passed integrity, inventory, checksums, embedded-assets, secret and documentation checks. Final documentation-only repackaging preserves tested executable bytes. Local Windows/Linux/source ZIPs and `SHA256SUMS.txt` are under `releases/v0.1.0-test.16/` outside the checkout; earlier packages remain intact.

## Remaining checks and next steps

- Operator acceptance on the physical touchscreen and actual OBS, especially pending match presets and the Font/Bold picker, using a separate portable configuration.
- Windows tray, real seven-field changes/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain unverified by automation. Preserve the scoped 2026-11-06 test.9 home OCR and test.8 Linux OBS Flatpak reports.
- Keep the test.10 intermittent connection reset and test.11 reproduction/fix in history; investigate any recurrence without hiding failures with retries.
- After acceptance, prepare **v0.1.0 normal release** with refreshed version/docs and separately authorized publication. Do not publish this build or create another public test/prerelease by default.
- Future optional work remains verified source freshness/confidence policy, multiple OCR sources and automatic sport rules. Preserve manual fallback, compatibility and authentication boundaries.
