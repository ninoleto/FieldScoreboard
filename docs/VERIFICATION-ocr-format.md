# Local v0.1.2-ocr-format.4 verification

2026-11-22. Branch `feature/ocr-automatic-time-format`, base `2f85c9afae20a137bac2a6d146edb4eab1d6d3eb`. The operator accepted .3 functionality. This is a local UI usability update only; public v0.1.2 and all .1/.2/.3 archives remain unchanged. No commit, push, tag, publication, deletion or other-repository change is authorized or performed.

## Scope and preservation

`before/work.tar.gz` preserves the pre-edit publication source, three binaries and existing top-level screenshots. `before/audit.json` records source/binary and 205 archive/manifest hashes. New .4 logs/screenshots/staging live in `.test/ocr-format4/`. Prior verification below remains historical; changed application assets and rebuilt .4 executables receive fresh checks.

Runtime edits are limited to the .4 version constant and operator HTML/CSS/JavaScript: the requested switch/help wording, Time precision captions, Final-minute appearance captions/descriptions, examples synchronized with selected precision, and off-state help. The shared choice dialog optionally displays descriptions and gives these OCR options a 64 px minimum height; existing buttons, event handling, selected highlighting and keyboard/focus restoration remain. Description text is inserted with `textContent`. No preview panel is added.

OCR parsing, exact precision, ownership, automatic/manual formatting, persistence/API, shot/game controls, shared renderer/overlay styles, floating renderer and saved layout geometry are unchanged. Go differs only in `Version`. Internal precision/style strings and field IDs remain unchanged. Detailed source precision, rounding and alignment remain in the user guide/OCR plan. Current release notes and safe test commands use .4 and the new labels.

## Automated checks

| Check | Result and evidence under `.test/ocr-format4/` |
| --- | --- |
| Build, Go tests/vet and JS | PASS, `build.log`: Windows `scripts/build.ps1`, all Go tests/vet, seven JavaScript syntax checks, rebuilt Windows GUI/console and Linux x64 with CGO disabled/trimpath. |
| Focused OCR and usability | PASS, `targeted.log` and `targeted-verified.log`: both precisions/all three appearances, dynamic examples including an externally changed setting while the dialog is open, saved values/restart, accessible closed labels, selected styling, 64 px options, full-row taps, keyboard/focus, five widths and actual 200%/400% zoom. Existing decimal OCR ON/OFF/manual-format matrix, ownership/holds and 1,944 geometry combinations each for operator/OBS pass. |
| Relevant full regressions | PASS: `primary-runner.log` / `editor-runner.log` and all ten individual logs: OCR, offline UI, clock, display, floating preview, backgrounds, elements, fonts, team names and legacy overlay. Shared dialog regressions include drafts, dynamic options, keyboard/focus, five widths, real zoom, duplicate IDs/overflow and saved/draft previews. .3-to-.4 legacy OBS pixels match for default, font/alignment/dot and background scenarios. |
| Linux test/vet/race and native | PASS, `linux-share/console.log`, `run.sh`, `linux-runner.log`: Go 1.24.13, GCC 14.2.0, Alpine x64 kernel 6.12.115. `go test ./...`, `go vet ./...`, `CGO_ENABLED=1 go test -race ./...`, simulated native OCR, HTTP and transport complete with `LINUX_RESULT_0`. |
| Extracted native packages | PASS: `windows-console-http.log`, `windows-gui-http.log`, `windows-transport.log`; extracted Windows GUI/console smoke and 1,500 console transport requests. Linux extracted executable hash, HTTP and 1,500 transport requests pass in `linux-share/command-completed.sh` / `console.log`, ending `PACKAGE_RESULT_0`. No transport retries. Final packages retain the exact tested executable bytes. |
| Visual review | PASS: narrow/desktop appearance dialogs and closed controls, including 1920×1080 and corrected actual 200%/400% zoom captures inspected. |
| Documentation/package/security | PASS: `final-check_docs.log`, `final-package.log`, `final-verify_packages.log`, `final-delivery.log`, `final-receipt.json`; 137 documentation links/anchors, exact source/native inventories and bytes, embedded assets, portable formats/permissions, ZIP CRC and SHA-256. Gitleaks 8.30.1 finds no leaks in expanded source/native archives or final packages (`gitleaks-final-expanded.*`, `gitleaks-final-packages.*`); personal-path/runtime-data scans pass. All 205 previous archive/manifest hashes are retained. |

