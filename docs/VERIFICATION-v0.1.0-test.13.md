# v0.1.0-test.13 verification

Date: 2026-11-07. Started from clean test.12 commit `c142d53` on `ocr/scoresight-match-clock`. Tests used isolated configurations/processes, separate ports and generated artwork. Field Timer and production configuration were untouched. No publication.

## Period behavior and compatibility

- Reproduced the issue against the extracted test.12 executable: a simulated Success reading of 3rd was rejected with the whole-number validation message, retaining period 1.
- Go regressions cover every period 1–20 in numeric/ordinal/quarter forms, upper/lowercase and surrounding whitespace; correct 11th/12th/13th; leading-zero numeric compatibility; whole-value matching, malformed suffixes, extra text, signs, decimals and out-of-range values. Other target parsers remain unchanged.
- Manual numeric/API updates, ±, all display formats, invalid setting rejection, legacy default Number, persisted restart, independent ownership, raw recognised/canonical accepted values, invalid/rejected/missing hold, takeover, OT on/off and game-reset format retention are covered.
- Format is outside Layout/presets. Profile loading preserves current period number/format, ownership and live values. Shared rendering consumes the centrally formatted label without changing stored transforms.
- Native simulated OCR regression covers all seven mappings and the new period forms, independent format choice while following, strict API limits, invalid-data holds, OT, presets, takeover and manual/disconnected restart.

## UI and general regressions

Windows Go tests/vet, JavaScript syntax and all three cross-builds passed. Linux Go tests/vet/race passed in an isolated Alpine environment with Go/GCC. Full offline UI checks passed at 375/500/1000/1440/1920, including existing selectors, 23 numeric groups, drafts/focus, emulated finger scrolling, native 200%/400% browser zoom and Fine position controls.

All-nine element regressions passed, including test.12's default normal selection/dragging, optional Free transform, mode transitions, Save/Discard, numeric drafts, presets, restart, value growth/dots and editor/preview/overlay geometry. Full background PNG/JPG/WebP shape/mode/alpha/original-byte/legacy/draft/profile regressions passed.

Focused period browser checks passed at 375/500/1000/1440/1920: mouse/emulated touch, at least 72 px format buttons, one checked choice, roving keyboard navigation, exact/± numeric entry, raw/canonical OCR values, format changes while following, OT on/off, polling focus, invalid holds and responsive stacking. Transformed period geometry and labels agree in editor, saved preview and the overlay page for all formats. No duplicate IDs, page errors or horizontal overflow. Normal-mode handles remain hidden; the dark OCR section stays last. Narrow/desktop screenshots were inspected, including 1920×1080. Browser tests used Microsoft Edge's Chromium engine.

Legacy test.12/test.13 overlay-page screenshots were pixel-identical for default layouts, custom fonts/alignments/foul dots and a legacy transparent background. This is new automated evidence, not actual OBS application testing.

## Final native and archive gates

Final source passed Linux tests/vet/race. Exact extracted Windows and Linux executables passed native HTTP, seven-field/period-format OCR simulations, restart and **1,500 transport requests per platform**, without retries or connection resets. The historical intermittent reset did not recur; the bounded HTTP action-body fix is unchanged.

All three ZIPs passed CRC, inventory, platform-format, embedded-asset and SHA-256 checks. Exact extracted source/Windows/Linux contents passed Gitleaks with no findings and personal-path/data review. All 77 relative documentation links/anchors and 11 external HTTPS links passed. Final documentation-only repackaging retains the tested executable bytes; native executable evidence is reused for those identical bytes. The archive hashes are in `SHA256SUMS.txt`.

Earlier release-folder files retain their pre-change SHA-256 hashes, including test.12. Published main/test.8 references remain unchanged. Source excludes runtime settings, tokens, personal graphics, logs, caches, temporary test environments and generated executables. No push, public tag or release was performed.

## Live observations and manual evidence

The live ScoreSight endpoint exposed Home Score, Away Score, Home Fouls, Away Fouls, Period and Shot Clock; Time was absent. A read-only query showed Period raw 3rd with SameNoChange. A separate isolated test.13 followed only Period, leaving all other fields manual and unchanged.

There were **15 observations per display format** (45 total): raw 3rd and accepted numeric 3 displayed as 3, 3rd and Q3 respectively, all with SameNoChange. OT on/off, manual takeover and restart persistence passed on the isolated scoreboard. The source and its video input were never controlled. These were stable period observations; changing source periods, malformed/rejected/missing data, loss/recovery and capture pauses/resets are covered by simulation, not claimed as new physical-source tests. The endpoint still provides no detection timestamp/video heartbeat, so stable HTTP readings do not prove fresh video.

Historical evidence remains unchanged: [test.10 intermittent Windows reset](VERIFICATION-v0.1.0-test.10.md), [test.11 investigation/fix and live observations](VERIFICATION-v0.1.0-test.11.md), and [test.12 results](VERIFICATION-v0.1.0-test.12.md). The user reports from 2026-11-06 remain scoped to test.9 home match-clock OCR and test.8 Linux OBS Flatpak smoke tests; they are not test.13 or venue acceptance.

## Operator checks and release boundary

Physical touchscreen ergonomics, Windows tray, test.13 inside actual OBS, real changing seven-field OCR/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain operator checks. Browser input is emulated; overlay-page geometry checks are not actual OBS application tests. Rehearse with a separate portable configuration.

Keep test.13 local. After acceptance, the intended public release is **v0.1.0 normal release**, with separately authorized publication.
