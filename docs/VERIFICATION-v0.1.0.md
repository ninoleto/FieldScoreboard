# v0.1.0 release verification

Date: 2026-11-07. The owner accepted test.17 (`c7918be`) and explicitly authorized a normal v0.1.0 release. Acceptance is recorded without inferring additional physical/venue testing. The working tree was clean. Remote main remained the public test.8 commit, with no unrelated changes and no existing v0.1.0 tag/release. Authentication was confirmed as ninoleto.

## Release scope

The only application change after accepted test.17 is the requested Foul indicators heading/help cleanup, plus version metadata. App/renderer/OCR JavaScript, CSS, clock/API logic and persistence schemas are unchanged. Fresh Windows GUI/console and Linux binaries report v0.1.0; packages are built from this source, not renamed test archives. Test environments use isolated configurations and simulated OCR, leaving production settings and Field Timer untouched.

## Automated evidence

Windows Go tests/vet, all embedded JavaScript syntax checks and fresh Windows GUI/console/Linux x64 builds passed. Final source passed native Linux Go tests/vet/race with a C compiler in an isolated Alpine VM.

Full offline UI and native display/clock/team-name/background/element/Font suites passed at 375/500/1000/1440/1920 px. Checks cover touch emulation, mouse, keyboard/focus, dynamic dialogs, numeric drafts/caret protection, native 200%/400% zoom, clipping/overflow/duplicate IDs, exact wording/footer/version and panel placement. Narrow and desktop screenshots, including 1920×1080, were inspected. All quick adjustments, pending match presets, immediate shot presets, conditional resume, Set/format separation and OCR guards passed. Editor/background transforms, aspect locks, fonts/dots, Save/Discard, presets, restart and shared preview/overlay geometry passed.

Seven-field OCR/period browser and native simulations passed simultaneous/mixed ownership, per-field rejection/hold, delayed takeover, atomic combined/reset guards, connection transitions/loss/recovery, source pauses/resets, numeric/ordinal/Q parsing, independent display formats/OT, manual restart and final OCR-section order. These are simulated-source checks, not new observations of a live camera.

Extracted Windows GUI and console binaries and the Linux package passed version 0.1.0, clean defaults, startup/API/configuration/authentication and restart checks. New instances had HOME/AWAY, zero scores/fouls, period 1/Number, no artwork, Ready clocks and disconnected/manual OCR. Windows console and Linux each passed **1,500 HTTP transport requests without retries or connection resets**. The historical Windows connection reset did not recur. Automated startup of the GUI executable does not establish physical tray interaction.

All ZIPs passed CRC, manifest SHA-256, exact source/document inventory, executable format and embedded-asset checks. Release binaries differ from test.17 and match the bytes exercised by the native/browser checks. Expanded archives and the unpublished development history passed Gitleaks; personal-path/local-data review passed. 107 relative documentation links/anchors passed. Existing external links are checked before publication; the new release/download links are verified after they exist. Final documentation-only repackaging preserves the freshly built, tested executables and regenerates hashes. Earlier local package hashes, historical records and the public test.8 tag/release/assets are preserved.

Post-publication public-access, Latest/normal-release, documentation links and downloaded-asset SHA-256 verification are recorded in the GitHub release metadata, preserving the exact tagged source and archive bytes.

## Manual evidence and remaining checks

The operator reported Linux and its overlay working with OBS Flatpak on 2026-11-06 for test.8, and match-clock OCR working in the home setup with test.9. These are historical user-reported smoke tests, not venue validation or evidence that all seven OCR targets were physically tested. No new live ScoreSight or hardware test is claimed for this release; browser touch and source failures are emulated/simulated.

Physical touchscreen ergonomics, Windows tray behavior, actual OBS on the intended setup, real capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and live-event accuracy/latency remain operator checks. ScoreSight's observed JSON lacks a video heartbeat; cached HTTP success is not freshness evidence.

Preserve the [test.10 connection-reset history](VERIFICATION-v0.1.0-test.10.md), [test.11 fix](VERIFICATION-v0.1.0-test.11.md) and [test.17 evidence](VERIFICATION-v0.1.0-test.17.md). Investigate any future transport failure without masking it with retries. Earlier release notes/packages and public test.8 assets remain preserved.
