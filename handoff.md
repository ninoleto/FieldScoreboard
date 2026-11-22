# Field Scoreboard handoff

## Current local development — v0.1.2-ocr-format.4 (2026-11-22)

The operator accepted .3 functionality and requested only ScoreSight Match clock UI wording/usability before a future v0.1.3. Public v0.1.2 is unchanged. Continue on `feature/ocr-automatic-time-format`, base `2f85c9a`. No commit, push, tag, publication, release deletion or cleanup is authorized.

Implemented the requested switch label, Time precision choices and Final-minute appearance choices/descriptions, with examples updated for whole seconds/tenths. The existing shared dialog has 64 px OCR choices, whole-option selection and descriptive closed captions; keyboard/focus behavior remains. Short help text replaces the technical paragraph, with an additional message only when automatic switching is off. OCR parsing/ownership/precision, automatic output logic, manual formats, renderer/alignment, card order, layout geometry, network and auth remain unchanged. The only Go change is the .4 version constant.

Verification is complete: focused choice/OCR checks, all ten browser/overlay regressions, Windows Go/test/vet/JS, Linux Go/test/vet/race, extracted Windows GUI/console and Linux native HTTP/transport, package integrity/SHA-256, documentation and secret/personal-path scans pass. Windows GUI/console and Linux x64 were rebuilt once for changed embedded assets. A zoom screenshot harness correction was verified separately; no application correction was needed. Evidence, `final-receipt.json` and the pre-edit source/binary/screenshot snapshot are under `.test/ocr-format4/`; all 205 previous archive/manifest hashes remain unchanged. Verified Windows, Linux and source ZIPs plus `SHA256SUMS.txt` are in `dist/v0.1.2-ocr-format.4/`. All .1/.2/.3 packages and existing local work remain preserved. No required automated check remains incomplete. Physical touch, tray, real ScoreSight/video freshness, production OBS and separate-machine LAN/Companion remain operator checks. Stop here for operator approval; no GitHub operations were performed. See [current verification](docs/VERIFICATION-ocr-format.md) and [operator test instructions](docs/RELEASE_NOTES-ocr-format.md).

## Current local development — v0.1.2-ocr-format.3 (2026-11-22)

Continue on `feature/ocr-automatic-time-format`, base `2f85c9a`. The owner requested only three corrections and local verified packages. Do not commit, push, tag, publish, remove releases/files, reset or clean. All prior work, .1/.2 archives, configurations and evidence remain preserved; `.test/ocr-format3/before/` holds the pre-edit source/binary snapshot and archive hashes.

Implemented: Match OCR recognition accepts MM:SS or final-minute SS/SS.t regardless of Automatic OCR time format; exact tenths and explicit ownership remain, OFF uses the existing manual format/rounding. Presentation changes no longer invalidate readings. Clean SS.t uses natural text width with existing left/center/right anchors, without hidden prefixes; whole-second and visible/invisible tenths retain their alignment columns. ScoreSight cards read Home/Away score, Home/Away fouls, Period/Shot clock, then full-width Match clock; mobile and keyboard follow the same DOM order. Underlying target order, IDs/mappings/API, shot parser, floating previews, drafts and upright UI typography remain intact.

Targeted and full Go/native/browser checks pass, including all ten browser/overlay suites, Linux test/vet/race with GCC, simulated OCR and Windows/Linux extracted HTTP/transport. During verification resumption, application source, tests and all three existing .3 binaries stayed unchanged; no rebuild or failure correction was needed. Final documentation, ZIP integrity/SHA-256, exact source/executable comparisons, Gitleaks and personal-path/runtime-data scans pass. No automated verification blocker remains. See [current development verification](docs/VERIFICATION-ocr-format.md) for exact evidence and limitations. The verified local approval set is `dist/v0.1.2-ocr-format.3/` (Windows GUI/console, Linux x64 and source ZIPs plus `SHA256SUMS.txt`). Final packages are made from a fresh exact-source staging tree with the tested binaries, leaving the earlier top-level .3 candidate archives/manifest and every .1/.2 archive untouched. New evidence and `final-receipt.json` are under `.test/ocr-format3/resume/`. Since resumption only this handoff, the current verification report and local release notes changed; application and test source remain identical. [Release/test instructions](docs/RELEASE_NOTES-ocr-format.md) describe .3 behavior and isolated operator checks. No GitHub operations were performed. Stop here for operator approval.

Physical touchscreen/tray, real camera/video freshness, production OBS, separate-machine LAN/Companion and live-event checks remain operator work. Earlier .2/.1 and public-release history follows below.

## Current local development — v0.1.2-ocr-format.2 (2026-11-22)

