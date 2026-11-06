# test.5 verification — 2026-11-06

> Historical checkpoint before the first public preview. For current release and manual-test status, see [test.8 verification](VERIFICATION-v0.1.0-test.8.md).

This report describes automated checks and visual screenshot inspection. It does not claim physical touchscreen or broadcast field validation.

## Baseline and scope

The workspace contained test.4 Windows/Linux/source ZIPs and an extracted Windows package, with no Git checkout or editable source tree. The supplied source was extracted into a new directory. Original artifacts were retained. No GitHub publication or Field Timer modification took place. test.5 was the next unused version found locally.

The desktop issue was reproduced in Chromium at 1920px: 11 native selectors existed, and the large choice trigger was hidden while the native direction select remained visible. The existing popup was the visual reference. Backend clock/auth/network/layout logic and standalone OBS assets were preserved; only the Go release version changed.

## Automated checks

Windows build/test toolchain: Go 1.27.3 amd64, Node 24.18.0. Linux tests: Go 1.24.13 on Alpine 3.22.8 amd64 in an isolated QEMU VM. Portable packages contain no emulator or toolchain dependencies.

| Check | Result |
|---|---|
| Windows `go test ./...`, `go vet ./...` | PASS |
| Linux `go test ./...`, `go vet ./...`, `go test -race ./...` | PASS |
| `node --check` on all embedded JavaScript | PASS |
| `python scripts/test_ui_offline.py` | PASS |
| Windows GUI / console and Linux amd64 builds, CGO_ENABLED=0 | PASS |
| Extracted Windows and Linux native HTTP smoke, including restart | PASS |
| ZIP CRC, SHA-256, PE/ELF formats, embedded assets, Gitleaks and archive hygiene | PASS |

Browser checks use headless Chromium with deterministic API fixtures. The suite covers all three pages and all 11 selectors at **375, 500, 1000, 1440 and 1920 CSS px** with a mouse/fine pointer. It checks option row/text sizes, labels and selected state, hidden native selects removed from tab order, unique IDs, control clipping and horizontal overflow. It tests arrow keys, Home/End, typeahead, Enter/Space, Tab/Shift+Tab confinement, Escape, Close, outside dismissal and restored focus; dialog navigation must not nudge layout coordinates.

Dynamic profiles are saved, selected and deleted; options also update while a dialog is open. Adapter replacement updates labels and network URLs. Duration tests cover zero minutes, unfinished blank input across polling/navigation, seconds carry/borrow, invalid zero total duration, applied direction, shot drafts, editor drafts and network drafts. Existing regression checks retain independent/combined clock wiring, shot reset/presets, OT, shot visibility, layout dragging/scaling, Companion request generation, token controls and transparent overlay rendering.

Chromium touch emulation uses actual CDP touch-start/move/end events at 375, 1000 and 1920px. Swipes scroll the long Companion action list without selecting; a subsequent deliberate tap selects. This is browser emulation, not hardware testing.

Native browser page zoom is tested at **200% and 400%** in isolated browser profiles, using Chromium's persisted zoom preference. Tests assert 960px and 480px effective widths from a 1920px window, with matching devicePixelRatio, then verify all pages and the choice dialog. This is actual browser page zoom, not CSS zoom or a simulated pinch.

## Screenshots

The source working directory's `.test/` contains full-page screenshots for Live control, Layout editor and Output & API at all five widths, choice-dialog screenshots, native zoom viewport screenshots, and a transparent-overlay screenshot. These are local test evidence and are excluded from release archives. Native zoom dialog geometry was also checked while scrolled; captures use the scroll origin to avoid CDP scaled-scroll screenshot offsets. Desktop/mobile editor, clock group, menu and dialog screenshots were visually reviewed for spacing, contrast, wrapping and clipping.

## Operator-pending checks

1. Use the actual 24-inch touchscreen at its normal Windows scaling and browser size, both with and without a mouse. Check finger targeting, rapid clock operations, list scrolling and the on-screen keyboard. Repeat on any production tablets.
2. Launch the Windows GUI; inspect the tray icon/menu, Open control/data folder, Exit and restart. Automated HTTP tests do not validate native tray interaction.
3. Verify installed OBS Browser Source transparency, live updates, OT and shot auto-hide, nested 1920×1080 scene scaling, and imported production graphics/layouts. No OBS integration test was performed.
4. Test actual LAN binding/restart, Windows Private firewall, remote OBS on another computer and Companion with bearer auth, including token regeneration. Unit/HTTP tests do not establish field network behavior.
5. Confirm existing production config/profile/background retention during upgrade and restart, clock Ready state, combined transport retaining times, and shot reset resuming only while the match clock runs. Use the detailed test sequence in `handoff.md`.
