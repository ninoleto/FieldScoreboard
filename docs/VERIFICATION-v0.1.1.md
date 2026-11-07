# v0.1.1 review verification

Date: 2026-11-07. Base: released v0.1.0 commit `12e81de`. The checkout was clean before work. The owner requested a focused update with local packages/screenshots for visual acceptance before publication. No release/tag has been published or deleted.

## Automated checks

Windows Go tests/vet and all embedded JavaScript syntax checks passed. Fresh Windows GUI/console and Linux x64 executables were built with `scripts/build.ps1`. Native Linux tests/vet/race passed in the isolated Alpine VM with Go and GCC; released binaries remain CGO-free.

The native OCR suite and new Go connection tests cover seven retained values, paused owned clocks, cancellation of an in-flight request, no further polling after Disconnect, late successes/errors across reconnect, preserved address/mappings, explicit following after reconnect, pending cancellation and idempotent Connect. Existing seven-field, period/OT, strict parsing, per-target takeover, clock ownership, source pause/reset/loss/recovery and restart regressions passed. Browser checks cover successful/failed/lost/reconnected states, disconnected restarts, duplicate pending Connect/Disconnect prevention, backend status with all fields manual, focus/scroll stability and large source selectors at all five widths.

Offline UI and native background, element, display, font, clock and team-name suites passed at 375/500/1000/1440/1920 px. Coverage includes touch emulation, mouse/keyboard, unfinished drafts/caret, choice dialogs, selected states, duplicate IDs, overflow and native 200%/400% browser zoom. Editor checks assert matching desktop card edges, profiles below both columns, top action order and coordinate-help placement. Save/Discard, profile save/load/delete, Restore Defaults scope, live-data isolation, background aspect/clipping/transparency, font transformations and shared preview/overlay rendering passed. Screenshots include a 1920x1080 viewport and full-page desktop/narrow views with generated artwork only.

One existing display test assumed a maximum 30 px live-preview gap. The released v0.1.0 and candidate measured identically (32.28125 px at 1440 px), because the taller score card contributes to both grid rows. The test now checks the actual column boundaries and separation; no live-layout change was made for this assertion.

Screenshot inspection caught an obsolete source-success label after Disconnect. The final correction clears that label and shows Disconnected — value retained. Fresh binaries were rebuilt; Go tests/vet/JavaScript checks, native Linux tests/vet/race and the full native/browser OCR suite passed again. The other UI-suite evidence applies to unchanged editor, clock, font, background and team-control code.

Extracted Windows GUI and console packages and the Linux package passed clean startup, version 0.1.1, defaults, API/authentication, layout/profile/background and restart smoke tests. The final Windows console and Linux executables each passed **1,500 HTTP transport requests without retries or connection resets**. Native Linux also passed the full simulated OCR/period/connection suite against its extracted binary.

All three ZIPs passed CRC integrity, SHA-256, source/document inventory, embedded assets and executable-format checks. Expanded executable bytes match those tested and differ from v0.1.0. The exact expanded source/platform archives passed Gitleaks and personal-path/local-data review. All 111 relative documentation links/anchors passed. Final documentation-only repackaging retained the exact tested executable bytes and regenerated hashes. Earlier local release-file hashes and the v0.1.0 Git tag/history were preserved.

Delivery is under `releases/v0.1.1/` outside the checkout: Windows/Linux/source ZIPs with `SHA256SUMS.txt`, 27 PNG review screenshots, and `FieldScoreboard-Screenshots-v0.1.1.zip` with `SCREENSHOTS-SHA256SUMS.txt`. The screenshots cover all five editor widths, desktop/narrow top and profile details, eight OCR states at desktop/narrow widths, and full-page native 200%/400% zoom. They use a simulated loopback source and generated test artwork only. Review artifacts are not committed to Git.

## Scope of evidence

All new OCR observations are simulated. No new physical touchscreen, tray interaction, production OBS, live-camera freshness, separate-machine LAN/firewall, Companion hardware or venue test is claimed. Historical operator-reported test.8 Linux/OBS Flatpak and test.9 home match-clock OCR checks remain scoped to those versions. Successful HTTP polling cannot verify camera freshness.

## Acceptance and release order

Visual acceptance is pending. After acceptance: publish v0.1.1 as a normal Latest release; verify unauthenticated access and downloaded asset SHA-256; then remove only the v0.1.0 GitHub release entry/assets. Keep its tag/history/local archives and unrelated releases. Public verification is not part of this unpublished review pass.
