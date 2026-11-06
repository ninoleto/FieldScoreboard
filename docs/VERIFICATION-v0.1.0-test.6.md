# test.6 verification — 2026-11-06

> Historical checkpoint before the first public preview. For current release and manual-test status, see [test.8 verification](VERIFICATION-v0.1.0-test.8.md).

This report separates automated testing and screenshot review from operator/hardware validation.

## Baseline and scope

Read AGENTS.md and handoff.md; compared completed test.5 source with its delivered source archive. There were no user edits or additional source files. Retained the original tree and packages and implemented in a separate test.6 directory. test.6 was the next unused local version. No GitHub publication or Field Timer modifications.

Reproduced the defect in test.5 Chromium: a 400×400 graphic rendered as 1920×1080 with object-fit fill. New background transforms, editor controls and shared placement fix this while preserving nil-transform legacy rendering. No production clock/action logic was replaced.

## Automated verification

Windows toolchain: Go 1.27.3 amd64 and Node 24.18.0. Linux tests run on Go 1.24.13, Alpine 3.22.8 amd64 in isolated QEMU. Browser tests use Chrome/Chromium through Playwright; fixtures/configs are temporary and generated. Pillow is only a test dependency. Release binaries use CGO_ENABLED=0 and standard-library runtime code.

| Check | Result |
|---|---|
| Windows Go unit tests/vet and all embedded JS syntax | PASS |
| Linux Go unit tests/vet/race detector | PASS |
| Existing offline UI regression | PASS |
| Real-server background browser regression | PASS |
| Windows GUI/console and Linux x64 cross-build | PASS |
| Extracted Windows/Linux native HTTP smoke and restart | PASS |
| ZIP CRC/SHA-256, embedded assets, portable formats, credential scan | PASS |

Backend tests cover proportional Fit defaults, staged vs immediate imports, unchanged image bytes, finite bounded transforms, malformed/oversized image headers, PNG/JPEG and all three WebP header formats, JPEG EXIF orientation, deep-copy isolation, saved config/restart, legacy and transformed profiles, graphic removal, and sanitized private-LAN overlay state. Existing tests retain clock behavior, scoring, OT, shot reset/auto-hide, token rotation/authentication and API contracts.

The real-server UI suite imports square (400×400), portrait (400×800), banner (1600×200) and canvas (1920×1080) artwork in PNG, JPG and WebP: 12 actual encoded fixtures. It verifies default Fit/lock, all sizing modes, original dimensions, exact uploaded bytes and SHA-256 filenames, shared editor/preview/overlay rectangles, PNG alpha and transparent uncovered canvas. A 1920×1400 output viewport verifies that Fill clips at the logical canvas and leaves letterboxes transparent. It exercises locked/unlocked dimensions, negative coordinates, Center/Reset, steppers, explicit selection, keyboard/mouse resize/move, 56 px handles, emulated finger dragging, and unchanged scoreboard coordinates. It checks removal/import Discard, blank numeric drafts across polling/navigation, saving while newer edits arrive, saved profile reload, nil-transform legacy opening/saving/editing and real server restart with Ready clocks.

At 375, 500, 1000, 1440 and 1920 CSS px, tests check horizontal overflow, unique IDs, 64 px numeric controls, all 12 hidden native selectors, the large sizing dialog with 56+ px rows/18+ px text, disabled Custom keyboard skipping and Escape focus restoration. Saved coordinates remain identical through viewport resizing. Real browser page zoom at 200% and 400% tests the new sizing dialog and geometry in isolated Chrome profiles; it is not CSS zoom.

The retained offline suite checks all original 11 selectors/pages, dynamic profiles/adapters, focus trapping/restoration, mouse/keyboard, finger scrolling without selection at 375/1000/1920 px, Menu navigation, draft retention, clock duration carry/borrow/zero minutes, Both clocks wiring, shot hiding/OT and Companion generation. Its native 200%/400% zoom checks pass as well. Browser touch emulation is not physical hardware testing.

The extracted Windows console and Linux binaries pass native HTTP smoke tests for startup, scores, OT, shot hiding/reset, independent/combined clocks, SSE, token rotation, image bytes/default Fit/draft upload, transformed profiles and restart persistence. Final archive checks verify CRCs and SHA-256, x64 PE GUI/console subsystems and ELF format/permissions, exact embedded image-editor/render assets and source, and absence of runtime config, uploaded artwork or tool caches. Gitleaks reports no secrets.

## Screenshot review

Local `.test/` evidence includes background editor screenshots at all five widths, selected touch handles, a transparent overlay, and 200%/400% zoom dialogs, alongside the retained touch-interface screenshots. Reviewed desktop and narrow editor stacking, control spacing/readability, image/selection alignment, contrast, clipping and dialog layout. Evidence is excluded from portable/source ZIPs.

## Operator checks still required

1. Physical 24-inch touchscreen with normal Windows display scaling, browser zoom and a mouse attached: number editing, on-screen keyboard, swiping choices, selecting/dragging/resizing artwork and rapid clock control.
2. Native Windows tray menu, opening the control/data folder, Exit/restart and upgrade using the operator's real configuration and preset images.
3. Installed OBS/CEF, local and separate-machine LAN Browser Sources: transparent PNG margins, Fit/Fill cropping, saved geometry, no editor handles, nested scene scaling, live clocks/OT/shot auto-hide.
4. Actual private LAN/firewall, Companion bearer headers/token rotation and full live-production/field operation. Automated authorization and HTTP checks do not establish hardware/network reliability.
