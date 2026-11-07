# v0.1.0-test.15 verification

Date: 2026-11-07. Started from clean test.14 commit `b6427dd` on `ocr/scoresight-match-clock`. Test processes/configurations, ports and source readings are isolated. Field Timer and production settings remain untouched. No publication.

## Focused checks

Go regression tests cover −5/−1/+1/+5 on both clocks in running/paused states, main count-up/down, unchanged other-clock anchors/configuration, countdown zero completion, count-up zero hold, exact seven-day boundary, upper rejection without mutation and all four API actions rejected under OCR ownership. Production clock/transport/API logic is unchanged.

Native browser checks cover 375/500/1000/1440/1920 widths: exact card/action order, four matching 64 px quick targets with 22 px text, narrow 2×2 rows, full-width 72 px blue Set last and aligned desktop buttons, large selectors, one-unit numeric drafts, immediate formats independently of Set, zero-minute duration, invalid Set rejection, preset/reset behavior, auto-hide mouse/keyboard access, OCR restrictions and format persistence. Footer text is exact. Narrow and maximized desktop screenshots are inspected.

The offline auto-hide fixture was updated to activate its visible label rather than click the visually hidden checkbox after moving the control into Clock setup. Keyboard Space remains supported; application switch behavior is unchanged.

## Regression and package evidence

Windows Go tests/vet, JavaScript syntax and Windows GUI/console/Linux cross-builds passed. Final source passed native Linux Go tests/vet/race with a C compiler in an isolated Alpine VM.

Full offline UI passed at 375/500/1000/1440/1920: all large choice dialogs/dynamic options, 23 numeric groups, drafts/focus, emulated finger scrolling/taps, Fine position, no duplicate IDs/overflow and native 200%/400% browser zoom. The focused native clock suite passed at all five widths on the extracted Windows executable, including exact footer text, Set actions and restart. The keyboard switch test waits for the first response to be consumed before issuing another toggle; no transport retries are used.

Native display/toolbar tests passed all five widths, immediate editor/preview/overlay rendering, stale layout saves, Save/Discard, position reset, queued/delayed writes, presets and restart. Seven-field OCR/period browser and native simulations passed mixed ownership, rejection/hold, takeover, connection states/loss/recovery, atomic guards, strict period formats, OT and transformed period rendering. The OCR section stays last. No new real-source observation is claimed.

Extracted Windows/Linux packages passed HTTP startup/API/configuration/restart checks and **1,500 transport requests each**, without retries or connection resets. Linux native OCR/period simulations and restart passed. Windows browser/OCR tests used the exact executable bytes included in the final archive. The historical connection reset did not recur; its fix is unchanged.

All three ZIPs passed CRC, manifest SHA-256, inventory, executable format, embedded-asset and documentation checks. Expanded Windows/Linux/source contents passed Gitleaks and personal-path/local-data review. 90 relative documentation links/anchors and 11 external HTTPS links passed. Final documentation-only repackaging retains tested executable bytes and regenerates hashes. Earlier release files and published main/test.8 Git checkpoints remain unchanged; no publication.

## Historical evidence and manual checks

The test.14 all-nine element/background/legacy-renderer evidence remains applicable to unchanged editor/background/renderer implementations; it is historical evidence, not a claim of repeating those full suites. See [test.14 verification](VERIFICATION-v0.1.0-test.14.md). Preserve the [test.10 Windows reset history](VERIFICATION-v0.1.0-test.10.md) and [test.11 fix](VERIFICATION-v0.1.0-test.11.md); investigate any recurrence without retries masking failures.

No new live ScoreSight/physical hardware test is claimed. User-reported 2026-11-06 test.9 home match-clock OCR and test.8 Linux OBS Flatpak smoke tests remain scoped reports, not venue validation or test.15 acceptance. Physical touchscreen ergonomics, actual OBS output, Windows tray, real capture changes/loss, separate-machine LAN/firewall, Companion hardware and live-event accuracy/latency remain operator checks. Browser touch is emulated; cached successful HTTP responses cannot prove fresh video.

Keep test.15 local. After acceptance, prepare v0.1.0 as a normal release with separately authorized publication.
