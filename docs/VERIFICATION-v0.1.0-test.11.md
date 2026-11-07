# v0.1.0-test.11 verification

Date: 2026-11-07. Started from clean local commit `112b48f` on `ocr/scoresight-match-clock`. Tests used isolated configurations, separate ports and generated artwork. Field Timer and production settings were untouched. No publication.

## Automated implementation checks

- Windows Go tests/vet, all embedded JavaScript syntax checks, CGO-free Windows GUI/console and Linux x64 builds passed. Final Linux Go tests/vet/race passed in Alpine 3.22.8 with Go 1.24.13/GCC; cross-builds used Windows Go 1.27.3.
- Seven-field OCR: simultaneous/mixed ownership; strict time/number/status validation, foul 0–30 and period 1–20 bounds; missing/invalid/duplicate field isolation; no clearing/clamping; one bounded poll worker; per-field delayed takeover/re-follow; independent clocks and effective auto-hide; saved mappings/game values and manual restart. Legacy test.9 field and test.10 mapping compatibility remain covered.
- Manual/API guards cover ±, exact values and transport/Set. Combined clock rejection remains atomic. Game reset rejects atomically for each individual score/foul/period owner. Numeric period observations preserve OT; explicit OT off reveals the latest accepted number. Authentication and sanitized overlay boundaries pass.
- OCR browser checks passed at 375/500/1000/1440/1920 px: seven dynamic large selectors, keyboard/emulated touch, native select tab-stop removal, polling-safe drafts/focus/scroll, per-target button ownership, OT toggle access, disconnected restart, duplicate IDs and overflow. OCR stays last. Outer background is exactly rgb(20,20,20); inner cards retain rgb(16,29,45). Effective 200%/400% zoom layouts passed.
- Element tests passed for all nine fields: movement, proportional corner resize, unlocked side resize, numeric dimensions, left/center/right anchors, reset size, fonts/color/bold, growing 9→10 score and 32-character name, numeric/dot fouls including overflow count, drafts, Save/Discard, presets and restart. Background/element selection is mutually exclusive; output contains no editor handles/borders.
- Element mouse/emulated-touch geometry passed at 375/500/1000/1440/1920, with effective zoom layouts and **native Chromium 200%/400% zoom** resize/anchor/keyboard checks. Editor, saved preview and actual overlay page logical bounds agree. Responsive screenshots were inspected, including the narrow handle guide and 1920×1080 editor/OCR views.
- Legacy compatibility: actual OBS page screenshots from test.10 and test.11 were pixel-identical for default layouts, customized fonts/alignments/dots/OT, and an imported transparent background with legacy transform metadata absent. Optional element metadata is omitted for legacy layouts; snapshot/config transforms are deep-copied and validated.
- Existing full offline UI suite passed: 11 original dropdowns, 23 numeric groups, exact entry, duration drafts/seconds carry/borrow, small-screen navigation, native 200%/400% zoom, Fine position 5/10/20 default 5 with all directions/boundaries, and X/Y ±1.
- Background suite passed: square, portrait, wide banner and 1920×1080 PNG/JPG/WebP; original bytes, proportions/modes, clipping/transparency, mouse/touch editing, drafts, Save/Discard, profiles, restart and all five widths. All 19 selectors use the universal dialog.
- Native Windows/Linux HTTP and simulated seven-field OCR suites passed. Final archive gates are recorded below.

## Windows connection-reset investigation

The unexplained intermittent Windows loopback reset in [test.10 verification](VERIFICATION-v0.1.0-test.10.md) remains part of the history. It recurred during test.11’s native OCR test while the server process stayed alive.

A controlled comparison sent 500 pause requests with optional `{}` bodies and 500 empty-body requests. Before the fix, the optional-body run produced **14 connection resets and 3 connection aborts**; 483 requests returned the expected HTTP error. All 500 empty-body requests returned the expected error. Local Go HTTP server source inspection showed that connection-close responses can skip draining an unread request body.

Bodyless clock actions, game reset and token rotation now consume optional bodies after their existing access checks and before side effects/responses: maximum 64 KiB and a 5-second read deadline. The API continues accepting empty and optional unused bodies. Oversized/incomplete input is rejected before mutation. No retry loop was added.

After the fix, the same 1,000-request comparison returned complete expected responses with zero transport errors. The committed transport regression then passed **1,500 requests on Windows and 1,500 on Linux**: 500 successful reset responses with `{}`, 500 with empty bodies, and 500 complete rejected pause responses. Full native OCR/HTTP tests also passed. This establishes the reproduced failure path; it is not a claim that every possible network failure has been eliminated.

## Live observations and manual evidence

The running ScoreSight v0.4.3 endpoint exposed **Time, Home Score and Away Score**, with Success/SameNoChange statuses and no detection timestamp/video heartbeat. Shot Clock, Home Fouls, Away Fouls and Period were absent and remained unconfigured/manual.

An isolated test.11 process observed 40 match-time samples (nine distinct values, 45:48 to 45:40), followed by 20 Home Score observations all equal to 11 and 20 Away Score observations all equal to 101. Explicit per-target follow, mixed manual match operation, held takeover and restart passed. These score observations were stable; changing scores and new foul/period fields were tested with simulations. Field Timer and ScoreSight were only read, not controlled.

User-reported evidence is unchanged: on 2026-11-06, test.9 match-clock OCR worked in the home setup; test.8 Linux application/overlay worked with OBS Flatpak. Neither report establishes venue validation or acceptance of test.11. Deliberate pauses/resets, loss/freeze, bad detections and delays in this verification were simulations.

## Final package gates

Windows/Linux ZIPs were extracted and their exact executables passed native HTTP, seven-field OCR/restart and 1,500-request transport checks on the respective operating systems. Final documentation-only repackaging retained those tested executable bytes.

All three ZIPs passed CRC/inventory/platform-format/embedded-asset checks and SHA-256 verification. The source ZIP matches the explicit source allowlist and includes the new element/OCR/transport tests. Exact extracted Windows/Linux/source contents passed Gitleaks with no findings and the personal-path/data review. Runtime configuration, tokens, personal graphics, caches, temporary environments and generated executables are excluded from source control/source ZIP.

All 64 relative documentation links/anchors and 11 existing external HTTPS links passed. Final archives include this documentation; `SHA256SUMS.txt` supplies the Windows/Linux/source hashes. Earlier release-folder files retain their pre-change SHA-256 hashes, including test.10. Published main/test.8 tag remain unchanged; no push, public tag or release was performed. Test.11 is a local Windows/Linux/source/checksum set only.

## Operator checks and release boundary

Physical touchscreen use; Windows tray; test.11 in real OBS; real configured foul/period/shot readings and changing scores; live capture pause/reset/loss/freeze; separate-machine LAN/firewall and Companion hardware; venue accuracy and production latency still require the operator. Visual/browser automation is not a physical-device or broadcast test.

Test.11 stays local. After user acceptance, the intended public version is **v0.1.0**, a normal release. No additional public test/prerelease is planned by this task, and no publication is authorized yet.