The new `ocr_usability_checks.py` is called by the existing OCR format UI suite. Existing version expectations and versioned OCR/floating screenshot paths were updated. Visual inspection found that the initial dialog screenshot method could save blank images at real browser zoom despite passing interaction assertions. Only the test capture was corrected to use the established CDP viewport method with a nonblank assertion; original captures remain, and corrected files end in `-verified.png`. The affected focused suite passes again in `targeted-verified.log`; application bytes are unchanged by this harness correction. All configurations, images, source readings and listeners used in automation are isolated test data. No production configurations/layouts/graphics/OBS settings or live ScoreSight state were changed.

## Packages

Approval folder: `dist/v0.1.2-ocr-format.4/`, containing `FieldScoreboard-Windows-v0.1.2-ocr-format.4.zip`, `FieldScoreboard-Linux-v0.1.2-ocr-format.4.zip`, `FieldScoreboard-Source-v0.1.2-ocr-format.4.zip` and `SHA256SUMS.txt`. Packaging/verification run the unchanged repository scripts in a fresh exact-source staging tree, preserving the original top-level candidate archives and manifest. Tested binaries are retained for final documentation-only repackaging. Native tests use the extracted preflight packages; final archives have identical executables. The only post-preflight test change fixes zoom screenshot capture in the new browser helper; native harnesses and runtime code remain byte-identical. `scope-audit.json` / `runtime-scope.patch` record changes against accepted .3. All required automated checks are complete with no unresolved application failure. The owned test VM is stopped after its checks; no other application is stopped. The final receipt records file hashes/inventories; previous archives are checked against the pre-edit audit.

| Executable | SHA-256 |
| --- | --- |
| Windows GUI | `19632ecc05c4cb16e8e89297eb35a247068cbb3a166344ce1451259d7bde55ca` |
| Windows console | `01e061469f306ce61dc37bf63e07c0f4cc843bd0b3cf2148e1c4ce4b9a9d9c8b` |
| Linux x64 | `ccf44532657ad397b4a4e092a03d9ce22b05b2b2abe64a9199005ba6dfe032f0` |

## Limits

Physical touchscreen, actual Windows tray interaction, real ScoreSight/camera/video freshness, production OBS, separate-machine LAN/Companion and live-event checks remain operator work. Browser touch/zoom tests and Linux execution in QEMU do not establish those passes. The operator's .3 acceptance is separate from this .4 automated evidence. See [isolated operator test instructions](RELEASE_NOTES-ocr-format.md).

---

# Local v0.1.2-ocr-format.3 verification

2026-11-22. Branch `feature/ocr-automatic-time-format`, base `2f85c9afae20a137bac2a6d146edb4eab1d6d3eb`. Local operator-review build only: no commit, push, tag, publication, release removal or cleanup. Existing uncommitted work and all .1/.2 archives are preserved. Prior .2/.1 verification history follows this record.

## Reproduction and focused corrections

Before edits, `.test/ocr-format3/before/work.tar.gz` preserved the complete publication source, existing binaries and top-level screenshots. `before/audit.json` records source/binary/archive hashes, and the prior top-level checksum manifest is retained separately. Tests use isolated temporary configurations, generated images and random loopback ports; no production configuration or live ScoreSight endpoint was used.

`reproduce-go.log` reproduces .2 rejecting `48.2` with the automatic override off. `reproduce-ui.log` records clean SS.t occupying approximately 107.11 presentation pixels versus 62.48 for identical natural text, and the old Match-first DOM order. The focused changes are:

- Match observations always accept strict MM:SS or final-minute SS/SS.t, with exact `time.Duration` precision. The presentation toggle no longer controls parsing or invalidates observations. Valid observations can become available while manual, but only explicit Follow takes ownership. OFF uses the saved Match Clock format/direction/rounding; ON uses existing automatic options. Shot and unrelated parsers, ownership revisions on takeover/mapping/connection, authentication and API contracts are unchanged.
- Shared rendering uses plain natural text for clean SS.t (including the natural MM:SS text above one minute). No hidden prefix or reserved column exists in that mode. Whole-second modes and visible/invisible-zero tenths retain their columns. Saved anchors/transforms, fonts and layout coordinates are unchanged.
- OCR card DOM order is Home score, Away score, Home fouls, Away fouls, Period, Shot clock, Match clock. Match spans both desktop columns; narrow layouts retain that reading/tab order. All card contents/IDs/mappings remain, and backend target order is unchanged.

