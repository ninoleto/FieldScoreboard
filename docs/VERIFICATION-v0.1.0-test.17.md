# v0.1.0-test.17 verification

Date: 2026-11-07. Started from clean test.16 commit `1ab76d5` on `ocr/scoresight-match-clock`. Native tests use isolated processes/configurations and simulated OCR; Field Timer and production settings are untouched. No publication.

## Focused checks

At 375/500/1000/1440/1920 px, the native clock suite verified exact shot-card order, unique preset/resume placement, setup wording, 64 px preset targets, final full-width Set and desktop Set alignment. Every 14/24/30-second preset applied immediately while main was paused or running, with the expected Ready/running result and unchanged main/game/layout values. Mouse, emulated touch and keyboard activation passed. Shot OCR disabled all three buttons and the existing API rejected each preset without changing the held time. All four quick adjustments on both clocks, pending-only match presets, Set, formats, reset/auto-hide and restart regressions passed.

The new native team-name suite passed both fields at all five widths: 21 px bold labels, 64 px inputs, 24 px text, full width/gaps/focus border, mouse/label click, emulated touch and keyboard, 32-character entry, trim/empty validation and no horizontal page overflow. Actual server updates arrived while inputs had active selection/caret and partial text; polling left them unchanged, and Tab committed the edited name. Both names remained editable while all four score/foul fields followed simulated OCR. Live preview/overlay text updated without changing layout, font, size, weight, position, alignment or transform.

Narrow and desktop screenshots were inspected, including maximized 1920×1080 clock/name views. Production changes are limited to embedded HTML/CSS and version metadata; application/renderer/OCR JavaScript, Go clock/state/API logic and configuration schemas are unchanged.

## Regression and package evidence

Windows Go tests/vet, all embedded JavaScript syntax checks and Windows GUI/console/Linux builds passed. Full offline UI passed all five widths, touch/mouse/keyboard, large dialogs/dynamic options, 23 numeric groups, polling-safe drafts/focus, Fine position, duplicate-ID/overflow checks and native 200%/400% browser zoom. Native display/toolbar checks passed immediate output, stale layout drafts, Save/Discard, queued writes, position reset, presets and restart. Seven-field OCR/period browser/native simulations passed ownership, rejection/hold, delayed takeover, connection states/loss/recovery, strict period parsing/formats, OT, restart and final OCR-section order.

The new OCR preset test initially expected HTTP 409; it was corrected to the existing HTTP 400 response with the OCR explanation, then passed. This was a test expectation correction, not an API change. The isolated Linux verification VM required enabling its network interface and the repository containing Go before checks could run.

Final source passed native Linux Go tests/vet/race with a C compiler in the isolated Alpine VM. Extracted Windows and Linux packages passed HTTP startup/API/configuration/restart checks and **1,500 transport requests each**, without retries or connection resets. Linux native seven-field OCR/period simulations and restart also passed. The historical connection reset did not recur.

All three ZIPs passed CRC, manifest SHA-256, inventory, executable format, embedded-asset and documentation checks. Expanded Windows/Linux/source contents passed Gitleaks and personal-path/local-data review. 101 relative documentation links/anchors and 11 external HTTPS links passed. Final documentation-only repackaging preserves the exact tested executable bytes and regenerates archive hashes. Source packaging includes the new regression helpers. Local packages and `SHA256SUMS.txt` are delivered under `releases/v0.1.0-test.17/` outside the checkout. Earlier release hashes and published main/test.8 Git checkpoints remain unchanged; nothing was published.

## Reused evidence and remaining manual checks

The unchanged editor, background, Font picker and renderer retain the [test.16 all-nine-element/background/font verification](VERIFICATION-v0.1.0-test.16.md). Those full suites were not repeated for this markup/styling-only change. New team-name checks verify current preview/overlay styling directly. Preserve the [test.10 connection-reset history](VERIFICATION-v0.1.0-test.10.md) and [test.11 reproduction/fix](VERIFICATION-v0.1.0-test.11.md); investigate recurrence without retries masking failures.

No new real-source or hardware test is claimed. The user-reported 2026-11-06 test.9 home OCR and test.8 Linux OBS Flatpak smoke tests remain scoped historical reports, not venue or test.17 acceptance. Physical touchscreen ergonomics, actual OBS, Windows tray, real capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and live-event accuracy/latency remain operator checks. Browser touch is emulated; cached HTTP success cannot establish fresh video.

Keep test.17 local. After acceptance, prepare v0.1.0 as a normal release with separately authorized publication.
