# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.11**, local development build on `ocr/scoresight-match-clock`. Started from clean test.10 commit `112b48f`; earlier source history and packages are preserved. Field Timer and production configuration were untouched.

**Do not publish test.11. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) stays unchanged until a separately authorized release task.

Read [AGENTS.md](AGENTS.md) first, then the [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.11.md) and [verification](docs/VERIFICATION-v0.1.0-test.11.md).

## Completed

- Seven independent OCR targets: match/shot clocks, home/away scores, home/away fouls, numeric period. Actual-name suggestions only; absent sources stay unconfigured/manual. One connection/worker and existing large card selectors, per-field status/hold/takeover, delayed-response protection and manual restart.
- Foul limits 0–30 and period limits 1–20. Invalid readings hold rather than clear/clamp. Fouls drive both numeric and dot styles. Numeric period updates preserve the OT flag; explicit OT off reveals the latest saved period. Manual ±/exact/API/Companion ownership guards and atomic game-reset rejection cover every overwritten field.
- OCR stays last in Live control. Only its outer card has the neutral #141414 background/subtle border; inner cards/controls/status colors are retained. Polling does not scroll or steal focus.
- Direct move/resize for all nine elements. Clear selected-element label, editor-only actual bounds and 56 px handles; proportional corners by default, unlocked side handles, precise Width/Height ± fields and Reset element size. Small fields use an expanded dotted handle guide without changing actual geometry. Field/background selection is mutually exclusive. No sliders.
- Optional element transform stores scale_x/scale_y/lock_aspect (.05–20). Actual text/dots scale around the alignment anchor; values grow naturally without a fixed clipping box. Legacy OBS output is unchanged without metadata. Shared renderer, logical 1920×1080 geometry, fonts/color/bold/visibility, nudge controls, polling-safe drafts, Save/Discard, presets, restart and deep-copy validation are retained.
- Investigated the test.10 Windows reset when it recurred. Unread optional action bodies reproduced resets/aborts on closing connections. Bounded body consumption now precedes action mutation/reply, after existing authentication. Empty/optional-body semantics remain compatible; no retries hide failures. Historical verification remains unchanged and the new record contains before/after evidence.

## Source and checks

OCR changes: `ocr.go`, engine guards, `web/ocr.js`/cards, `ocr_seven_test.go`, `ocr_seven_checks.py`. Element changes: optional model transform/deep cloning, `web/render.js`, new `web/elements.js`, editor integration/CSS and `element_transform_test.go`/`test_elements_ui.py`. Transport fix: `consumeActionBody` in `server.go`, `action_body_test.go`, `test_http_transport.py`.

Windows tests/vet/JS syntax and all three cross-builds passed. Final Linux tests/vet/race and native HTTP/OCR/1,500-request transport regression passed. Established UI/background checks and seven-field OCR browser checks passed at 375/500/1000/1440/1920. All nine element mouse/touch/anchor/value/dot/preset/restart and editor-preview-OBS geometry checks passed, including native 200%/400% zoom and keyboard resizing. Responsive screenshots were inspected. Direct test.10/test.11 OBS screenshot comparisons were pixel-equal for three legacy scenarios. Final archive/extracted-package checks and hashes are documented in the verification record and SHA256SUMS.txt.

The live source exposed Time, Home Score and Away Score. An isolated test.11 observed changing Time (40 samples/nine values), stable home 11 and away 101 (20 samples each), explicit follow/takeover and restart. Shot/foul/period mappings, deliberate source failures/pauses/resets and changing scores were simulated. Freshness is still unverified: /json supplies no detection timestamp or heartbeat. Never infer running state or video freshness from cached success.

## Manual evidence and next steps

- Preserve the scoped reports from 2026-11-06: test.9 match-clock OCR works in the operator’s home setup; test.8 Linux application/overlay works with OBS Flatpak. These are not venue validation or test.11 acceptance.
- Operator rehearsal: configure real foul/period/shot fields, try mixed ownership and atomic reset rejection, verify OT, manipulate all nine elements on the physical touchscreen, and inspect actual OBS output while values change. Use a separate portable folder/configuration.
- Still required: physical touchscreen, Windows tray, test.11 OBS, real capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue conditions/latency.
- After explicit acceptance, prepare **v0.1.0 normal release** with refreshed version/docs, verified packages/checksums and separately authorized publication. Do not create another public test/prerelease by default.
- Future optional work remains confidence/stability policy, upstream detection heartbeat support, multiple OCR sources and automatic sport rules. Preserve manual fallback and authentication boundaries.
