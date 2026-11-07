# Field Scoreboard

**A manual sports scoreboard and graphics editor for OBS Studio.** Control scores, fouls, periods and two independent clocks from a large, touch-friendly web panel. Arrange your artwork and scoreboard fields in one transparent 1920×1080 Browser Source, then nest it over your camera scene.

Free and open source under the [MIT licence](LICENSE). Runs on **Windows x64 and Linux x64**, without a cloud account or extra application runtime. **This branch is v0.1.0-test.17, a local-only ScoreSight development build.** The published first preview remains test.8; the download links below are for that unchanged release. Neither build is a fully field-validated stable release.

The optional **ScoreSight OCR** section is at the **bottom of Live control**, below every manual panel. Connect to discover fields, then follow **match clock, shot clock, home/away scores, home/away fouls and numeric period independently**. Period OCR accepts 3, 3rd or Q3 independently of the chosen display format. Each card shows its source, recognised/accepted value and manual takeover. Missing fields stay unconfigured; bad readings keep the displayed value. Takeover retains the value and pauses clocks. See [setup and limitations](docs/OCR_PLAN.md), [test.17 notes](docs/RELEASE_NOTES-v0.1.0-test.17.md) and [verification](docs/VERIFICATION-v0.1.0-test.17.md). Use the separate local test.17 packages with an isolated configuration; the public downloads below remain test.8.

## Download and start

**[Download for Windows](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0-test.8/FieldScoreboard-Windows-v0.1.0-test.8.zip)** · **[Download for Linux](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0-test.8/FieldScoreboard-Linux-v0.1.0-test.8.zip)**

[Source ZIP](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0-test.8/FieldScoreboard-Source-v0.1.0-test.8.zip) · [SHA-256 checksums](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.0-test.8/SHA256SUMS.txt) · [Release notes](docs/RELEASE_NOTES-v0.1.0-test.8.md)

Extract the whole ZIP into a writable folder before running it.

**Windows:** double-click `fieldscoreboard.exe`. The browser opens and a notification-area icon provides **Open Field Scoreboard**, **Open data folder** and **Exit Field Scoreboard**. Closing the browser leaves the application running; use the tray menu to exit. `fieldscoreboard-console.exe` is included for diagnostics. For portable storage beside the executable, launch `start-portable.cmd` instead.

**Linux:** open a terminal in the extracted folder and run:

```bash
chmod +x fieldscoreboard start-portable.sh
./start-portable.sh
```

Keep that terminal open while using the scoreboard. Stop it with **Ctrl+C**. This launcher uses portable storage in the extracted folder. Linux has no tray; `./fieldscoreboard` uses your user configuration folder instead. Add `--open=false` for headless use.

The control panel is **http://127.0.0.1:8790** on the computer running Field Scoreboard. See [storage, backups and troubleshooting](docs/USER_GUIDE.md#configuration-and-backups).

## Put it in OBS

1. Create a **Scoreboard** scene. Add a **Browser Source**, turn **Local file** off, and set URL to `http://127.0.0.1:8790/overlay`, width **1920**, height **1080**.
2. In Field Scoreboard, open **Layout editor**, import your graphic, position the fields and choose **Save layout**. The checkerboard is editor-only; PNG transparency and uncovered areas stay transparent in OBS.
3. Add the Scoreboard scene as a **Scene Source** in your camera/production scene. Scale and position the nested scene as needed. Keep the Browser Source itself at 1920×1080. Leave **Shutdown source when not visible** and **Refresh browser when scene becomes active** off.

