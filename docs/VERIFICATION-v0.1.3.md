# Field Scoreboard v0.1.3 verification

2026-11-22. Owner-authorized stable release preparation on `feature/ocr-automatic-time-format`, preserving checkpoint `efab87e472e7effd73128cdd3d1ebfd980814fd0` and public v0.1.2. [Release notes](RELEASE_NOTES-v0.1.3.md).

## Scope and evidence

The interrupted build completed `scripts/build.ps1`: Go test/vet, all seven embedded JavaScript syntax checks, and fresh CGO-free Windows GUI/console and Linux x64 binaries. That completed evidence is reused from `build.log`; binaries are retained without rebuilding. Against the accepted .4 checkpoint, runtime changes are only v0.1.3 labels and the blue Custom sizing CSS. OCR, timing, renderer and sizing logic remain frozen. Tests add focused Custom status color/screenshots and update version/evidence paths.

All new evidence is under `.test/release-v0.1.3/`. `before/work.tar.gz` and `before/audit.json` preserve source/binaries/screenshots and previous artifact hashes; `built-audit.json` records the retained release binaries and exact source. The Linux snapshot matches application and native test bytes. The retained binaries were built from the v0.1.3 working tree before its final commit; Go VCS metadata therefore names checkpoint `efab87e` with modified=true. Application/API/UI versions are v0.1.3, and tested runtime source/assets are byte-identical to the final release tree. No rebuild was performed merely to change VCS metadata. Historical .1/.2/.3/.4 evidence and archives remain preserved. Test data, generated images and listeners are isolated; no production scoreboard, live source or Field Timer is modified.

## Release checks

| Check | Result and evidence |
| --- | --- |
| Windows build/test/vet/JavaScript | PASS, completed before interruption in `build.log`; `scripts/build.ps1` runs Go test/vet and `node --check` for all seven embedded JS files before building all three executables. This evidence is reused against unchanged application bytes; `build-info.log` confirms CGO disabled, amd64 and trimpath. |
| Blue Custom sizing | PASS, `test_background_ui.log`: computed blue background/border/white text, dark unselected presets, 375/500/1000/1440/1920 px and actual 200%/400% zoom. Narrow/desktop (1920×1080) and zoom screenshots inspected. Existing sizing, aspect lock, legacy metadata, generated PNG/JPG/WebP, Save/Discard/profiles and editor/preview/OBS geometry pass. |
| Full browser/overlay regressions | PASS, all ten `test_*.log` files: offline UI, clocks, display, floating previews, OCR, backgrounds, elements, fonts, team names and legacy overlay. Mouse/emulated touch/keyboard, five widths, real zoom, drafts/focus/caret, dynamic choices, duplicate IDs/overflow, persistence and saved/draft output are covered. .4-to-v0.1.3 legacy overlay pixels match in all three scenarios. |
| OCR recognition and formatting | PASS, `test_ocr.log`: independent seven-field ownership, strict decimal recognition with automatic formatting ON/OFF, all five manual formats, both precisions/three appearances, dynamic examples, cancellation/reconnect/holds/restart, and 1,944 style/font/size/alignment/transform combinations each for operator and OBS. Simulated sources only. |
| Linux Go/vet/race and native | PASS, `linux-share/console.log` / `run.sh`: actual Alpine Linux x64 kernel 6.12.115 in isolated QEMU, Go 1.24.13 and GCC 14.2.0. `go test ./...`, `go vet ./...`, `CGO_ENABLED=1 go test -race ./...`, native simulated OCR and HTTP/transport end with `LINUX_RESULT_0`. |
| Extracted native packages | PASS, `windows-console-http.log`, `windows-gui-http.log`, `windows-transport.log`; Linux `command-completed.sh` / `console.log` ends with `PACKAGE_RESULT_0`. Windows GUI/console and Linux HTTP/API checks include independent clocks, state/SSE/auth/token rotation, layouts/images/profiles and persistence. Windows console and Linux each complete all 1,500 connection-close requests without retries. Final documentation-only packaging retains these exact tested executables. |
| Documentation/archive integrity | PASS, preflight and final `check_docs`, `package`, `verify_packages` logs and receipts: relative links/anchors, exact source/native inventories and bytes, embedded assets, platform formats, executable permissions, ZIP CRC and SHA-256. Final source matches the release Git tree; version labels and package names use v0.1.3. |
| Security and preservation | PASS, Gitleaks 8.30.1 reports no leaks in expanded source/native packages or recursively scanned archives; preflight/final redacted JSON/logs retained. Exact allowlists and personal-path/runtime-data scans pass. All prior artifact hashes match the pre-release audit. Temporary tools, test evidence, private data and generated binaries are excluded from Git/source publication. |

## Executable identity

| Executable | SHA-256 |
| --- | --- |
| Windows GUI | `097f25379d81f159633029cd02bfe1606ed1853348c086e0f5402b9c9b094f24` |
| Windows console | `d96c621d0ea8727b0c87af96c7f020da6edd38c84357eb72b3a1f2b83933b733` |
| Linux x64 | `e163b41a148ef9acf90ed0ab745a7736be96ae23e374234e7ec138feef181892` |

## Publication and limitations

Publication is authorized only after mandatory checks pass. Use a normal main fast-forward, a new `v0.1.3` tag and stable Latest release with three ZIPs plus checksum file. Never rewrite history, overwrite a tag or remove previous releases. Verify public unauthenticated downloads against local bytes, and main/tag/source identity. Store server metadata, download hashes and the final commit in the local publication receipt. Development is frozen after publication.

Physical touchscreen, Windows tray interaction, real ScoreSight/camera/video freshness, production OBS, separate-machine LAN/Companion and live-event checks remain operator work. Browser emulation and an actual Linux kernel in QEMU do not establish these passes. Historical owner-reported Linux acceptance is recorded separately. No live source was contacted during automation.
