# v0.1.0-test.16 verification

Date: 2026-11-07. Started from clean test.15 commit `65c76c0` on `ocr/scoresight-match-clock`. Isolated processes/configurations and simulated sources; Field Timer and production settings untouched. No publication.

## Focused checks

Native browser clock checks at 375/500/1000/1440/1920 px exercised all five match-duration presets while paused and running. Presets/custom drafts issued no live writes; minutes/seconds, highlight, polling/navigation protection and pending direction/immediate format were checked. Other clock/game/OT/layout values and OCR ownership stayed unchanged. Set applied the pending duration/direction through the existing action. OCR-owned match setup could be prepared but Set stayed disabled, without changing effective values. Existing quick adjustments, zero/upper boundaries, shot presets/reset, transport, auto-hide and restart checks passed.

The native Font suite passed all five widths: family/weight independence, pinned Bold row during font-list scrolling, switch touch/Space/Enter without closing, closed labels, Escape/Close focus restoration, focus trapping and no hidden-row tab stop in other dialogs. Element switching, navigation, Save/Discard, layout preset reload and restart retained correct draft/saved styling. Transformed editor, saved preview and overlay style/geometry agreed. Narrow, short-height and desktop screenshots, including maximized 1920×1080 clock panels, were inspected. Touch is browser emulation.

Production changes are limited to embedded HTML/CSS/JavaScript and version metadata. Go clock/state/API, OCR, renderer, configuration and preset schemas are unchanged.

## Regression and package evidence

Windows Go tests/vet, all embedded JavaScript syntax checks and Windows GUI/console/Linux builds passed. Full offline UI passed all five widths, large dialogs/dynamic sources, 23 numeric groups, drafts, focus, emulated touch/scrolling, Fine position, duplicate-ID/overflow checks and native 200%/400% zoom. All-nine element and background suites passed movement/resize, transforms, legacy graphics, clipping/transparency, Save/Discard, presets, restart and shared geometry. Seven-field OCR/period simulations passed ownership, independent validation, delayed takeover, connection transitions/loss/recovery, strict period parsing/formats, OT, restart and final-section order. No new real-source observation is claimed.

Final source passed native Linux Go tests/vet/race with a C compiler in an isolated Alpine VM. Native display/toolbar checks passed all five widths, immediate preview/overlay rendering, stale layout saves, Save/Discard, position reset, queued/delayed writes, presets and restart.

Extracted Windows/Linux packages passed HTTP startup/API/configuration/restart checks and **1,500 transport requests each**, without retries or connection resets. Linux native seven-field OCR/period simulations and restart passed. Windows browser tests used the exact executable bytes included in the archives. The historical connection reset did not recur.

All three ZIPs passed CRC, manifest SHA-256, inventory, executable-format, embedded-asset and documentation checks. Expanded Windows/Linux/source contents passed Gitleaks and personal-path/local-data review. 95 relative documentation links/anchors and 11 external HTTPS links passed. Final documentation-only repackaging retains the tested executable bytes and regenerates hashes; source packaging includes all new tests. Earlier release files and published main/test.8 Git checkpoints remain unchanged. Final ZIPs and `SHA256SUMS.txt` are delivered in the local `releases/v0.1.0-test.16/` folder outside the checkout; no publication.

## Historical evidence and manual checks

Preserve the [test.10 Windows reset history](VERIFICATION-v0.1.0-test.10.md) and [test.11 reproduction/fix](VERIFICATION-v0.1.0-test.11.md); investigate any recurrence without retries masking failures. The transport implementation remains unchanged.

The user-reported 2026-11-06 test.9 home match-clock OCR and test.8 Linux OBS Flatpak smoke tests remain scoped historical reports, not venue validation or test.16 acceptance. No new physical hardware test is claimed. Operator checks remain physical touchscreen ergonomics (especially presets and the Font/Bold picker), actual OBS rendering, Windows tray, real capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and live-event accuracy/latency. Cached successful HTTP responses cannot establish fresh video.

Keep test.16 local. After acceptance, prepare v0.1.0 as a normal release with separately authorized publication.
