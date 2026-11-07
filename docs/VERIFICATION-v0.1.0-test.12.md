# v0.1.0-test.12 verification

Date: 2026-11-07. Started from clean local test.11 commit `b7d2716` on `ocr/scoresight-match-clock`. Tests use isolated processes/configurations, separate ports and generated artwork. Production settings and Field Timer are untouched. No publication.

## Focused editor checks

- The new regression against the extracted test.11 executable fails because the Free transform button is absent. Test.12 implements the explicit mode.
- All nine elements: normal selection/dragging with only a thin outline; hidden handles/guides/bounds have no client rectangles or pointer hit area. The button is at least 64 px high, uses aria-pressed and changes to Done transforming. Existing four corner/eight unlocked handles remain 56 px.
- Mode changes preserve geometry, saved state, clean/dirty state and unfinished numeric drafts. Done, selecting a different rendered field/button, entering background editing, leaving for Live control or Output & API, and page reload return to normal mode. Background selection disables element Free transform; leaving background selection does not restore it.
- Proportional/unlocked resizing, opposite anchors, keyboard handle resizing, position/size controls, font/color/bold/alignment, changing score digits and long names, foul dots/numbers, Save/Discard, presets and restart are covered. Save/Discard also work while Free transform is active. Mode is not saved in layout/configuration.
- Mouse/emulated touch passed at 375/500/1000/1440/1920 px; effective zoom layouts and native Chromium-engine 200%/400% zoom passed. Narrow and 1920x1080 screenshots were inspected in normal and transform modes. No horizontal overflow or page errors. Shared editor, saved preview and actual overlay-page logical geometry agree; the overlay contains no editor decorations.

## Regression and package checks

Windows Go tests/vet, JavaScript syntax and Windows GUI/console/Linux x64 cross-builds passed. The full offline UI suite passed, including large selectors, 23 numeric groups, keyboard, drafts, touch scrolling, focus, five widths, native zoom and Fine position controls. The complete background suite passed with PNG/JPG/WebP shapes/modes, original bytes, mouse/touch gestures, drafts, Save/Discard, presets, legacy compatibility and restart.

Final source passed Linux Go tests/vet/race in an isolated Alpine 3.22.8 VM with Go 1.24.13/GCC. Windows cross-builds used Go 1.27.3. Browser tests used installed Microsoft Edge (Chromium engine); screenshots and touch inputs are automated/emulated, not physical hardware tests.

Seven-field OCR simulation and browser regressions passed: independent/mixed ownership, per-field validation and hold, atomic resets, OT/saved period, delayed takeover, loss/recovery, manual restart, large selectors, drafts/focus/scroll, dark outer container and bottom ordering at all five widths, connected/following/disconnected. OCR implementation and the shared renderer were not changed.

Actual test.11/test.12 overlay-page screenshots were pixel-identical in the default, custom fonts/alignments/dots and legacy transparent-background scenarios. This is new automated evidence; it does not claim actual OBS application testing. The final element suite also compared transformed editor/preview/overlay geometry as values changed.

Exact extracted Windows and Linux executables passed native HTTP, simulated seven-field OCR/restart and **1,500 transport requests per platform** without retries. All responses were complete; the previously documented intermittent reset did not recur. Test.11's bounded optional-action-body handling is unchanged.

All three ZIPs passed CRC, inventory, platform-format, embedded-asset and SHA-256 checks. Exact extracted source/Windows/Linux contents passed Gitleaks with no findings and personal-path/data review. All 71 relative documentation links/anchors and 11 external HTTPS links passed. Final documentation-only repackaging retains the tested executable bytes; native binary evidence is reused for those identical bytes. `SHA256SUMS.txt` contains the final archive hashes.

Earlier release-folder files retain their recorded pre-change hashes, including test.11. Published main/test.8 references remain unchanged. Source inventory excludes runtime settings, credentials, personal graphics, logs, caches, temporary environments and generated binaries. No push, public tag or release was performed.

## Evidence boundaries and remaining operator checks

No new live ScoreSight or physical-device test is claimed for test.12. Seven-field source changes, failures and takeover checks use the existing simulator. [Test.11](VERIFICATION-v0.1.0-test.11.md) retains its live observations (Time and stable Home/Away Score), absent source fields, legacy OBS screenshot comparisons and Windows connection-reset investigation. The historical [test.10 intermittent reset](VERIFICATION-v0.1.0-test.10.md) is preserved; connection-reset regression results for this build belong in the final gates.

User reports remain scoped to 2026-11-06: test.9 match-clock OCR worked in the home setup, and test.8 Linux application/overlay worked with OBS Flatpak. Neither establishes venue validation or acceptance of test.12.

Still needed: physical touchscreen selection/dragging/Free transform ergonomics; Windows tray; test.12 in actual OBS; real seven-field OCR and capture pause/reset/freeze/loss; separate-machine LAN/firewall and Companion hardware; venue accuracy/latency. Use a separate portable configuration for rehearsal. After acceptance, the intended public version is **v0.1.0 normal release**, with separate publication authorization.
