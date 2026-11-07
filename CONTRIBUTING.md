# Contributing to Field Scoreboard

Read [AGENTS.md](AGENTS.md), the current [handoff](handoff.md) and [architecture](docs/ARCHITECTURE.md) before changing behavior. Field Scoreboard is independent of Field Timer. Contributions are under the [MIT licence](LICENSE).

## Prerequisites

- Git and Go **1.23 or newer**. The application uses only Go's standard library and embedded browser assets; there is no npm install/build step.
- Node.js for JavaScript syntax checks; Python **3.10+** for tests and packaging.
- For browser tests: Python packages `playwright` and `Pillow`, plus Chromium/Chrome. These are development dependencies only.
- Linux race tests need CGO enabled and a working C compiler (for example GCC and the distribution's libc development package). Released application binaries use `CGO_ENABLED=0`.
- PowerShell for Windows builds; Bash for Linux builds.

Clone `https://github.com/ninoleto/FieldScoreboard.git` and run commands below from the checkout root. An optional virtual environment keeps Python dependencies local:

```text
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in Bash, then:

```text
python -m pip install playwright Pillow
python -m playwright install chromium
```

Alternatively set `CHROMIUM_PATH` to an existing Chrome/Chromium executable. Zoom tests may use a headed browser; on headless Linux use a virtual display, such as `xvfb-run -a python scripts/test_ui_offline.py`. Install Playwright's Linux browser dependencies as needed (see `python -m playwright install --help`).

## Run and build

Use a separate development configuration so testing does not affect a production game:

```text
go run ./cmd/fieldscoreboard --config .test/dev/config.json --open=false
```

Open `http://127.0.0.1:8790`. Add `--listen 127.0.0.1:8791` if another instance uses the default port. This overrides the listener for the run, without saving a network setting. HTML/CSS/JS is embedded at compile time, so restart/rebuild after editing assets. Windows runs a tray; Linux stays in the terminal.

**Windows PowerShell:**

```powershell
.\scripts\build.ps1
python scripts/test_ui_offline.py
python scripts/test_background_ui.py bin/fieldscoreboard-windows-console.exe
python scripts/test_elements_ui.py bin/fieldscoreboard-windows-console.exe
python scripts/test_display_ui.py bin/fieldscoreboard-windows-console.exe
python scripts/test_clock_ui.py bin/fieldscoreboard-windows-console.exe
python scripts/test_font_ui.py bin/fieldscoreboard-windows-console.exe
python scripts/test_http_transport.py bin/fieldscoreboard-windows-console.exe
python scripts/test_http.py bin/fieldscoreboard-windows-console.exe
python scripts/test_ocr.py bin/fieldscoreboard-windows-console.exe --ui
```

**Linux Bash:**

```bash
bash scripts/build.sh
python scripts/test_ui_offline.py
python scripts/test_background_ui.py bin/fieldscoreboard-linux
python scripts/test_elements_ui.py bin/fieldscoreboard-linux
python scripts/test_display_ui.py bin/fieldscoreboard-linux
python scripts/test_clock_ui.py bin/fieldscoreboard-linux
python scripts/test_font_ui.py bin/fieldscoreboard-linux
python scripts/test_http_transport.py bin/fieldscoreboard-linux
python scripts/test_http.py bin/fieldscoreboard-linux
python scripts/test_ocr.py bin/fieldscoreboard-linux --ui
```

The build scripts run Go tests/vet and cross-compile Windows GUI, Windows console and Linux amd64 into `bin/`. The Linux script also runs the race detector. Windows requires Node; the Bash script checks JavaScript when Node is present, so ensure Node is installed for release verification. Windows alone does not satisfy Linux race/native smoke requirements.

Individual checks:

```text
go test ./...
go vet ./...
```

On Linux, run `CGO_ENABLED=1 go test -race ./...`. Check each `internal/scoreboard/web/*.js` with `node --check` (PowerShell: `Get-ChildItem internal/scoreboard/web/*.js | ForEach-Object { node --check $_.FullName }`; Bash: `for js in internal/scoreboard/web/*.js; do node --check "$js"; done`).

The offline UI suite serves mocked API state, not OBS. The background and HTTP suites start isolated native processes with temporary configurations and generated artwork. Screenshots go under `.test/`. Inspect responsive screenshots, including 375 px and a maximized 1920×1080 viewport. Touch emulation is not physical touchscreen validation.

The element suite checks all nine move/resize workflows, default normal-mode selection/dragging, explicit Free transform and exit transitions, draft preservation and shared editor/preview/overlay geometry. For a direct legacy compatibility comparison, run `python scripts/test_legacy_overlay.py <previous-native-binary> <current-native-binary>`; it compares generated legacy OBS screenshots using isolated processes. The HTTP transport suite sends 1,500 action requests without retries and fails on truncated/reset responses.

The clock suite checks card order, matching quick targets, all four immediate adjustments, transport preservation, one-unit setup drafts, immediate formats, Set actions, presets, auto-hide, OCR guards, footer and restart at all five widths. Its `ui_duration_presets.py` helper verifies all five pending match presets without live writes while paused/running, custom highlights, direction/format preservation and Set. The OCR fixture confirms setup cannot bypass ownership. Go `clock_quick_test.go` covers both clocks, count-up/down, exact upper/zero boundaries and unchanged unrelated state.

The font suite checks the pinned Bold switch, family/weight independence, font-list scrolling, touch/keyboard/focus, hidden-row tab stops in other dialogs, element switching, Save/Discard, profiles, restart and transformed editor/preview/overlay rendering at all five widths.

The display suite checks all five responsive widths, editor toolbar modes and inspector keyboard order, immediate preview/overlay appearance, unfinished inputs, queued/delayed writes, stale layout saves, Discard, position reset, presets and restart. Go display tests cover authentication, strict validation, running clocks and seven-field ownership isolation. OCR browser checks include real simulated connection transitions and duplicate-request prevention.

The OCR suite also runs `period_checks.py` and, with `--ui`, `ui_period_checks.py`: strict number/ordinal/Q recognition, independent formats, OT, API compatibility, presets, restart, touch radio choices and transformed editor/preview/overlay geometry. The OCR suite simulates seven fields, simultaneous/mixed ownership, API guards, atomic combined rejection, delayed takeover, pauses/resets, per-field rejection, loss/recovery and restart. Browser checks cover bottom ordering, all seven selectors, drafts and polling focus/scroll; omit `--ui` for a native HTTP-only run. For a running real ScoreSight with a configured Time field, use `python scripts/test_ocr.py <native-binary> --live-address http://127.0.0.1:18099`. It starts an isolated scoreboard, reads the source without modifying it and records live observations separately. Do not combine `--ui` with the live option: browser field fixtures belong to the simulator.

## Contribution workflow

1. Inspect `git status` and preserve existing edits. Use a focused branch and describe the concrete issue or intended behavior.
2. Keep timing/state in Go and rendering in the shared frontend renderer. Preserve public APIs, optional configuration fields and the behavior listed in AGENTS.md.
3. Add meaningful regression coverage for changed behavior, run relevant checks, and update existing guides rather than creating contradictory copies.
4. Submit a pull request with the problem, resulting behavior, validation and remaining limitations. For UI changes, include narrow/desktop screenshots using generated or shareable artwork only.

Never commit real tokens, runtime configuration, private artwork, local absolute paths, logs or screenshots of credentials. Report security-sensitive issues privately to the maintainer through GitHub's private reporting facilities when available; do not post credentials in public issues.

## Packaging and release

For a new application version, update `internal/scoreboard/model.go`, the UI version label, package/test version references and matching release/verification documents together. Use the next unused local test version during development. After operator acceptance of this work, the intended public version is v0.1.0 as a normal release, not another public preview; publication still requires authorization. A documentation-only publication of an already-tested version can retain its version and exact executable bytes; record reused evidence explicitly.

After building, from the source root:

```text
python scripts/check_docs.py
python scripts/package.py
python scripts/verify_packages.py
```

`dist/` contains Windows, Linux and source ZIPs plus `SHA256SUMS.txt`. Native packages include launchers, licence and the complete documentation set. Source packaging uses an explicit project-file allowlist; inspect it when adding a new top-level source directory. Runtime configuration, uploaded graphics, caches, temporary environments and generated executables must stay out of the source archive and Git.

Extract platform ZIPs and run `scripts/test_http.py` with the extracted Windows console binary and Linux binary on their respective OSes. Verify archive executables match those tested. Run Gitleaks (for example `gitleaks dir <staged-source> --redact --max-archive-depth 2`) on the exact staged source and release directory, plus a review for personal paths/data. `verify_packages.py` checks CRCs, hashes, embedded assets, platform formats, source contents and basic hygiene; it does not replace the secret scan.

Publication requires the owner's authorization. Inspect repository/history, commit actual source and scripts, tag the verified commit, and attach all three ZIPs and the checksum file. Use a prerelease for explicitly approved preview versions; the planned accepted v0.1.0 is a normal release. After publishing, check unauthenticated repository/release access, download every asset and compare SHA-256 with local files. Record results without claiming pending physical tests passed.
