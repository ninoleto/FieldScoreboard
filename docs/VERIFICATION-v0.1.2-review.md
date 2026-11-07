# v0.1.2 review verification

Date: 2026-11-07. Base: local v0.1.1 commit `52f3458ae7a7e774de6d16d3c6135a07274a83da`. The checkout was clean. Work is on local branch `prepare/v0.1.2`; no release/tag is published or removed in this pass. The delivery's `review-build.json` records the final source commit and artifact hashes.

## Scope

The runtime changes are the background sizing interface and version. The four buttons call the existing preset function; renderer geometry, backend sizing, persistence schemas, clock/OCR behavior and original image storage are unchanged. Custom is a status with no selected preset. Current documentation/version references are updated; historical release notes and verification records remain intact.

## Build and automated checks — passed

- Fresh Windows x64 GUI/console and Linux x64 executables from `scripts/build.ps1`; Go tests/vet and syntax checks for every embedded JavaScript file passed. The executables differ from the preserved v0.1.1 packages.
- Native Linux `go test ./...`, `go vet ./...` and `go test -race ./...` passed in an isolated Alpine x64 VM with Go 1.24.13 and GCC/musl. This is an actual Linux runtime under emulation.
- `test_ui_offline.py`: all pages and choice dialogs at 375/500/1000/1440/1920 px; mouse, keyboard, emulated touch, focus, drafts, dynamic options, numeric groups, fine positioning, duplicate IDs, overflow and native 200%/400% browser zoom.
- Expanded `test_background_ui.py`: all four buttons with 400×400, 400×800 portrait, 1600×200 landscape and 1920×1080 images, each in PNG/JPG/WebP. Original bytes are retained; expected geometry matches editor, saved preview and browser OBS output. Portrait/landscape profiles restore each preset and its selection.
- Background Custom transitions cover numeric dimensions/position, Center image and mouse/touch gestures. Custom removes selected color, border and checkmark; Reset to fit restores Fit selection and aspect lock. Locked portrait/landscape changes preserve original proportions; unlocked changes preserve the other dimension. No-image controls remain visible and disabled.
- Background Save/Discard, unfinished numeric drafts through polling/navigation, in-flight Save edits, import/removal, Custom profile restoration, legacy stretch, clipping/transparency and restart persistence passed. Each preset remains a draft until Save Layout; saved live preview/OBS geometry remains unchanged during draft edits. The mouse test explicitly scrolls its drag target into view after controls move the page, and style checks wait for the existing color transition.
- Buttons retain at least 124 px height, 20 px labels and 16 px help. Desktop rows are balanced; narrow screens stack without horizontal overflow. Keyboard and emulated touch operate all four modes, including at native zoom. Numeric controls remain 64 px. Desktop editor top/bottom edges align and Layout profiles remains below both cards.
- `test_display_ui.py`, `test_elements_ui.py`, `test_font_ui.py`, `test_clock_ui.py` and `test_team_names_ui.py` passed: existing toolbar/order, Restore Defaults scope, layout drafts/Save/Discard, profiles, transforms, fonts, live display preferences, clock transport/setup, team entry and saved preview/OBS regressions.
- `test_ocr.py --ui` passed with simulated sources: seven independent fields, validation/ownership, successful/failed/lost connections, disconnect with active following or pending I/O, canceled late responses, stopped polling, retained values/settings, paused owned clocks and explicit following after reconnect. Restart remains manual/Ready/disconnected. Connection success still does not establish camera freshness.
- Extracted Windows GUI and console packages and extracted Linux package passed `test_http.py`: startup/version, game/clocks, SSE/auth, layout/background/profiles and restart persistence. `test_http_transport.py` passed on extracted Windows console and Linux binaries: 500 complete reset responses with `{}`, 500 with an empty body and 500 complete rejected optional-body actions on each OS, without retries masking failures.

## Packages and review images

The final Windows, Linux and source ZIPs include updated documentation. Documentation-only final repackaging preserves the freshly built and tested executable bytes; native runtime/UI/race evidence above is reused for those identical executables, not claimed as an additional runtime run.

`check_docs.py` passed 114 relative link/anchor checks. `verify_packages.py` passed source allowlist/content identity, embedded UI assets, executable formats/subsystems, Linux executable permissions, ZIP CRCs and SHA-256 checks. Expanded archives were checked for credentials, local settings/data and personal paths; Gitleaks reported no leaks. Package manifests and screenshot checksums accompany the delivery. All earlier local release files match the pre-work SHA-256 manifest; `prepare/v0.1.1` still points to `52f3458`, and the v0.1.0 tag/history are preserved.

The review folder contains 31 PNG screenshots and a separate screenshot ZIP: portrait/landscape canvas and button states for all four modes, Custom controls, full editor pages at all five widths, desktop/narrow details and real 200%/400% zoomed browser viewports. The 400% viewport naturally shows part of the vertically scrollable controls; the narrow full-page images show the complete stacked layout. Screenshots use isolated configuration and generated artwork, with no personal graphics or credentials. Desktop, narrow, Custom and zoom captures were visually inspected.

## Evidence boundaries and publication

Browser touch is emulated and OCR sources are simulated. No new physical touchscreen, tray interaction, production OBS, live-camera freshness, separate-machine LAN/firewall, Companion hardware or venue check is claimed. Browser OBS-page checks verify shared saved rendering; they do not establish behavior inside a production OBS installation.

Visual acceptance remains pending. v0.1.2 supersedes the planned v0.1.1 publication target: publish it as Latest after acceptance, verify public downloads/hashes, then remove only the v0.1.0 release entry/assets. Preserve v0.1.0's tag/history/local archives and the v0.1.1 checkpoint/packages. Public links/downloads are not changed or claimed newly verified during this local review pass.
