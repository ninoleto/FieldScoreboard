# v0.1.0-test.14 verification

Date: 2026-11-07. Started from clean test.13 commit `ea0daec` on `ocr/scoresight-match-clock`. Tests use isolated configurations/ports and generated data/artwork. Field Timer, production settings, earlier builds and published test.8 remain untouched. No publication.

## Interface and state isolation

- Go tests cover all five display preferences, strict invalid/unknown/null rejection, limits, authentication, stale Save merging, legacy layout/preset compatibility and persistence. Seven OCR owners, game values and held/running clock anchors remain unchanged.
- Native browser display checks pass at 375/500/1000/1440/1920: desktop panel beneath preview, narrow panel after primary controls/before final OCR, exact inspector DOM/keyboard order, equal large toolbar controls, mode help, normal hidden handles and touch/mouse/keyboard activation.
- Immediate preview/overlay changes need no Save; unfinished numeric entries survive polling. Dirty geometry survives display changes. Save/Discard, position reset, external updates, queued/delayed display responses and presets preserve the intended boundary. Restart retains preferences.
- Simulated connection checks cover red disconnected/lost/failed labels, disabled pending Connecting with one request, green Connected, automatic recovery, visible ownership restrictions and no polling focus/scroll jumps. Connectivity stays separate from following/capture freshness.

## Required regressions

Windows Go tests/vet, all JavaScript syntax checks and Windows GUI/console/Linux cross-builds passed. Linux Go tests/vet/race passed with Go/GCC in an isolated Alpine VM. Its first run lacked loopback and failed to bind an httptest listener; enabling loopback resolved the environment issue without application changes.

Full offline UI passed at all five widths: universal dialogs, dynamic options, 23 numeric groups, exact entry/drafts, Fine position, emulated finger scrolling/taps, focus and native 200%/400% browser zoom. Tests were updated for moved controls; the delayed-response fixture uses browser evaluation without weakening application CSP. Colour assertions wait for the existing CSS transition.

All-nine element and PNG/JPG/WebP background regressions passed: movement/resizing, optional Free transform/normal dragging, aspect locks, values/dots, anchors, Save/Discard, presets, restart, alpha/clipping, legacy behavior and matching editor/preview/overlay geometry. Narrow/desktop screenshots including maximized 1920×1080 were inspected; no horizontal overflow, duplicate IDs or page errors.

Seven-field OCR/period suites passed: simultaneous/mixed ownership, independent validation, missing/rejected holds, late takeover, atomic resets/combined actions, source pauses/resets, connection loss/recovery, numeric/ordinal/Q recognition, all display formats, OT, transformed rendering and manual/disconnected restart. Changing source data is simulated.

## Final native and package gates

Final source passed Windows and Linux Go tests/vet and Linux race. The exact extracted Windows/Linux executables passed native HTTP, seven-field/period OCR simulations and restart. **1,500 transport requests per platform** passed without retries or connection resets. The historical reset did not recur.

Legacy test.13/test.14 overlay screenshots were pixel-identical for default layouts, custom fonts/alignments/dots and a legacy transparent background. This is automated overlay-page evidence, not an OBS application test.

All three archives passed CRC/inventory, executable-format, embedded-asset and SHA-256 checks. Expanded Windows/Linux/source contents passed Gitleaks and personal-path/local-data review. Documentation checks passed 83 relative links/anchors and 11 external HTTPS links. Final documentation-only repackaging preserves the exact tested executable bytes and regenerates archive checksums. Source packages include the updated guides and tests; binaries, configuration, tokens, personal graphics and caches are excluded from source control. Earlier release hashes and the published main/test.8 Git checkpoint remain unchanged.

## Historical evidence and operator checks

No new live ScoreSight or physical hardware claim is made for test.14. Preserve [test.13 live period observations](VERIFICATION-v0.1.0-test.13.md), [test.10 intermittent Windows reset](VERIFICATION-v0.1.0-test.10.md) and [test.11 reproduction/fix](VERIFICATION-v0.1.0-test.11.md). The bounded action-body fix is unchanged; investigate recurrence without retries masking failures.

User-reported smoke tests on 2026-11-06 remain scoped to test.9 match-clock OCR working at home and test.8 Linux application/overlay with OBS Flatpak. Neither is venue validation or test.14 acceptance.

Physical touchscreen ergonomics, actual OBS, Windows tray, real changing seven-field capture/pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain operator checks. Browser touch is emulated and overlay-page checks are not actual OBS tests. Use a separate portable configuration. Cached HTTP success cannot prove fresh video.

Keep test.14 local. After acceptance, the intended public version is **v0.1.0 normal release**, with separately authorized publication.
