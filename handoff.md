# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.14**, local development build on `ocr/scoresight-match-clock`, starting from clean test.13 commit `ea0daec`. Earlier source history/packages and production settings are preserved. Field Timer was untouched.

**Do not publish test.14. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged until separately authorized publication.

Read [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.14.md) and [verification](docs/VERIFICATION-v0.1.0-test.14.md). Historical verification files remain intact.

## Completed change

- OCR connection action uses red disconnected/lost/failed labels, pending Connecting and green Connected based on actual connection state. Pending checks cannot duplicate. Ownership locks have visible instructions; following and camera freshness remain separate.
- Editor selection/status sits above a balanced toolbar: Free transform left, background editing right, stacked in that order when narrow. Mode-specific help is below; Save/Discard remain separate. Optional handles, normal dragging and mutually exclusive selection are preserved.
- Inspector DOM/keyboard order: Match clock / Shot clock / Period; Home name / score / fouls; Away name / score / fouls.
- Scoreboard display moved to Live control: below preview on desktop, after primary controls on narrow screens, before final OCR. Foul styles/dot maximum and clock formats apply immediately and persist without saving a layout draft. Period format remains by Period/OT.
- Editor Save/Discard and position reset retain newer display options. Immediate display changes never save/discard geometry or change game values, clock state or OCR owners. Legacy configs/full-layout APIs and explicit preset loads retain appearance semantics.
- Seven mappings, period recognition/OT, optional Free transform, dark final OCR section, touch controls, clocks, image proportions, authentication and bounded HTTP transport fix remain. No sliders.

## Source and verification

`display.go` patches one preference through `POST /api/display` under the configuration mutex. Current editor saves use `PUT /api/layout?preserve_display=1`, merging the latest five preferences under that mutex. Their existing Layout representation retains config/preset compatibility. Browser writes are serialized, protect numeric drafts and keep current preferences in open geometry drafts. Explicit preset loading restores display preferences without replacing live values or the separate Period format.

Go/authentication/state-isolation tests, full offline UI, background/element suites, simulated seven-field OCR/period and focused display/toolbar/draft browser checks passed. All five widths, emulated touch/mouse/keyboard and native zoom were checked; screenshots were inspected. Extracted Windows/Linux packages passed HTTP, seven-field/period OCR, restart and 1,500 transport requests each without reset recurrence. Archives passed CRC, inventory, embedded-asset, SHA-256 and secret/personal-path checks; all documentation links passed. Documentation-only repackaging retains the tested executables. See the verification record for exact evidence. Browser overlay checks are not physical OBS tests.

## Remaining checks and next steps

- Operator acceptance on the physical touchscreen and actual OBS, especially connection labels, immediate display preferences and the editor toolbar, using a separate portable configuration.
- Windows tray, real seven-field changes/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain unverified by automation. Preserve the scoped 2026-11-06 test.9 home OCR and test.8 Linux OBS Flatpak reports.
- Keep the test.10 intermittent connection reset and test.11 reproduction/fix in history; investigate any recurrence without hiding failures with retries.
- After acceptance, prepare **v0.1.0 normal release** with refreshed version/docs and separately authorized publication. Do not publish this build or create another public test/prerelease by default.
- Future optional work remains verified source freshness/confidence policy, multiple OCR sources and automatic sport rules. Preserve manual fallback, compatibility and authentication boundaries.