Version changes are limited to .3 labels/test expectations. Upright typography, floating saved/draft previews, manual controls, Companion/API, network/auth and persistence are preserved. User/developer docs describe the recognition/presentation distinction and include focused operator rehearsal steps.

## Automated evidence

All .3 logs are local under `.test/ocr-format3/`. Prior .2 application-test results are historical, not substitutes for the new .3 tests. Targeted checks precede full regression checks; failed reproduction logs are expected evidence, not passes.

| Check | Result and evidence |
| --- | --- |
| Targeted Go | PASS, `targeted-go.log`: five manual formats × both directions × automatic ON/OFF × precision/style; explicit following, exact holds, rejected/lost sources, in-flight presentation updates, stale takeover rejection, defaults/persistence/API. |
| Targeted native/browser | PASS, `targeted-ui.log`: manual output menu unchanged; decimal OCR across all five formats with override ON/OFF; exact holds/loss/recovery; 1,944 combinations each in operator/OBS for preview/editor/floating classes, fonts/sizes/anchors/transforms, natural clean SS.t and retained other columns; card DOM/grid/keyboard order, five widths, actual 200%/400% zoom, focus, drafts and restart. |
| Windows build/Go/vet/JS | PASS, `build.log`: `scripts/build.ps1`, Go 1.27.4, all Go tests/vet, all seven embedded JavaScript syntax checks, Windows GUI/console and Linux x64 builds with CGO disabled and trimpath. |
| Full browser regressions | PASS: `primary-runner.log` and `editor-runner.log` completed with exit 0; individual `test_ocr`, `test_clock_ui`, `test_display_ui`, `test_floating_ui`, `test_ui_offline`, `test_background_ui`, `test_elements_ui`, `test_font_ui`, `test_team_names_ui`, `test_legacy_overlay` logs all pass. Includes five widths, mouse/emulated touch/keyboard, real 200%/400% zoom, drafts/focus, dynamic options, duplicate IDs/overflow, shared rendering, ownership and restart. Legacy pixel comparison is .2-to-.3. |
| Linux Go/test/vet/race | PASS: `linux-share/console.log`, `run.sh` and `linux-runner.log`; Go 1.24.13 and GCC 14.2.0 on Alpine x64, kernel 6.12.115. `go test ./...`, `go vet ./...`, `CGO_ENABLED=1 go test -race ./...`, simulated native OCR and HTTP/transport complete with `LINUX_RESULT_0`. |
| Native and extracted packages | PASS: `resume/windows-console-http.log`, `resume/windows-gui-http.log`, `resume/windows-transport.log`; both Windows executables pass smoke and console passes 1,500 transport requests without retries. Linux extracted hash/HTTP and 1,500-request transport pass in `linux-share/console.log` / `command-completed.sh`, ending `PACKAGE_RESULT_0`. Final packages retain identical tested executable bytes. No tray or Linux browser pass is claimed. |
| Screenshot inspection | PASS: inspected the four-row desktop OCR panel, 375 px Match controls, natural clean SS.t overlay, floating editor at 1920×1080, and 200%/400% captures. Automated grid/tab/overflow assertions passed at all required widths. |
| Documentation/package/security checks | PASS: `resume/final-check_docs.log`, `final-package.log`, `final-verify_packages.log`, `final-delivery.log` and `final-receipt.json`; 132 relative documentation links/anchors, exact source/native inventories and bytes, embedded assets, ZIP CRC/SHA-256, portable formats/permissions and personal-path/runtime-data scans. Gitleaks 8.30.1 reports zero findings on expanded source/native archives and final packages (`resume/gitleaks-final-expanded.*`, `gitleaks-final-packages.*`). Preflight archives/scans are retained separately. |

New regression coverage lives in `ocr_corrections_test.go` and `ocr_correction_checks.py`, with updated formatting/renderer/grid assertions in existing OCR suites. Old recognition tests were updated to the requested independent-input semantics. Existing .2 screenshot locations remain intact; .3 OCR/floating captures have their own directory. Browser suites use the installed full Chromium outside the Windows sandbox because sandboxed Playwright subprocesses cannot launch; this is isolated automation, not physical touchscreen verification.

