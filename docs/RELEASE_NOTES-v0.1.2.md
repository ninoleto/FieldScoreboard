# Field Scoreboard v0.1.2

Field Scoreboard is a free, open-source sports scoreboard and graphics editor for **Windows x64 and Linux x64**. Run it locally, control a match in your browser and send a transparent **1920×1080 overlay to OBS Studio** through a Browser Source. No cloud account or additional application runtime is required. ScoreSight is optional and only needed for OCR.

## What you can do

- Operate team names, scores, fouls, periods/OT and independent match and shot clocks with large controls, exact numeric entry and quick time adjustments.
- Use manual control throughout, or independently follow ScoreSight OCR for match time, shot time, home/away scores, home/away fouls and period.
- Import PNG/JPG/WebP artwork; move, resize and style nine scoreboard elements; save named layout profiles with their graphic references and placement.
- Preview the saved layout and use the same geometry in OBS. Layout edits remain drafts until **Save Layout**; **Discard** restores the saved layout.

## New since the public v0.1.0 release

**Clear ScoreSight connection controls.** Separate large Connect and Disconnect buttons and a readable red/amber/green connection-status badge reflect backend state independently of OCR ownership. Disconnect stops polling, cancels pending source I/O and releases all followed fields with their displayed values retained. Owned clocks stay paused; the address and mappings are preserved. Reconnect requires explicit Follow OCR choices and never starts clocks.

**An organised layout editor.** Restore Defaults, Discard and Save Layout sit together at the top. Restore Defaults retains its element-position/size reset scope. Coordinate help sits under X/Y, Free transform stays left and Edit background right. Desktop editor panels have matching top and bottom edges; narrow screens stack naturally. A separate, full-width Layout profiles card contains profile selection, Load/Delete, name and Save preset.

**Visible background sizing buttons.** Four large actions replace the dropdown in a balanced 2×2 grid that stacks on narrow screens:

| Button | Effect |
|---|---|
| Fit entire image | Show the whole image without stretching. |
| Fill canvas | Fill the canvas; edges may be cropped. |
| Original size | Use the image's original pixel dimensions. |
| Stretch to canvas | Fill the canvas without preserving proportions. |

The active preset has the established green selection, border and checkmark. Manual position/size edits show **Custom sizing** and clear preset highlights. Custom is a status. Aspect lock, numeric controls, Center image, Reset to fit, drag/resize and profile restoration retain their behavior. Live preview and OBS continue to use the saved layout until Save Layout.

## Downloads and startup

Download the ZIP for your operating system and extract the **whole archive** into a writable folder. The Source ZIP is for development; ordinary users should choose a platform ZIP.

- [Windows x64 ZIP](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.2/FieldScoreboard-Windows-v0.1.2.zip)
- [Linux x64 ZIP](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.2/FieldScoreboard-Linux-v0.1.2.zip)
- [Source ZIP](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.2/FieldScoreboard-Source-v0.1.2.zip)
- [SHA-256 checksums](https://github.com/ninoleto/FieldScoreboard/releases/download/v0.1.2/SHA256SUMS.txt)

**Windows:** double-click `fieldscoreboard.exe`. It opens the browser and runs in the notification area. Closing the browser leaves it running; use **Exit Field Scoreboard** in the tray menu to stop. Use `start-portable.cmd` to keep data beside the executable. `fieldscoreboard-console.exe` is included for diagnostics.

**Linux:** open a terminal in the extracted application directory and run:

```bash
chmod +x start-portable.sh fieldscoreboard
./start-portable.sh
```

**Sudo is unnecessary.** The terminal stays open while the application runs; press **Ctrl+C** to stop. Linux has no tray. The launcher stores data in the extracted directory. The interface is at **http://127.0.0.1:8790**; open it manually if the browser does not open. Running `./fieldscoreboard` directly uses the user configuration directory instead; `--open=false` disables automatic browser opening.

**OBS:** add a Browser Source with Local file off, URL `http://127.0.0.1:8790/overlay`, width 1920 and height 1080. Keep Field Scoreboard running. Transparent areas remain transparent; editor outlines and checkerboard are not broadcast. See the [user guide](USER_GUIDE.md) for scene setup, LAN access and troubleshooting.

## Upgrade and configuration

Stop the old instance before upgrading. Back up **`config.json`, `profiles/` and `backgrounds/` together**; profile JSON references shared artwork. Extract v0.1.2 into a separate writable directory. For portable use, copy those data files/directories into the new folder before starting its launcher. Direct Windows execution uses `%AppData%\FieldScoreboard`; direct Linux execution uses `$XDG_CONFIG_HOME/FieldScoreboard`, or `~/.config/FieldScoreboard` when unset. Keep the same launch mode or existing `--config` path to keep using the intended data.

Existing configuration and layout profiles remain compatible. The packages contain no personal settings or images, and there is no automatic backup/migration wizard. Restart retains saved settings and game values, returns clocks to Ready and starts OCR disconnected/manual. Runtime clock progress and OCR ownership are not restored. Do not run two instances against the same configuration/port. See [configuration and backups](USER_GUIDE.md#configuration-and-backups).

## OCR limitations and verification

ScoreSight provides recognised values, not verified camera freshness or match running status. Cached successful HTTP responses can continue after video freezes. Missing/rejected readings or connection loss retain the last accepted values; OCR clocks are held rather than extrapolated. Rehearse mappings and monitor the actual source. OCR accuracy depends on the source and is not guaranteed. Automatic sport rules, NDI and direct OBS control are not implemented. See [OCR behavior and limits](OCR_PLAN.md).

On **2026-11-07**, the owner accepted the interface and reported that the **Linux test PASSED**. This is owner-reported evidence; it does not claim additional physical touchscreen, venue OCR or OBS tests. Automated Windows/Linux, OCR/clock/layout, responsive/zoom and package checks are documented in [release verification](VERIFICATION-v0.1.2.md). Final publication updates documentation and ZIP permission metadata while retaining the accepted executable and launcher bytes.

Field Scoreboard is MIT licensed and independent of OBS Studio, ScoreSight and Bitfocus Companion.
