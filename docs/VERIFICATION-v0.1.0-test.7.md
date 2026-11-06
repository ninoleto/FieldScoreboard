# test.7 verification — 2026-11-06

> Historical checkpoint before the first public preview. For current release and manual-test status, see [test.8 verification](VERIFICATION-v0.1.0-test.8.md).

Automated checks and screenshot review are reported separately from operator/hardware tests.

## Baseline and scope

Read AGENTS.md and handoff.md first. Compared test.6 with its delivered source archive: no modified, missing or extra source files. Preserved test.6 and worked in a separate test.7 directory, the next unused local version. No GitHub publication or Field Timer changes.

Measured the existing controls in Chromium: live score/foul/period groups were 48 px high with no gaps; editor steppers were 49 px with no gaps, while duration groups were 64 px with 10 px gaps. The background toggle was below the detailed image controls.

Changes are confined to HTML/grouping, shared CSS, the existing background toggle's labels and release metadata. All existing app.js action/draft handlers are retained. Its only addition maps touch buttons for the three former native-spinner fields to native stepUp/stepDown plus their existing input/change listeners. The Go engine/server/security, background transform logic, shared renderer and overlay assets match test.6 byte-for-byte. The only Go edit is the version. No slider exists in the DOM.

## Automated results

Windows: Go 1.27.3 amd64, Node 24.18.0. Linux: Go 1.24.13 on Alpine 3.22.8 amd64 in isolated QEMU. Browser checks use Chrome/Chromium through Playwright. No test tooling/runtime dependencies are shipped in portable packages.

| Check | Result |
|---|---|
| Windows Go unit tests, vet, all embedded JS syntax | PASS |
| Linux Go unit tests, vet, race detector | PASS |
| Required offline UI suite, including all 21 numeric groups | PASS |
| Real-server background image suite | PASS |
| Windows GUI/console and Linux x64 builds, CGO_ENABLED=0 | PASS |
| Extracted Windows/Linux native HTTP smoke and restart | PASS |
| ZIP CRC/SHA-256, embedded assets, portable formats, credential scan | PASS |

At **375, 500, 1000, 1440 and 1920 CSS px**, the numeric suite measures all 21 groups: period, four score/foul groups, main minutes/seconds and shot seconds, four inspector steppers, four background steppers, two Companion duration steppers, server port, Companion signed adjustment and Companion period. The latter three replace tiny native spinners while preserving input bounds and pending Save/Test behavior. Each has labelled grouping, 64 px buttons/values, 64 px ± widths, 28 px numerals, 10 px gaps and matching borders/radii. Text measurement verifies allowed integer limits fit, including 10079-minute input, score 999, coordinates 1920/1080 and signed background bounds, port 65535, Companion period 20 and signed clock adjustment. New port/period button bounds and signed adjustment are verified; these controls send no live API write until their existing Save/Test action. Groups wrap/stack without horizontal overflow or duplicate IDs. Every input stepper is exercised with Enter/Space; all five live value buttons retain immediate ± updates and keyboard exact-value prompts with accessible labels. Duration blank/zero drafts survive polling/navigation and remain unapplied.

The relocated background button is unique, adjacent to and before the canvas, 64+ px high, and has the requested labels/explanation. Keyboard activation shows the existing four handles and active aria-pressed state without making a layout dirty; Escape exits. No sliders are present.

The full retained offline suite passes universal choice dialogs, all original selectors, dynamic profiles/adapters, mouse/keyboard focus handling, emulated touch scrolling/taps, Menu navigation, duration carry/borrow/zero minutes, input drafts, combined/independent clock wiring, OT/shot hiding and Companion generation. Native browser zoom at **200% and 400%** passes on all pages and dialogs.

The real-server background suite passes 12 actual PNG/JPG/WebP fixtures (square, portrait, banner, 1920×1080), sizing modes, original byte preservation, aspect lock/unlocked resizing, steppers, keyboard/mouse/emulated touch manipulation, selection alignment, clipping/transparency, shared editor/preview/overlay placement, Save/Discard, concurrent drafts, profiles, legacy compatibility and restart. Its 200%/400% image-dialog zoom checks also pass.

The extracted Windows console and Linux binaries pass native startup/API smoke tests, including independent/combined clocks, OT/shot hiding/reset, scoring, SSE, token rotation, layouts/background transforms, profiles and restart persistence. Archive verification checks CRCs, SHA-256, Windows x64 GUI/console PE subsystems, Linux x64 ELF permissions, exact embedded assets and all source bytes. Credential scanning reports no secrets; user config, uploaded artwork, caches and local evidence are excluded.

## Screenshot review

Reviewed narrow and desktop live/editor layouts, numeric grouping and readability, active background controls/handles, and large choice dialogs. Local `.test/` contains full-page screenshots at all five widths and exact **1920×1080** viewport captures for every page, plus background/overlay and zoom evidence. Screenshot evidence is excluded from release archives. Some pages require vertical scrolling; controls retain their target size rather than compressing to fit one screen.

## Remaining operator checks

The operator confirms background selection/manipulation works in test.6. That confirmation does not establish validation of the changed test.7 layout or all production hardware.

1. Use the actual 24-inch touchscreen at normal Windows scaling, maximized browser and any production zoom. Check the prominent background button, every numeric group, exact-value prompts/on-screen keyboard, and rapid score/clock work.
2. Exercise Windows GUI/tray, Open control/data folder, Exit/restart and upgrade with real configuration/presets.
3. Verify installed local/LAN OBS Browser Sources, transparency, nested scene scaling, live clocks/OT/shot hiding and imported production graphics.
4. Test physical LAN/firewall, Companion/token rotation and live field production. Browser touch emulation and HTTP authorization checks do not establish these hardware/network results.