Work remains on `feature/ocr-automatic-time-format` at base `2f85c9a`, with the existing uncommitted feature work preserved. The current task explicitly prohibits push, tagging, publication, deletion, reset and cleanup. Stop after verified local packages for owner approval; historical publication authorization below does not apply.

Already implemented: visible/invisible-zero and clean-second final-minute OCR styles with independent optional tenths; original upright interface typography; optional floating previews in Live control and Layout editor, including unsaved drafts. Defaults, ownership, exact observed times and saved manual formats are preserved. Floating preferences are per page in browser storage and never write layout/game/clock APIs.

Verification resumption preserved source/logs/screenshots and hashed all application files and binaries under `.test/ocr-format2/resume/`. Completed .2 OCR/clock/display/font/name/floating/legacy runs were audited and reused. Offline, background and element suites now pass; only test-harness corrections were required (selector count and waiting for scheduled canvas scaling). Application source and all three binaries remain unchanged. Extracted Windows GUI/console HTTP and 1,500-request transport checks pass. Linux Go/test/vet/race, native simulated OCR and extracted Linux HTTP/transport now pass in an isolated Alpine/QEMU VM. Final documentation, ZIP integrity/SHA-256, exact source/executable comparisons, Gitleaks and personal-path/runtime-data scans pass. See [development verification](docs/VERIFICATION-ocr-format.md) for the complete reused/new evidence and executable hashes. No automated verification blocker remains.

The complete approval set is `dist/v0.1.2-ocr-format.2/`: Windows GUI/console, Linux x64 and source ZIPs plus `SHA256SUMS.txt`; identical copies are at the top of `dist/`. Final logs, expanded archives and `final-receipt.json` are under `.test/ocr-format2/resume/`. Candidate/preflight packages and the previous manifest are preserved there. Only regression harnesses and documentation changed during resumption; application files and tested executables are byte-identical. No GitHub operations were performed. Stop here for owner approval.

Current user/developer docs and [local rehearsal instructions](docs/RELEASE_NOTES-ocr-format.md) describe .2. Prior .1 packages, documentation history and interrupted logs remain available. No live source or production configuration was accessed. Physical touch, tray, live ScoreSight/video freshness, production OBS, separate-machine LAN/Companion and live-event checks remain separate operator work.

The next section preserves the completed .1 development history; public v0.1.2 history follows it.

## Local development — automatic OCR time format (2026-11-22)

Work is on `feature/ocr-automatic-time-format`, based on clean `main` at `2f85c9a`. Local version is **v0.1.2-ocr-format.1**; public v0.1.2, main, tags and release assets remain untouched. The owner's current instruction explicitly prohibits push/tag/publication/removal and supersedes historical publication/retention authorization for this task. Stop at the tested local build and await owner approval.

Added optional **ScoreSight → Match clock → Automatic OCR time format**, disabled by default, with SS/SS.t final-minute choice. Exact source tenths are held in Go without independent ticks. Only while following main OCR, display is MM:SS at/above 60 and SS/SS.t below; SS omits tenths without rounding up. Manual Output format remains saved and returns on takeover/Disconnect with the same paused duration. Settings persist outside layouts/profiles; restart stays manual/Ready/disconnected. Other OCR targets and manual controls are unchanged. Legacy parsing remains when disabled; enabled inputs are strict M:SS/MM:SS or final-minute SS/SS.t, not guessed separators/fractions.

The original 01:00 → 55.4 freeze was reproduced with the preserved v0.1.2 binary and a simulated source. New tests include exact precision, threshold/reset, invalid/loss handling, takeover, config compatibility/persistence, API authentication, isolated revisions, preview/OBS, touch/keyboard, focus, layout drafts and real browser zoom. New controls were corrected to 64-pixel minimum targets and to restore focus after pending preference writes. Older browser tests needed explicit asynchronous-event/action synchronization; actual zoom requires full Chromium instead of the newer Playwright headless shell. See [local test instructions](docs/RELEASE_NOTES-ocr-format.md) and [development results/files/checks](docs/VERIFICATION-ocr-format.md). All configurations/ports/sources used in this task are isolated; no live source or production scoreboard was contacted.

Interrupted verification was completed on 2026-11-22. Extracted Windows GUI/console HTTP smoke and console transport passed; the final extracted Linux executable passed HTTP, transport and simulated OCR in an isolated Alpine/QEMU VM. Prior Linux Go/test/vet/race evidence was checked against all 26 unchanged Go/module files. Existing final browser-suite logs were retained; the focused OCR format suite was rerun after fixing blank zoom screenshots in the test harness (direct viewport capture plus a blank-image assertion). Application source and all three tested executable hashes remain unchanged during this resumed work. Windows sandbox temporary-folder failures were resolved by approved execution outside the sandbox with workspace test data.