## Resumed verification and preservation

At resumption both full browser runners had completed successfully. Their passing results were reused after comparing all application files against the Linux source snapshot and all three binaries against the existing .3 candidate ZIPs. `resume/audit.json` records the exact source/binary/archive/log hashes; `resume/source-before.tar.gz` preserves the resumption source. The existing Linux runner was allowed to finish; its extracted-package checks were added through its existing command queue. Windows extracted smoke/transport and a fresh seven-file JavaScript syntax check (`resume/javascript.log`) completed during resumption. The owned verification VM was stopped afterward.

No application code, regression tests or binaries changed during resumption, and no rebuild was needed. Only `handoff.md`, this verification record and `RELEASE_NOTES-ocr-format.md` were finalized. No unresolved application/test failure remains; expected .2 reproduction failures are retained separately. Safe test procedures use independent configuration files/listeners and the loopback simulator.

Packaging runs the repository's unchanged `scripts/package.py`, `scripts/verify_packages.py` and `scripts/check_docs.py` from a fresh exact-source staging tree under `resume/final-source/`, with copies of the tested binaries. This preserves every original top-level `dist/` archive/manifest, including the earlier .3 candidate set. Use the versioned approval folder below. Final source/native inventories are compared byte for byte with the working tree/binaries; `.1`/`.2` and all earlier archive hashes are checked against the pre-resume audit. Logs and the final receipt live under `resume/`.

## Packages and executable identity

Approval destination: `dist/v0.1.2-ocr-format.3/`, with `FieldScoreboard-Windows-v0.1.2-ocr-format.3.zip`, `FieldScoreboard-Linux-v0.1.2-ocr-format.3.zip`, `FieldScoreboard-Source-v0.1.2-ocr-format.3.zip` and `SHA256SUMS.txt`. Windows includes GUI and console binaries; Linux is CLI with no tray. Native packages include launchers and the documentation set. The source ZIP includes simulator/test scripts and excludes runtime configuration, personal artwork, tools and generated binaries.

| Executable | SHA-256 |
| --- | --- |
| Windows GUI | `194187c7a77a0db3a6fcb057259554899f4c4e73dba6fbba9756cdfb00d7e7e6` |
| Windows console | `bb6250f28631bb578a33a34c15c76d5d94aa7b05a24c3c2da219b1e80fb7f79b` |
| Linux x64 | `743d06b9a9bd1fc575a1285096c8bf2986beffb61a44fb22d7ce10b4400e8da5` |

Final package hashes are recorded in the versioned checksum manifest and local `final-receipt.json`. Earlier .1/.2 packages, candidate archives and test evidence remain local; publication requires separate approval.

## Verification limits

No new physical touchscreen, Windows tray interaction, real ScoreSight/camera/video freshness, production OBS, separate-machine LAN/Companion or live-event pass is claimed. Browser touch/zoom automation and actual Linux kernel execution in QEMU are recorded separately from physical/operator tests and the owner's historical public v0.1.2 Linux PASS. See [local test/rehearsal instructions](RELEASE_NOTES-ocr-format.md).

---

# Local v0.1.2-ocr-format.2 verification

Resumed 2026-11-22 on `feature/ocr-automatic-time-format`, based on `2f85c9afae20a137bac2a6d146edb4eab1d6d3eb`. This is an unpublished local review build. No push, commit, tag, release, deletion, reset or cleanup was performed. Existing local work, .1 packages and historical archives remain preserved. The earlier .1 record follows below and is not evidence for changed .2 application bytes.

## Scope and evidence audit

The already implemented changes are the three final-minute OCR output styles (visible zeros, invisible zeros and clean seconds), independent SS/SS.t precision, original upright interface typography, and optional floating previews showing the saved Live layout or unsaved editor draft. Source parsing, exact held duration, ownership, manual-format restoration and connection rules remain as documented in the [local test instructions](RELEASE_NOTES-ocr-format.md).

At resumption, .2 binaries and tests existed but current documentation still described .1. `.test/ocr-format2/resume/start-audit.json` records every publication-source file and all three executable SHA-256 values. `preserved-work.tar.gz` retains the initial source, prior .2 logs/screenshots and existing top-level test screenshots. All application files matched the interrupted Linux run's `source.tar.gz`. Completed browser logs postdate the final .2 build. No application source or executable was changed during resumption; binaries were not rebuilt.

