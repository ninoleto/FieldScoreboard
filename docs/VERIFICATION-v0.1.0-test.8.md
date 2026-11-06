# test.8 verification — 2026-11-06

## Completed application evidence (reused)

Before public preparation, the completed test.8 source matched its delivered source ZIP exactly, with no additional user files. The publication checkout preserves all application source, embedded assets and tested Windows GUI/console and Linux executable bytes. Documentation and release tooling are the only publication changes.

The following checks were completed for test.8 and their existing local logs were reviewed. They are reused for the unchanged application; no new physical hardware testing is claimed.

| Check | Recorded result |
|---|---|
| Windows Go tests/vet; embedded JavaScript syntax | PASS |
| Linux Go tests/vet/race | PASS |
| Windows GUI/console and Linux x64 builds, CGO_ENABLED=0 | PASS |
| Offline responsive UI and Fine position regression | PASS |
| Real-server background regression | PASS |
| Narrow/desktop screenshot review, including 1920×1080 | PASS |
| Extracted Windows/Linux HTTP smoke and restart | PASS |
| Original package CRC/SHA-256, embedded assets/formats and credential scan | PASS |

Fine position coverage: **5/10/20 px × four directions**, default 5, one selected/pressed choice, crossing and pressing at each boundary (X 0–1920, Y 0–1080). X/Y ±1 under every selected step and at bounds; font/dot increments; switching fields; mouse, emulated touch, Enter/Space; unchanged canvas shortcuts; polling/navigation and Save/Discard.

The retained UI suite checks all 21 numeric groups, 12 choice dialogs, drafts, navigation, focus, dynamic options, duplicate IDs and overflow at **375/500/1000/1440/1920 px**, plus **200%/400% native browser zoom**. The image suite covers square, portrait, banner and 1920×1080 PNG/JPG/WebP fixtures, original bytes, fit/fill/original/stretch, locked/unlocked resizing, explicit selection/gestures, clipping/alpha, editor/preview/overlay consistency, drafts, presets, legacy layouts and restart.

Native HTTP smoke covers clocks, combined time retention, conditional shot reset, scores, OT, visual shot hiding, SSE, auth/token rotation, network discovery, image/layout/profile persistence and startup. Screenshots/logs and temporary configurations are local test artifacts, excluded from source and packages.

Recorded toolchains: Windows Go 1.27.3 / Node 24.18.0; Linux Go 1.24.13 / Alpine 3.22.8 amd64 in an isolated VM; Chrome/Playwright. These are test tools, not runtime dependencies.

## Executables retained for public packaging

| Executable | SHA-256 |
|---|---|
| Windows GUI | `0fdcda1303abe939dacb41e776fcd10b89690847dc5d81d7af09296a0f669153` |
| Windows console | `b58cecc422d39f41a3bc6205a4f809241d2e291733e0745e23d741326f96f068` |
| Linux x64 | `26ebdc80bb8b785c54f000bd257333b8be3da8b173952e1dbbea304d73e6ac8e` |

Archive hashes change because documentation/package contents change. Final ZIP hashes are in the separate release `SHA256SUMS.txt`.

## Publication checks

Publication gates: source/executable byte comparison; documentation/code review; relative link/anchor checks in source and all packages; exact allowlisted source inventory; archive CRC/SHA-256 and platform/embedded-asset checks; expanded archive and exact source secret scans. Final results are recorded below before publication.

Post-upload public access, external download links and hashes of every downloaded asset are verified after upload and recorded in the GitHub release notes. This packaged document cannot contain evidence of a future download of itself.

## Manual evidence and remaining checks

**User-reported manual smoke test on 2026-11-06:** the Linux application and its overlay work with OBS Flatpak. Earlier operator confirmation of test.6 background selection/manipulation is retained in [handoff](../handoff.md).

Still operator-pending: physical 24-inch touchscreen evaluation, native Windows tray, installed Windows OBS, detailed scene/image checks, separate-machine LAN OBS/firewall, actual Companion control and live-event production rehearsal. No touchscreen, tray, LAN, Companion or live-event test is inferred from the Linux/Flatpak report.

### Repackaging results

| Check performed for publication | Result |
|---|---|
| Application source/assets and all three executable bytes compared with completed test.8 | PASS; hashes above retained |
| Windows Go tests/vet and all JavaScript syntax checks rerun | PASS |
| Newly repackaged Windows console HTTP smoke/restart with isolated configuration | PASS |
| README/user/developer instructions checked against source; API methods, paths, storage and reset behavior | PASS |
| Relative documentation links/anchors in source and each ZIP | PASS |
| Explicit source inventory, archive CRC/SHA-256, platform formats and embedded assets | PASS |
| Gitleaks scan of exact public source and expanded release archives; personal-path/data review | PASS; no leaks found |

Linux native/race and browser/image/screenshot checks above are reused, not newly rerun for documentation-only packaging. Final Git index/source archive equality and scans are release gates. External GitHub links and downloaded asset hashes are checked after publication and reported on the release page.
