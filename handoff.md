# Field Scoreboard handoff

Checkpoint: **2026-11-06**, **v0.1.0-test.9**, local OCR development build.
Branch: `ocr/scoresight-match-clock`. Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged. **Do not publish this OCR build without a new instruction.**

Read [AGENTS.md](AGENTS.md) first. Work began from a clean test.8 tree; no user changes were overwritten. Field Timer remains separate and untouched.

## Completed

- Working ScoreSight match-clock connector with address/check, dynamic large field dialog (Time preferred), recognised/accepted values and clear connection/reading warnings. Controls remain touch-friendly on desktop and narrow screens; no sliders.
- Single Go polling worker (~5 Hz, 800 ms timeout, bounded payload, no redirect/proxy/credential forwarding). ScoreSight /json state and strict MM:SS validation gate accepted readings.
- Explicit OCR ownership supplies the effective match time while the internal clock stays held. Pauses/resets reflect subsequent readings; bad/missing/disconnected readings keep the last value.
- Immediate manual takeover retains the time paused and rejects late responses. Following again requires an explicit action. Restart begins manual/Ready and disconnected; only address/field settings persist.
- Scores/fouls/period/names and shot timing are not mapped. Shot controls stay independent; shot resets stay Ready during OCR ownership because the source's running state is unknown. Auto-hide derives from the effective match value.
- Manual match/combined commands are guarded while following. Existing authentication protects OCR APIs; the public overlay does not receive OCR addresses, field lists or warnings.
- Retained test.8 touch/numeric controls, Fine position 5/10/20 default 5 and X/Y ±1, background proportions/editing, Save/Discard, layout coordinates, presets and game/config compatibility.

## Source and evidence

See [connector guide](docs/OCR_PLAN.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.9.md) and [verification](docs/VERIFICATION-v0.1.0-test.9.md). Implementation is in `ocr.go`, engine/server integration and `web/ocr.js`; tests include `ocr_test.go` and `scripts/test_ocr.py`.

Completed checks: Windows Go tests/vet/JS syntax and cross-builds; final Linux Go tests/vet/race; existing full UI/zoom and image regressions; new OCR browser checks at all five widths and narrow/1920×1080 screenshot review; extracted Windows/Linux HTTP and simulated OCR smoke/restart; source/archive integrity, documentation links and secret scans. Local Windows/Linux/source ZIPs and SHA256SUMS.txt are prepared for test.9. Exact results and manual limits are in the verification record.

The live ScoreSight v0.4.3 endpoint was read directly and then exercised through an isolated native build. It returned Time, MM:SS and Success/SameNoChange. Forty observations over eight seconds included nine distinct times. Follow/takeover/restart and untouched unrelated fields were checked live. Source pause/reset, rejection, missing fields, disconnection/recovery and delayed responses were simulated.

**Freshness is unavailable:** this source endpoint has no detection timestamp or video heartbeat. HTTP success and unchanged/cached responses cannot prove live video. The UI says so and warns after three seconds without a numeric change. Do not replace this with a false “live” indicator or an extrapolated countdown.

## Remaining operator checks and next steps

- Physical touchscreen, Windows tray, real OBS rendering of OCR output, deliberate live-source pauses/resets, hardware capture loss/freeze and live-event accuracy/latency.
- Separate-machine LAN/firewall and real Companion devices. Linux native automated checks do not establish OBS or touchscreen behavior.
- The owner reported the Linux application/overlay working with OBS Flatpak on 2026-11-06 for test.8 only; do not extend that statement to test.9 or other manual tests.
- Rehearse with an isolated configuration before using live production data. Keep test.8 as the published checkpoint.
- Additional OCR fields, source heartbeat support when an upstream API supplies it, confidence/stability policy and automatic sport rules remain future work. Follow the existing manual-override, persistence and security contracts.