The prior background log failed at a stale 18-selector assertion (there are now 20, including the two OCR choices). The element log measured geometry before the visible canvas's scheduled animation-frame scaling, yielding a null box; that race was reproduced. The offline log was empty. Linux showed ordinary Go tests, but no confirmed vet/race completion or native/package tests. Those results were not treated as passing.

## Reused completed .2 checks

Evidence in this table is under `.test/ocr-format2/`, not the older `.test/ocr-format/`.

| Check | Result and evidence |
| --- | --- |
| Windows Go tests/vet, embedded JavaScript syntax, Windows GUI/console and Linux x64 build | PASS, `build-final.log`; `scripts/build.ps1` exits on failures. Go 1.27.4, amd64, CGO disabled, trimpath. Binary build metadata and embedded assets were independently checked during resumption. |
| Complete simulated OCR and browser suite | PASS, `test_ocr-final.log`: seven targets, validation/ownership/cancellation/restart, period/OT, format/style, drafts/focus, five widths and actual browser zoom; 1,296 geometry combinations each in operator and OBS pages. |
| Clock and display/toolbar suites | PASS, `test_clock_ui-final.log`, `test_display_ui-final.log`: adjustments, pending setup/immediate formats, presets, ownership, five widths, queued writes, draft isolation and restart. |
| Font and team-name suites | PASS, `test_font_ui-final.log`, `test_team_names_ui-final.log`: family/weight, draft/profile persistence, names/validation/caret, OCR availability, responsive controls and shared output. |
| Floating previews | PASS, `test_floating_ui-final.log`: default off, independent browser preferences, read-only saved/draft output, pointer/keyboard move/resize, close/reload, Save/Discard, five widths, emulated touch and actual 200%/400% zoom. |
| Legacy overlay | PASS, `test_legacy_overlay-final.log`: pixel equality against preserved .1 for default layout, font/alignment/dots and legacy background. This is a .1-to-.2 comparison, not a new direct comparison against public v0.1.2. |

## New checks and minimal corrections

New logs are under `.test/ocr-format2/resume/`. Earlier failures remain diagnostic history; none are counted as passes.

| Check | Result and evidence |
| --- | --- |
| Offline UI | PASS, `offline-resume.log`: 375/500/1000/1440/1920 px, mouse/emulated touch/keyboard, native 200%/400% zoom, dynamic choices, drafts, focus, numeric groups and overflow. |
| Background UI | PASS, `background-resume.log`: full suite after correcting the stale selector count; generated PNG/JPG/WebP, Fit/Fill/Original/Stretch, aspect lock, Save/Discard, profiles, legacy, mouse/touch, five widths, zoom and shared geometry. |
| Elements UI | PASS, `elements-resume.log`: full suite after making geometry measurements wait for a visible scaled canvas; all nine elements, text/dot growth, drafts, modes, profiles, restart, five widths and real 200%/400% zoom. No application timing was changed. |
| Focused OCR format/style UI | PASS, `format-style-verified.log`: source thresholds/tenths/holds, all style/precision combinations, 1,296 font/size/alignment/transform combinations each in operator and OBS, focus, drafts, persistence and real browser zoom. |
| Screenshot review | PASS: narrow/desktop floating previews, 1920×1080, 200%/400% zoom and regenerated OCR style captures inspected. Test-only dark screenshot backing makes the white overlay text readable; no runtime style changed. |
| JavaScript | PASS, `javascript.log`: all seven embedded files, including `floating.js`, passed `node --check`. |
| Extracted Windows GUI and console | PASS, `windows-gui-http.log`, `windows-console-http.log`: HTTP/state/clock/auth/SSE/image/layout/profile/restart smoke; no tray-interaction claim. |
| Extracted Windows transport | PASS, `windows-transport.log`: all 1,500 connection-close action requests, no retries. |
| Linux Go/test/vet/race and native tests | PASS, `linux-share/console.log` ends with `LINUX_RESULT_0` and `PACKAGE_RESULT_0`; `run.sh`/`command-completed.sh` use `set -eux`. Alpine kernel 6.12.115, Go 1.24.13, GCC 14.2.0, Python 3.12.16: full Go test/vet/race, simulated native OCR (including all styles), native HTTP/transport, then extracted Linux hash/HTTP/transport. No Linux browser/hardware claim. |
| Final documentation, packaging and security scans | PASS: `docs-final.log`, `package-final.log`, `verify-packages-final.log`, `delivery-final.log` and `final-receipt.json`; exact source allowlist/bytes, native executable identity, embedded assets, ZIP CRC/SHA-256 and portable permissions. Gitleaks 8.30.1 reports zero findings on expanded source/native archives and the isolated final package set (`gitleaks-final-expanded.*`, `gitleaks-final-packages.*`). Personal-path/runtime-data scan also passes. Preflight archives/scans are retained separately. |

