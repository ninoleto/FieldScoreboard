# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.15**, local development build on `ocr/scoresight-match-clock`, starting from clean test.14 commit `b6427dd`. Earlier source history/packages and production settings are preserved. Field Timer was untouched.

**Do not publish test.15. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged until separately authorized publication.

Read [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.15.md) and [verification](docs/VERIFICATION-v0.1.0-test.15.md). Historical verification files remain intact.

## Completed change

- Both clock cards now use title/status/time, transport controls, exactly **−5s / −1s / +1s / +5s**, then a divider and Clock setup, with a full-width blue Set button last. Quick rows match and become 2×2 when needed; desktop Set buttons align without fixed-height padding.
- Match setup retains one-unit Minutes/Seconds steppers, Direction and its moved Output format. Shot setup retains Seconds, moved Output format, immediate 14s/24s/30s presets, Auto-hide and status/help. Auto-hide remains keyboard/touch accessible with readable text.
- Format changes remain immediate through the test.14 display path; duration/direction edits remain pending until Set. Foul display preferences stay under the preview (after primary controls when narrow). Both clocks remains separate; OCR stays last.
- Existing adjustment/Set/reset/preset handlers, clock engine, OCR ownership and persistence/draft protection are unchanged. At zero, countdown still completes; exceeding the seven-day adjustment limit is rejected. Numeric setup limits and one-unit increments are unchanged.
- Footer now reads **Field Scoreboard · Free & open source · Windows & Linux**. Project-separation instructions remain in developer documentation; Field Timer was untouched.
- Seven mappings, period recognition/OT, optional Free transform, test.14 toolbar/inspector, background transforms, authentication and the HTTP transport fix remain. No sliders.

## Source and verification

Application changes are scoped to embedded HTML/CSS and the test version. Existing app/renderer/OCR JavaScript and Go clock/API implementations are retained. `clock_quick_test.go` adds boundary/transport/ownership regressions; `test_clock_ui.py` exercises actual native requests and responsive controls with a simulated source. The existing display suite verifies that moved format controls still preserve live state, layout drafts, Save/Discard, presets and restart.

Go tests/vet/Linux race, full offline UI, native clock/display and seven-field OCR/period checks passed. Five widths, mouse/emulated touch/keyboard and native zoom were checked; screenshots were inspected. Extracted Windows/Linux HTTP/restart and 1,500-request transport suites passed with no reset recurrence. Packages passed integrity, inventory, embedded-asset, checksum, secret and documentation checks; final documentation-only packaging retains the tested binaries. See [test.15 verification](docs/VERIFICATION-v0.1.0-test.15.md) for completed checks and package evidence. Browser touch and overlay-page tests must remain distinct from physical touchscreen and OBS acceptance.

## Remaining checks and next steps

- Operator acceptance on the physical touchscreen and actual OBS, especially the final clock-card order, quick adjustments and setup/format distinction, using a separate portable configuration.
- Windows tray, real seven-field changes/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain unverified by automation. Preserve the scoped 2026-11-06 test.9 home OCR and test.8 Linux OBS Flatpak reports.
- Keep the test.10 intermittent connection reset and test.11 reproduction/fix in history; investigate any recurrence without hiding failures with retries.
- After acceptance, prepare **v0.1.0 normal release** with refreshed version/docs and separately authorized publication. Do not publish this build or create another public test/prerelease by default.
- Future optional work remains verified source freshness/confidence policy, multiple OCR sources and automatic sport rules. Preserve manual fallback, compatibility and authentication boundaries.