Final documentation, ZIP CRC/SHA-256, exact source/executable comparison, Gitleaks and personal-path/data scans passed. The complete local test set is `dist/v0.1.2-ocr-format.1/` (three ZIPs plus `SHA256SUMS.txt`), also available at the top of `dist/`. Pre-resume packages remain under `.test/ocr-format/resume-linux/`; older archives are untouched. Logs/screenshots and the final receipt are under `.test/ocr-format/`. No push, tag, publication, release deletion or Git reset/cleanup was performed. Physical touch, actual tray interaction, real ScoreSight/camera, production OBS and separate-machine LAN/Companion checks remain for the operator. The release notes now include isolated Windows/Linux launch commands and a real-source rehearsal procedure.

The material below records the unchanged public v0.1.2 history.

Version **v0.1.2**, 2026-11-07. Repository: [ninoleto/FieldScoreboard](https://github.com/ninoleto/FieldScoreboard). Release: [Field Scoreboard v0.1.2](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.2). The owner accepted the interface at `e9f19cdc2e1dd2b9942dc94010422a043d736a16`, reported **Linux test PASSED** and explicitly authorized publication as the normal Latest release. Final publication changes documentation and ZIP permission metadata only; application source, launchers and tested executable bytes remain unchanged. Field Timer was untouched.

Read [AGENTS.md](AGENTS.md), [user guide](docs/USER_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.2.md) and [verification](docs/VERIFICATION-v0.1.2.md). The [original review evidence](docs/VERIFICATION-v0.1.2-review.md) is a historical record and its review-stage status is superseded by the acceptance above.

## Included behavior

- ScoreSight has independent Connect/Disconnect controls and a text/color backend status badge. Disconnect cancels polling/in-flight I/O, returns followed fields to manual with values retained and leaves owned clocks paused. Address/mappings persist; reconnect never restores ownership or starts clocks. Successful HTTP polling cannot prove camera freshness.
- The editor has top Restore Defaults, Discard, Save Layout actions, coordinate help beneath X/Y, Free transform left and Edit background right, aligned desktop card edges and a separate Layout profiles card below. Reset scope is unchanged.
- Background Sizing uses four visible Fit/Fill/Original/Stretch buttons with explanations and green selected border/checkmark. Manual adjustments show Custom sizing with no preset selected. Aspect lock, numeric controls, Center/Reset, gestures, draft Save/Discard, profiles and shared saved preview/OBS geometry are preserved. Narrow screens stack large targets.

## Startup and configuration

Windows: extract the complete ZIP into a writable folder, then double-click `fieldscoreboard.exe`; exit through its tray menu. Use `start-portable.cmd` for data beside the executable.

Linux: from the extracted application directory:

```bash
chmod +x start-portable.sh fieldscoreboard
./start-portable.sh
```

Sudo is unnecessary. The terminal stays open while the app runs; Ctrl+C stops it. The interface is at http://127.0.0.1:8790. Linux has no tray. Portable launchers use the extracted folder's config; direct executables use the user config directory unless `--config` is supplied. Upgrades must retain the launch mode/path and `config.json`, `profiles/`, `backgrounds/` together. See the guide for exact locations.

## Release and retention

The final release is integrated into main without force-pushing and tagged `v0.1.2`; normal release flags are draft=false/prerelease=false, with Latest selected. The final source ZIP must agree with that commit and platform documentation. Final packages/checksums and publication receipts live under the workspace's `releases/v0.1.2-published/`; original review files remain in `releases/v0.1.2/`. Keep `prepare/v0.1.1` at `52f3458` and `prepare/v0.1.2` at `e9f19cd`.

The owner's current removal authorization covers **all older GitHub releases and attached assets in ninoleto/FieldScoreboard**, including tests/prereleases, superseding the earlier v0.1.0-only plan. Removal follows successful unauthenticated download/hash verification and main/tag/source agreement. Preserve full release/asset metadata and all attached assets in the local GitHub archive first; retain all Git tags, history and existing local release archives. Initial remote inventory contained v0.1.0 and v0.1.0-test.8. The local publication receipt and release-page verification record report the final outcome; do not infer future cleanup authorization from this one-time operation. Other repositories are out of scope.

## Verification boundaries

The accepted interface and owner-reported Linux PASS are recorded accurately. Reuse the historical Go/vet/Linux race, responsive/zoom, OCR/clock/layout and native-package tests only for the identical application/executable bytes. Final documentation/archive/link/permission checks and public download verification are separate publication checks.

No additional physical touchscreen, Windows tray, production OBS, venue OCR or live-video freshness, separate-machine LAN/firewall or Companion hardware pass is claimed. Historical test.8 Linux OBS Flatpak/test.9 home OCR reports remain scoped reports. Preserve the test.10/test.11 HTTP reset investigation and never hide transport failures with retries. Automatic sport rules, NDI, direct OBS control and verified video freshness remain future work.