Windows browser execution first failed inside the sandbox before application testing (Playwright Node subprocess access denied, `offline.log`). Approved execution outside the sandbox used workspace-local temporary data and isolated listeners/configurations. Screenshot capture initially hit the overlay's CSP and then its intentionally transparent `!important` background; only the test-page backing was changed, using CSSOM with an assertion of the resulting color. Existing CSP and runtime styles remain unchanged.

Candidate native archives are preserved in `resume/candidate/`; extracted tests run their exact executables. Final documentation-only repackaging retains those bytes; final archive hashes are in the versioned `SHA256SUMS.txt` and local receipt. The final four files match the top-level `dist/` copies. Prior manifest and all candidate/preflight archives remain preserved. Test helpers and docs are the only files changed during resumption. No production scoreboard or live ScoreSight endpoint was contacted. No automated verification blocker remains. The owned Linux VM was stopped after its checks; the existing scoreboard instance was left alone.

## Local deliverables and executable identity

The final approval folder is `dist/v0.1.2-ocr-format.2/`, containing Windows, Linux and source ZIPs plus `SHA256SUMS.txt`. Native ZIPs include launchers and documentation; the Windows ZIP contains GUI and console executables. The source ZIP contains the simulator and regression scripts. No developer tools are required to run the native application.

| Executable | SHA-256 retained from the existing .2 build |
| --- | --- |
| Windows GUI `fieldscoreboard.exe` | `a96e6e3a4df93d3ebe13265931a25e4506f5bf4f226f60cc652c8c7971ec5e06` |
| Windows console `fieldscoreboard-console.exe` | `46318ea3086621f38230972572fa7ef81f1d1e2cee1461b45af397ec8c762a8e` |
| Linux `fieldscoreboard` | `97433f7bc80a84928ee840f5631c800629763c65a140e81413c7191ba96b8504` |

## Operator checks still separate

Physical touchscreen, actual Windows tray interaction, real ScoreSight/camera and video freshness, production OBS, separate-machine LAN/Companion and live-event operation remain operator checks. Browser touch emulation and an actual Linux kernel/binary in QEMU do not establish those hardware/venue results. The owner's historical public v0.1.2 Linux PASS is separate from this development build. No publication or remote download check is claimed.

---

# Automatic OCR clock format development verification

Local build **v0.1.2-ocr-format.1**, 2026-11-22. Base commit `2f85c9afae20a137bac2a6d146edb4eab1d6d3eb`; branch `feature/ocr-automatic-time-format`. Initial working tree was clean. Read-only remote inspection confirmed main at the same commit and Latest v0.1.2. Nothing was pushed, tagged, published, deleted or changed in another repository.

## Reproduction and implementation

The preserved v0.1.2 Windows console binary was run with a temporary config, random loopback listener and a simulated HTTP source. After accepting 01:00, source text 55.4 yielded `reading=malformed` and left `main.display=01:00`. No live ScoreSight source was queried.

New code keeps strict legacy parsing when the option is disabled. When enabled, the main target additionally accepts final-minute SS/SS.t; integer arithmetic stores exact tenths in `time.Duration`. Conditional formatting in the Go snapshot selects MM:SS at/above 60 and SS/SS.t below; SS truncates the display fraction. Manual format/configuration and clock direction are unchanged. The same snapshot display feeds preview/OBS. Preference writes preserve held time, ownership, mappings and geometry; input-policy changes invalidate only main's cached/in-flight observation revision. Settings persist in optional `ocr.main_time_format`, with disabled/SS legacy defaults. Restart never restores ownership or connection.