If **Browser Source is missing on Linux**, check which OBS installation you launched. The official Flatpak includes the browser component; if installed, launch it explicitly with `flatpak run com.obsproject.Studio`. See [OBS setup and Linux troubleshooting](docs/USER_GUIDE.md#obs-setup), [OBS Browser Source documentation](https://obsproject.com/kb/browser-source) and [official Linux installation guidance](https://obsproject.com/kb/linux-installation).

## What you can control

- Large home/away name inputs with polling-safe typing; scores and fouls; numeric or dot foul displays; periods displayed as **Number (3)**, **Ordinal (3rd)** or **Quarter (Q3)**, and an **OT** override that preserves the period number and chosen format. Changes apply immediately.
- Independent match and shot clocks, count-up/down match timing, duration entry and time corrections. **Start both / Pause both** keeps their current times. Resetting or setting the shot clock (including 14/24/30 presets) starts it only if the match clock is running, without changing the match clock.
- Optional **shot auto-hide** hides its output when shot time is at least the remaining match time, or the match has expired. Timing continues internally. After application restart, saved game values remain but both clocks return to Ready.
- Large choice dialogs and consistent numeric ± controls at every screen size. Duration drafts wait for **Set** and survive background updates; narrow screens use **Menu** navigation.
- Both clock cards put **−5s / −1s / +1s / +5s** directly below transport controls. The shot card then offers immediate **14s/24s/30s Duration presets** with its resume explanation, followed by Clock setup. Both cards end with a full-width blue Set button. Output format in each card applies immediately; duration/direction wait for Set. Match **Duration presets (5/8/10/12/20 min)** fill pending setup only; press Set match clock to apply.
- **Scoreboard display** in Live control applies foul styles and maximum dots immediately to preview/OBS, independently of layout Save/Discard. On narrow screens it follows the primary controls; OCR stays last.
- Nine movable/stylable fields with a clear selected-element label, optional **Free transform** resize handles, aspect lock and precise width/height ± controls. Resizing transforms the text or foul dots; extra digits and longer names grow naturally. PNG/JPG/WebP backgrounds are supported. New images **Fit entire image** without distortion; Fill, Original size, Stretch and Custom placement are available. Aspect lock, dimensions and position controls preserve original proportions when locked.
- Use **Edit background — move & resize** beside the preview to drag the image or resize its corner handles; **Finish editing background** exits that mode. **Save layout / Discard** controls when edits reach OBS. Layout presets include graphics and positioning without replacing live scores or clocks.
- The touch-friendly **Font** picker includes a pinned **Bold** switch; changing family or weight preserves the other. The closed control shows both, and changes wait for Save layout.
- Fine-position arrows move **5/10/20 px**, default **5 px**. X/Y ± buttons remain **1 px**. Saved coordinates always use the logical 1920×1080 canvas.

[The user guide](docs/USER_GUIDE.md) explains operation, image sizing, presets, limits and recovery.

## LAN and Companion

In **Output & API**, enable LAN access, save and restart. Use the selected real adapter address, never `0.0.0.0`, on other computers. The LAN OBS URL is read-only and needs no token on a trusted private network. Remote control requires an **Authorization: Bearer** header; copy or regenerate the token locally under OBS Browser Source. HTTP is unencrypted: use a trusted network and do not expose the port to the internet.

The built-in **Companion HTTP Builder** generates requests for Bitfocus Companion's Generic HTTP Requests connection. There is no dedicated Companion module or live button feedback. See [Companion setup](docs/COMPANION_SETUP.md) and [LAN and authentication](docs/USER_GUIDE.md#lan-and-authentication).

## Preview status and development

**User-reported manual smoke test, 2026-11-06, for test.8:** the Linux application and its overlay work with OBS Flatpak. This does not validate the OCR build or establish physical touchscreen, Windows tray, LAN, Companion or live-event validation. See [test.8 verification](docs/VERIFICATION-v0.1.0-test.8.md) and the separate [test.17 results](docs/VERIFICATION-v0.1.0-test.17.md).

**User-reported home smoke test, 2026-11-06:** match-clock OCR works in the operator’s home setup with test.9. This is not venue validation. Local test.17 includes seven independent OCR mappings and optional element Free transform. Normal selection/dragging shows only a thin outline; **Free transform** reveals handles and **Done transforming** hides them without saving or discarding edits. Automatic sport rules, NDI and direct OBS control are **not included**. See [current scope and future work](docs/OCR_PLAN.md).

After user acceptance, the intended public version is **v0.1.0**, a normal release. Test.17 remains local and is not published.

To contribute, read [CONTRIBUTING.md](CONTRIBUTING.md), the [architecture guide](docs/ARCHITECTURE.md), [AGENTS.md](AGENTS.md) and the current [handoff](handoff.md). Field Scoreboard is separate from Field Timer and is not affiliated with OBS Studio or Bitfocus Companion.
