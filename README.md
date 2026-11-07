# Field Scoreboard

**A sports scoreboard and graphics editor for OBS Studio, for Windows and Linux.** Control scores, fouls, periods and two independent clocks from a large, touch-friendly web panel. Use manual controls or optionally follow recognised values from ScoreSight. Arrange artwork and scoreboard fields in one transparent 1920×1080 Browser Source.

**v0.1.1 review build — awaiting visual acceptance.** The current public release remains v0.1.0; the download links below refer to that release until v0.1.1 is approved. Free and open source under the [MIT licence](LICENSE). Windows x64 and Linux x64 packages run without a cloud account or additional application runtime. ScoreSight is needed only for optional OCR. [v0.1.1 changes](docs/RELEASE_NOTES-v0.1.1.md) · [Verification and limitations](docs/VERIFICATION-v0.1.1.md).

## Download and start

**[Download for Windows](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0/FieldScoreboard-Windows-v0.1.0.zip)** · **[Download for Linux](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0/FieldScoreboard-Linux-v0.1.0.zip)**

[Source ZIP](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0/FieldScoreboard-Source-v0.1.0.zip) · [SHA-256 checksums](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0/SHA256SUMS.txt) · [GitHub release](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0)

Extract the whole ZIP into a writable folder before running it.

**Windows:** double-click `fieldscoreboard.exe`. It opens the browser and a notification-area icon with **Open Field Scoreboard**, **Open data folder** and **Exit Field Scoreboard**. Closing the browser leaves the app running; use the tray menu to exit. For portable storage beside the executable, use `start-portable.cmd`. `fieldscoreboard-console.exe` is included for diagnostics.

**Linux:** open a terminal in the extracted folder:

```bash
chmod +x fieldscoreboard start-portable.sh
./start-portable.sh
```

Keep the terminal open; stop the application with **Ctrl+C**. The launcher uses portable storage in the extracted folder. Linux has no tray. Running `./fieldscoreboard` directly uses the user configuration folder; add `--open=false` for headless use.

Open the control panel at **http://127.0.0.1:8790** on the host computer. Existing settings remain compatible; keep the same launch mode when upgrading. See [configuration locations and backups](docs/USER_GUIDE.md#configuration-and-backups).

## Put it in OBS

1. Create a **Scoreboard** scene and add a **Browser Source**. Turn **Local file** off. Use `http://127.0.0.1:8790/overlay`, width **1920**, height **1080**.
2. Import your graphic in **Layout editor**, arrange the fields and choose **Save layout**. PNG alpha and uncovered areas remain transparent in OBS; the checkerboard is editor-only.
3. Add the Scoreboard scene as a **Scene Source** over your camera scene. Scale/position the nested scene while keeping the Browser Source at 1920×1080. Leave **Shutdown source when not visible** and **Refresh browser when scene becomes active** off.

**Browser Source missing on Linux?** Check which OBS installation you launched. If the official Flatpak is installed, launch it explicitly with `flatpak run com.obsproject.Studio`. See [OBS setup and troubleshooting](docs/USER_GUIDE.md#obs-setup), [OBS Browser Source documentation](https://obsproject.com/kb/browser-source) and [official Linux installation guidance](https://obsproject.com/kb/linux-installation).

## Operate the scoreboard

- Large team-name fields, scores, fouls and periods; exact numeric entry and consistent ± controls. **Period format** selects Number, Ordinal or Quarter. **OT** overrides the label while retaining the numeric period and chosen format.
- Independent match and shot clocks, **Start both / Pause both**, and immediate **−5s / −1s / +1s / +5s** corrections. Match **5/8/10/12/20-minute presets** fill pending setup; press **Set match clock** to apply. Shot **14s/24s/30s presets apply immediately**. Shot Reset/Set/presets resume only if the match clock is internally running, without changing it. Output formats apply immediately, independently of Set.
- Optional **shot auto-hide** hides output when shot time is at least remaining match time or the match has expired. Timing is unaffected. **Foul indicators** applies numeric/dot styles and dot maximum immediately. Restart retains saved game/configuration but returns clocks to Ready.
- Touch-friendly dialogs at every screen size, large buttons, polling-safe drafts and narrow-screen **Menu** navigation.
- Nine editable scoreboard elements: position, font, **Bold inside Font**, color, alignment and visibility. Normal mode supports selection/dragging; optional **Free transform** reveals resize handles. Background graphics support Fit, Fill, Original size, Stretch and Custom, with aspect lock and precise controls. Use **Edit background — move & resize** to manipulate the image. The top actions are **Restore Defaults / Discard / Save Layout**; Restore Defaults keeps its element-position/size reset scope. A separate full-width **Layout profiles** card sits below the aligned editor columns; presets preserve live game values.
- Fine-position arrows use **5/10/20 px**, default **5 px**. X/Y ± remains **1 px**. Saved geometry uses logical 1920×1080 coordinates.

[The user guide](docs/USER_GUIDE.md) covers operation, editing, recovery and limits.

## ScoreSight, LAN and Companion

**ScoreSight OCR** is at the bottom of Live control. Connect to discover fields, then follow match time, shot time, home/away scores, home/away fouls and period independently. Missing fields remain manual. Period OCR accepts 3, 3rd or Q3 independently of display format. Rejected/missing readings hold the last value; **Take manual control** retains that value and pauses a clock. Separate **Connect** and **Disconnect** buttons use a shared status badge. Disconnect stops polling, returns all followed fields to manual with values retained, and leaves followed clocks paused. Reconnect requires explicit Follow OCR again. Restart starts manual and disconnected. **Successful HTTP readings do not prove fresh camera video.** See [OCR setup, validation and freshness limitations](docs/OCR_PLAN.md).

In **Output & API**, enable LAN access, save and restart. Use the selected real adapter address on other machines. Remote control needs an **Authorization: Bearer** header; copy or rotate the token locally. The read-only LAN OBS URL needs no token on permitted private clients. HTTP is unencrypted; use a trusted network. The **Companion HTTP Builder** generates requests for Generic HTTP Requests, without a dedicated Companion module or live feedback. See [LAN/authentication](docs/USER_GUIDE.md#lan-and-authentication) and [Companion setup](docs/COMPANION_SETUP.md).

## Verification and development

The operator accepted the application for v0.1.0 release. Automated checks are documented separately from manual evidence: on **2026-11-06**, the operator reported Linux/OBS Flatpak working with test.8 and match-clock OCR working at home with test.9. These reports do not establish venue, physical touchscreen, tray, LAN or Companion validation. The v0.1.1 visual review is pending. See [review-build verification](docs/VERIFICATION-v0.1.1.md).

Automatic sport rules, NDI, direct OBS control and verified video freshness are **not implemented**. Contributions start with [CONTRIBUTING.md](CONTRIBUTING.md), [architecture](docs/ARCHITECTURE.md), [AGENTS.md](AGENTS.md) and [handoff](handoff.md). Field Scoreboard is separate from Field Timer and is not affiliated with OBS Studio, ScoreSight or Bitfocus Companion.