## Changed files

- `internal/scoreboard/ocr_time_format.go` (new), `ocr.go`, `engine.go`, `model.go`, `server.go`: exact observations, validated optional preference/API, persistence, conditional display and distinct local build version.
- `internal/scoreboard/web/ocr.js`, `index.html`, `app.css`: match-only switch/large selector, explanatory text, save/poll synchronization, keyboard focus restoration and local version label. Renderer/overlay geometry and manual controls are unchanged.
- `internal/scoreboard/ocr_time_format_test.go` (new), `scripts/ocr_time_format_checks.py` (new), `test_ocr.py`: strict formats, tenths/boundaries/resets, rejected/missing/lost data, manual takeover, restart, deep-copy/persistence, authentication, per-target revisions, shared output and responsive browser checks.
- `scripts/test_http.py`, `test_display_ui.py`: expected local build version. `test_clock_ui.py`, `ui_period_checks.py`, `ui_touch_checks.py`: test-action synchronization and full Chromium for actual zoom. No manual clock or period application logic was changed for these harness fixes.
- `scripts/simulate_ocr_clock.py` (new): loopback-only simulator for safe Windows rehearsal.
- `README.md`, `CONTRIBUTING.md`, `docs/USER_GUIDE.md`, `docs/OCR_PLAN.md`, `docs/ARCHITECTURE.md`, these local release/verification notes and `handoff.md`: behavior, API, testing and handoff documentation.

## Checks

Verification resumed and completed on 2026-11-22 without resetting or discarding the existing feature work. Logs and screenshots are local under `.test/ocr-format/`; generated tools/builds are ignored by Git. No application code or executable was changed during resumption. Only the OCR test screenshot capture and final documentation were updated.

### Earlier-session evidence checked and reused

| Check | Result and evidence |
| --- | --- |
| Windows Go tests, vet, six embedded JavaScript syntax checks, three-platform build | PASS, `build-final.log`; the unchanged `scripts/build.ps1` stops on any failure. Binaries were built with Go 1.27.4, CGO disabled, amd64, trimmed paths. JavaScript was also rechecked during resumption. |
| Linux `go test ./...`, `go vet ./...`, `CGO_ENABLED=1 go test -race ./...` | PASS, `linux-share/console.log` ends with `LINUX_RESULT_0`; `linux-share/run.sh` uses `set -eu`. Alpine Linux, Go 1.24.13 and GCC 14.2.0. All 26 Go/module files match the saved `source.tar.gz` byte for byte, recorded in `resume-evidence-audit.json`. Later CSS/JavaScript and test/documentation edits do not change this Go timing/ownership evidence. |
| Complete simulated OCR and browser suite | PASS, `ocr-ui-final.log`: seven fields, strict validation, ownership, API guards, cancellation, restart, period/OT, responsive order and shared preview/overlay. Final focus/delayed-write/zoom coverage is supplemented by the new targeted run below. |
| Clock UI | PASS, `clock-ui-fixed.log`: five widths, four adjustments, pending durations, immediate formats, presets, OCR guards and restart. The later application edits were confined to the new OCR format controls. |
| Display and font UI | PASS, `display-ui-final.log`, `font-ui.log`: five widths, drafts, immediate preferences, toolbar order, family/weight, persistence and shared output. |
| Offline UI | PASS, `offline-final.log`: 375/500/1000/1440/1920 px, mouse/emulated touch/keyboard, native 200%/400% zoom, drafts, dynamic choices, numeric controls and overflow. New OCR controls are independently covered by the final native-browser run below. |

Earlier failed logs remain as diagnostic history, not passing evidence. The prior session corrected the control height/focus issues and asynchronous test-action/zoom setup problems before its final passing runs. Historical public v0.1.2 results are not substituted for tests of this feature.

### Checks completed during resumption

