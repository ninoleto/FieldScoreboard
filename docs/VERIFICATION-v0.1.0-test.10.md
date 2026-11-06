# v0.1.0-test.10 verification

Date: 2026-11-06. Local OCR branch; no publication. Field Timer and production configuration were not modified. Tests used temporary configurations, generated graphics and separate ports.

## Automated checks

- Windows: Go tests/vet, syntax checks for every embedded JavaScript file and CGO-free Windows GUI/console + Linux amd64 cross-builds passed.
- Linux: final Go tests/vet/race passed in an isolated Alpine Linux 3.22.8 VM with Go 1.24.13/GCC; Windows builds used Go 1.27.3. Native package smoke results are recorded below.
- Go OCR regressions: strict per-target limits/statuses, valid zeros, malformed/duplicate wire fields isolated from other targets, one bounded non-overlapping poll worker, timeouts/recovery, no credential forwarding/redirects, authentication and sanitized overlay privacy.
- Multi-field ownership: simultaneous and mixed updates; manual/API guards for exact scores, adjustments, clock transports/Set and combined actions; atomic game reset rejection; delayed response after individual takeover/re-follow; no inferred main running state; independent shot reset/resume; effective auto-hide; legacy test.9 mapping migration, explicit unconfiguration, saved mappings/scores and manual restart.
- Native simulated OCR integration: source pauses/resets, missing/rejected/invalid values, connection loss/recovery, valid zeros, mixed ownership and delayed takeover passed on Windows and Linux. The sanitized overlay receives all four effective values.
- Browser OCR checks passed at 375, 500, 1000, 1440 and 1920 px: bottom DOM/visual order while connected, following and disconnected; four large selectors, dynamic options, native tab-stop removal, focus restoration, keyboard and emulated touch, address drafts, readable values, duplicate IDs, clipping/overflow and no opening/polling focus or scroll jumps. A held older browser response cannot repaint OCR ownership after takeover. Effective 200%/400% zoom layouts passed.
- Established UI regression: all 11 original selectors, numeric groups, duration drafts/carry/borrow, navigation, native 200%/400% browser zoom, exact-value entry and Fine position 5/10/20 with all four directions/boundaries passed. X/Y ± remains 1 px.
- Image regression: square, portrait, wide banner and 1920×1080 PNG/JPG/WebP; fitting/modes/proportions, unlocked controls, clipping/alpha, direct manipulation, drafts, Save/Discard, presets, legacy transform behavior, restart and shared editor/preview/overlay rendering passed.
- Native Windows HTTP regression passed: independent/combined clocks, OT, shot auto-hide, SSE, authentication/token rotation, network interfaces, images/layouts/presets and restart persistence.
- Responsive screenshots were inspected, including narrow OCR cards and the maximized 1920×1080 manual-control page and desktop OCR cards. Screenshot/Playwright checks do not establish physical touchscreen or OBS behavior.

## Live observations (not simulated)

The local ScoreSight v0.4.3 `/json` endpoint returned **Time** and **Home Score** with text/state/rect data. Shot Clock and Away Score were absent and stayed unconfigured/manual. No source/detection timestamp or video heartbeat was present.

An isolated native test.10 process observed 40 match-time samples, 10 distinct values from 03:45 to 03:36, with Success/SameNoChange statuses. Explicit follow, held manual takeover and restart were checked. Home Score followed independently while match time was manual: 20 observations all read 1, followed by successful takeover retaining 1. This does not establish changing live-score behavior; score changes were simulated separately.

Field Timer and ScoreSight were read only. Deliberate pauses, resets, bad detections, disconnections and delayed responses were simulated, not induced in the live source.

## User-reported manual evidence

- **2026-11-06, test.9:** the operator confirms match-clock OCR works in the home setup. This is a home smoke test, not venue/live-event validation or approval of new test.10 mappings.
- Historical **2026-11-06, test.8:** the operator reported Linux application/overlay operation with OBS Flatpak. This does not validate OCR, touchscreen, tray, LAN or Companion.

## Final package gates

Windows and Linux ZIPs were extracted and their exact executables passed native HTTP and simulated multi-field OCR/restart suites on the respective operating systems. Executable bytes match the tested build outputs. Final documentation-only repackaging retains those executable bytes.

One additional Windows smoke attempt encountered a loopback connection reset. A diagnostic-enabled rerun passed; the cause was not established. Failure logging was added to the test runner, without automatic retries or a production behavior change.

All three ZIPs passed CRC/inventory/format/embedded-asset checks and SHA-256 verification. Source contents match the explicit source allowlist, with no runtime configuration, tokens, personal graphics, build caches or generated executables. Gitleaks found no leaks in the exact extracted Windows/Linux/source contents; the personal-path review also passed. All 61 relative documentation links/anchors and 11 existing external HTTPS links passed. Final archives include the updated documentation and a separate `SHA256SUMS.txt` manifest supplies their hashes.

The original test.8 and test.9 release-folder files match their pre-change SHA-256 hashes. Published main/tag commit remains unchanged; nothing was pushed or released. Test.9 source remains in local branch history. The final deliverable is one local test.10 set: Windows, Linux, source and checksums.

## Operator checks still required

Physical touchscreen ergonomics; Windows tray lifecycle; OBS operation of test.10; deliberate real-source pauses/resets and capture freezes/loss; configured live Shot Clock/Away Score and changing Home Score; separate-machine LAN/firewall and Companion hardware; venue accuracy, lighting/camera conditions and production latency. Unverified freshness remains an explicit limitation, not a passed test.
