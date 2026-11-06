# v0.1.0-test.8 — First public preview

Field Scoreboard is a free, MIT-licensed manual sports scoreboard and layout editor for OBS Studio on Windows x64 and Linux x64. This is a **prerelease**, retaining the completed test.8 application and tested executable bytes.

## Included

- One transparent 1920×1080 OBS Browser Source with nine configurable fields and your PNG/JPG/WebP artwork; nest the scoreboard scene over a camera scene.
- Home/away names, scores and fouls; numeric/dot foul display; periods and OT.
- Independent match and shot clocks, count-up/down match timing, corrections and combined Start/Pause. Shot Reset/Set/presets resume only while the match clock is running. Optional shot auto-hide changes output visibility only.
- Large choice dialogs and consistent numeric controls at every width; small-screen Menu navigation, keyboard access and polling-safe drafts.
- Fit/Fill/Original/Stretch/Custom background sizing, aspect lock, logical position/dimensions, explicit background editing, dragging/resizing, Save/Discard and layout presets. Legacy layouts retain their appearance.
- Fine-position steps **5/10/20 px**, default **5 px**; arrows use the chosen step with boundary clamps. X/Y ± stays **1 px**. Canvas keyboard movement remains 1 px / Shift+10 px.
- Local-first operation, optional trusted-LAN read-only OBS output, authenticated remote controls and a Companion HTTP Builder.
- Windows tray/portable launcher and Linux terminal/portable launcher; all guides included in the packages.

Public-release preparation updates documentation and packaging only. No application behavior, embedded UI assets, clock logic, APIs or tested executable bytes changed. No sliders were added.

## Downloads and start

Download the Windows, Linux or source ZIP from the [release](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8). Download the separate `SHA256SUMS.txt` to verify the three ZIPs.

Windows: extract and run `fieldscoreboard.exe`, or `start-portable.cmd` for portable data. Linux: extract, run `chmod +x fieldscoreboard start-portable.sh`, then `./start-portable.sh`; keep the terminal open and stop with Ctrl+C. Control panel: `http://127.0.0.1:8790`. OBS URL: `http://127.0.0.1:8790/overlay`, viewport 1920×1080. See [quick start](../README.md) and the [user guide](USER_GUIDE.md).

## Verification and limits

The [verification record](VERIFICATION-v0.1.0-test.8.md) separates reused application tests from publication checks. Completed test.8 evidence includes Go tests/vet/Linux race checks, JavaScript syntax, responsive/touch-emulated/keyboard/zoom browser checks, image regressions and native Windows/Linux HTTP smoke/restart.

**User-reported manual smoke test, 2026-11-06:** the Linux application and its overlay work with OBS Flatpak. If Linux OBS lacks Browser Source, check the installed package and explicitly launch the installed Flatpak using `flatpak run com.obsproject.Studio`.

Physical touchscreen, Windows tray, Windows OBS, separate-machine LAN/firewall, Companion hardware and live-event validation remain pending. The Linux smoke report does not cover those tests.

Known limits: preview quality; x64 packages only; Linux has no tray; OBS browser support depends on installation. Restart resets clocks to Ready while keeping saved game/layout settings. LAN listener changes require restart; HTTP is unencrypted and intended for trusted networks, with bearer authentication for remote control. No automatic backups, live Companion feedback module, OCR, NDI, direct OBS control or automatic sport rules. No Field Timer changes.