| Check | Result and evidence |
| --- | --- |
| Extracted Windows console and GUI HTTP smoke | PASS, `windows-extracted-http-final.log`, `windows-extracted-gui-http-final.log`: startup, independent/combined clocks, game state, SSE, token rotation, images/layout/profiles and restart. This does not test tray interaction. |
| Extracted Windows transport | PASS, `windows-extracted-transport-final.log`: all 1,500 connection-close requests, no retries. |
| Final extracted Linux executable | PASS, `resume-linux/console.log` and `result.json`: executable hash, HTTP smoke, all 1,500 transport requests and full simulated native OCR suite. Actual Linux x64 kernel 6.12.115 in isolated Alpine/QEMU, Python 3.12.16; no Linux browser or physical-hardware claim. |
| Focused automatic-format native/browser checks | PASS, `format-ui-resume.log`: boundaries/tenths/holds/reset/takeover; all five widths; touch/mouse/keyboard; delayed-write focus and polling; layout drafts; preview/overlay; restart; actual 200%/400% Chromium zoom. The existing `.tools/run_format_ui.py` skips unrelated suites already covered above. |
| Screenshot inspection | PASS: 375 px and 1920×1080 captures and actual 200%/400% captures inspected. Old zoom PNGs were blank because document-offset clipping captured outside the scrolled surface; `ocr_time_format_checks.py` now captures the viewport directly via CDP and rejects blank images. Interaction assertions were retained and passed. |
| JavaScript and source whitespace | PASS, all six files via `node --check`, `javascript-resume.log`; `git -c core.whitespace=cr-at-eol diff --check` respects the repository's preserved CRLF bytes. |
| Documentation and packages | PASS, `docs-final.log`, `package-final.log`, `verify-packages-final.log`: internal links/anchors, ZIP CRCs, SHA-256 manifest, source allowlist/bytes, embedded assets, platform formats and executable permissions. Final docs were repackaged with identical tested binaries; no rebuild. |
| Security and local-data review | PASS, Gitleaks 8.30.1 on the exact expanded final source and native packages, and on the isolated final four-file package directory with archive recursion. Redacted reports/logs: `gitleaks-final-expanded.*`, `gitleaks-final-packages.*`. `final-receipt.json` records exact inventories, source/binary comparisons and a separate personal-path/runtime-data scan. No findings or packaged configuration, personal graphics, caches or tools. |
| Versioned local copy | PASS: all four files in `dist/v0.1.2-ocr-format.1/` match the top-level `dist/` bytes and checksums. Pre-resume ZIPs/manifest are retained in `resume-linux/`; older archives remain untouched. |

The first sandboxed Windows smoke attempts failed before application startup because Python temporary directories were inaccessible, including a workspace-local attempt. Those failures are retained in `windows-extracted-http-resume.log` and `windows-extracted-http-workspace-tmp.log`. Approved execution outside the sandbox with workspace temporary data completed the tests. No automated verification blocker remains.

## Deliverables and executable identity

The final folder `dist/v0.1.2-ocr-format.1/` contains:

- `FieldScoreboard-Windows-v0.1.2-ocr-format.1.zip`
- `FieldScoreboard-Linux-v0.1.2-ocr-format.1.zip`
- `FieldScoreboard-Source-v0.1.2-ocr-format.1.zip`
- `SHA256SUMS.txt`

The manifest contains the final ZIP hashes; `final-receipt.json` also records the copied file hashes. ZIPs include this verification report and the [Windows/Linux and ScoreSight test instructions](RELEASE_NOTES-ocr-format.md). The source ZIP includes the simulator and all regression scripts. Native packages require no development tools.

| Executable inside package | SHA-256 |
| --- | --- |
| Windows `fieldscoreboard.exe` | `b73adfd05a813c0a51e00a77e6d53cf91072b2c2d3a06b352a077a765143fcbd` |
| Windows `fieldscoreboard-console.exe` | `0afe4cb6b584f8c46c67b0e7c2a08ec44b2be882060ef71174d9c06a9af390e3` |
| Linux `fieldscoreboard` | `59214e60c2b4325ca664cc240c2a0f7072117451c544bb36c97be652e26f2c40` |

## Verification limits

Source formats were cross-checked in the earlier session against [ScoreSight's documented presets](https://royshil.github.io/scoresight/box-settings.html#format); runtime tests used a simulator. Physical touchscreen, venue ScoreSight/camera and live-video freshness, Windows tray interaction, production OBS and separate-machine LAN/Companion checks remain incomplete and require operator testing. Linux emulation runs the actual Linux binary/kernel; it is separate from the owner's historical v0.1.2 Linux PASS. Reused evidence is limited to this feature's earlier runs as identified above. No live source was contacted, no external documentation link check/public-download check was claimed, and nothing was pushed, tagged or published.
