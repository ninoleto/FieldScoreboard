# Field Scoreboard user guide

[Download and quick start](../README.md) · [Companion setup](COMPANION_SETUP.md) · [Preview verification](VERIFICATION-v0.1.0-test.8.md)

## Starting and stopping

Extract the complete Windows or Linux ZIP into a writable folder. Windows x64 has a GUI executable (`fieldscoreboard.exe`) and a diagnostic console executable (`fieldscoreboard-console.exe`); both use the native tray. Double-click the tray icon to reopen the control panel. Right-click for Open Field Scoreboard, Open data folder or Exit Field Scoreboard. Closing a browser tab does not stop the server or clocks.

For Windows portable storage, use `start-portable.cmd`. For Linux portable storage, open a terminal in the extracted folder:

```bash
chmod +x fieldscoreboard start-portable.sh
./start-portable.sh
```

Keep the terminal open and press Ctrl+C to stop. Linux has no tray. Running `./fieldscoreboard` directly uses the user configuration directory instead. Both platforms open the browser automatically unless launched with `--open=false`. Open **http://127.0.0.1:8790** manually if needed.

Do not start two instances using the same configuration or listening port. A port-in-use error usually means an instance is already running. Windows startup errors appear in a dialog; its log is `fieldscoreboard.log` next to the active configuration. Linux logs to the terminal. For a custom location, use `--config /path/to/config.json` (quote paths containing spaces).

## Operating a match

Local test.12 places **ScoreSight OCR at the bottom of Live control**, after all manual panels. Connect once, then select a discovered source and **Follow OCR** independently for match time, shot time, home/away scores, home/away fouls or numeric period. Missing fields remain unconfigured/manual. **Take manual control** retains that field’s displayed value; clocks stay paused until Start / Resume. Rejected/missing readings and connection failures keep values. Both-clock actions require both clocks manual, and game reset requires scores, fouls and period manual. Manual shot reset stays Ready while match time follows OCR because source running status is unknown. Mappings persist; restart is manual/Ready and disconnected. See [setup, validation and freshness limits](OCR_PLAN.md). Fouls accept 0–30; numeric periods accept 1–20. Numeric OCR changes the saved period number without toggling OT. The OT switch remains manual; turning it off reveals the latest accepted period. The manual behavior below applies to fields not following OCR.

**Live control** contains immediate score, foul, name and period updates. Scores allow 0–999, fouls 0–30 and periods 1–20. Tap a score/foul/period value, or focus it and press Enter/Space, for exact entry. OT changes only the displayed period label; turning it off restores the numeric period. Reset game clears scores, fouls and OT and returns the period to 1; use clock controls separately to reset timing.

The match clock counts down or up; the shot clock counts down. They are independent. Each has Start, Pause, Stop, Reset and time corrections. **Both clocks → Start both / Pause both** starts or pauses them together without changing their current times.

Minutes and Seconds are separate editable groups. Zero minutes is valid when the total is at least one second. Seconds ± carries/borrows across minutes. Edits stay pending until **Set match clock**; the shot duration likewise waits for Set. Polling and navigation preserve unfinished entries. Correct invalid values before applying them.

**Shot reset behavior:** Reset shot clock, Set shot clock and the 14/24/30-second presets restore the shot duration and resume it only when the match clock is currently running. Otherwise it stays Ready. They do not start, pause or reset the match clock. Independent shot Start/Pause/Stop still works.

**Auto-hide** affects only shot-clock output: it hides when shot remaining time is greater than or equal to remaining match time, or the match has expired. For count-up, remaining match time is configured duration minus elapsed time. The shot clock continues internally, and the operator still sees its value. The layout editor keeps the shot field visible for positioning. Auto-hide defaults to off.

Restarting retains scores, fouls, names, period/OT, durations, direction, auto-hide and saved layout. It resets both runtime clocks to Ready; it never resumes play automatically. Sport-specific rules and automatic period advancement are not implemented.

## Touch, mouse and keyboard

Large controls are the default even on a desktop with a mouse. Numeric ± groups use large labelled fields and visible gaps; narrow layouts stack groups. Every dropdown opens a centered choice dialog: scroll the options, select by touch/mouse, or use arrows, Home/End, typing a prefix and Enter/Space. Escape, Close or an outside tap dismisses it and restores focus. Small screens show a Menu button with the current page name; switching pages preserves drafts.

## Layouts and background graphics

The editor always stores **1920×1080 logical coordinates**. Browser size and zoom change only preview scale. Select a scoreboard field using the field controls or drag it in the preview. Configure position, font, size, color, weight, alignment and visibility. Fouls can use numbers or colored dots separately per team; counts beyond the selected dot maximum show an extra-count indicator.

**Move and resize any element:** select its field button or the rendered field. The “Editing:” label identifies the current selection. Normal mode opens by default: drag the field to move it, with only a thin selection outline. Choose **Free transform** beside the preview to reveal the 56 px resize handles. The active button reads **Done transforming**; choose it to hide the handles while retaining draft changes. Drag corner handles to resize proportionally. **Lock aspect ratio** is on by default. Turn it off for independent width/height resizing with the four side handles, or use the large Width/Height ± fields. On small previews, the dotted handle guide expands so handles remain distinct; the solid border shows the actual content bounds. Handles support arrow keys (1 logical pixel; Shift 10). Hidden fields can be made visible using the existing visibility control.

Width/height describe the current rendered value. Saved horizontal/vertical scales (5%–2000%) remain constant when a score changes from 9 to 10, a longer team name arrives, or foul dots change. Content can grow without a fixed clipping box; the canvas edge still clips output. Alignment keeps the left/center/right anchor at X. Font, color, bold and font size remain independently editable. **Reset element size** removes the extra scaling while retaining font settings and position. Legacy layouts have no extra scale and keep their previous OBS output until edited.

Selecting a field and editing the background are mutually exclusive. Free transform exits when selecting another field, entering background editing, leaving Layout editor or reloading the page. It is never stored in layouts or presets. Numeric position, size, font and aspect controls remain available in normal mode; existing transforms always render. Mode switches never save, discard or reset edits. Borders, dotted guides and handles appear only in the editor. Changes stay pending until **Save layout**; **Discard**, presets and restart preserve the chosen transform. Unfinished numeric drafts survive polling/navigation and invalid dimensions block Save. No sliders are used.

**Fine position** uses 5/10/20 px with 5 px selected by default. All four arrow-pad buttons use that step and clamp field anchors to X 0–1920 and Y 0–1080. X/Y ± stays at 1 px. Keyboard arrows on a selected field move 1 px, or 10 px with Shift; they are independent of the step selector. Anchors at the canvas edge may place part of a field outside the visible canvas.

Import PNG, JPG or WebP up to 15 MB and 8192 pixels per side. Original file bytes are kept unchanged. New imports default to centered **Fit entire image**, with **Lock aspect ratio** enabled.

| Sizing | Result |
|---|---|
| Fit entire image | Preserve proportions, show the complete image and center it. |
| Fill canvas | Preserve proportions, cover the canvas and crop overflow. |
| Original size | One image pixel per logical canvas pixel, centered. |
| Stretch to canvas | Explicitly stretch to 1920×1080, allowing distortion. |
| Custom | Shown after manually changing dimensions or position. |

In **Background graphic**, edit Width, Height, X and Y using exact values or large ± buttons. With aspect lock enabled, changing either dimension updates the other from the original proportions. Unlock it for independent dimensions. X/Y is the top-left position; negative positions crop the image. **Center image** keeps its size; **Reset to fit** restores fit, centering and aspect lock. Original dimensions appear for reference.

Use **Edit background — move & resize** beside the preview before dragging the graphic or resizing its generous corner handles. The active button reads **Finish editing background**. This explicit selection prevents moving a score or clock while editing the background. Keyboard arrows move the selected image (Shift for larger increments); focused corner handles support keyboard resizing. Escape or Finish editing background leaves this mode. The graphic always stays behind the scoreboard; selection borders and handles appear only in the editor. No sliders are used.

**Save layout** applies pending changes, including import/removal, to the saved preview and OBS. **Discard** restores the saved layout and graphic. Incomplete numeric drafts survive polling and page navigation and must be corrected before saving. Named layout presets include the graphic reference, placement, original dimensions and aspect lock. Loading a preset changes the layout immediately after any unsaved-change confirmation, without replacing game values or clocks. Saving a preset first saves pending layout edits.

Older layouts without background-transform metadata keep their previous stretched appearance until the background is explicitly edited. Opening, resizing or saving the editor alone does not migrate them. Unused draft uploads may remain in the data folder; there is no automatic cleanup that could delete a preset's artwork.

## OBS setup

1. Start Field Scoreboard and create a Scoreboard scene in OBS.
2. Add a Browser Source with Local file off, URL `http://127.0.0.1:8790/overlay`, width 1920 and height 1080. On another computer, use the LAN URL described below.
3. Save your layout in Field Scoreboard. PNG alpha and uncovered canvas areas remain transparent; the editor checkerboard, borders and handles are never output. JPG has no alpha, though areas outside its placed rectangle remain transparent.
4. Add the Scoreboard scene as a Scene Source in your camera scene, then scale/position that nested scene. Keep the browser viewport at 1920×1080 even if the production canvas differs.
5. Leave Shutdown source when not visible and Refresh browser when scene becomes active off. The server owns clock timing independently of scene visibility. If disconnected, the overlay retries and hides stale graphics after about six seconds without updates.

OBS describes Browser Source properties in its [official guide](https://obsproject.com/kb/browser-source).

### Linux: Browser Source missing

The [official OBS browser component](https://github.com/obsproject/obs-browser) is included in official Flatpak builds; other distribution packages may differ. If the Flatpak is already installed, close the unintended OBS instance and launch this one explicitly:

```bash
flatpak run com.obsproject.Studio
```

A desktop shortcut may open a different installed OBS package. Check the launched installation before changing packages or plugins; see [official Linux installation guidance](https://obsproject.com/kb/linux-installation). Recreate the Browser Source in the intended OBS instance and check the URL in a normal browser if the source is blank.

**User-reported manual smoke test (2026-11-06):** the Linux application and overlay work with OBS Flatpak. This report does not establish tests of touchscreen hardware, Windows tray, LAN, Companion or a live event.

## LAN and authentication

Local control uses `127.0.0.1:8790` and needs no token. In **Output & API → Output & network**, enable LAN access, select the private IPv4 adapter and port, save, then exit and restart. Changes do not rebind an active match. The adapter may use DHCP or a static address; selecting it chooses the displayed destination, while LAN mode listens on all IPv4 interfaces (`0.0.0.0`). No firewall rules are installed automatically.

Use the copied address reachable from the other device, such as `http://192.168.1.25:8790`; `127.0.0.1` means that device itself and `0.0.0.0` is not a destination. Allow the selected TCP port on your trusted private firewall profile if needed. If DHCP changes the address, refresh the adapter selection and update remote URLs.

The **OBS on another computer (LAN)** URL works once the running listener has LAN enabled. The overlay and sanitized read-only state/events require no token for clients on permitted private IPv4 networks (including CGNAT/private VPN ranges). Remote control and full state require `Authorization: Bearer YOUR_PER_INSTALLATION_TOKEN`. A remote control browser prompts for the token and keeps it in that tab's session storage.

On the host, use **Copy API token** or **Regenerate token** under OBS Browser Source. Regeneration invalidates the old token immediately without restart; update remote browser sessions and every Companion action. Token retrieval, rotation, network discovery and the full-state event stream are host-only. Tokens are never part of an OBS URL.

The listener uses **unencrypted HTTP**. Treat the LAN as trusted: static interface files and hash-addressed graphics are not private content, and authorized private clients can view the overlay. Do not port-forward this service to the internet. Store backups securely because configuration contains the API token. See [Companion setup](COMPANION_SETUP.md) for request construction and [architecture](ARCHITECTURE.md#http-and-authentication-boundaries) for exact route boundaries.

## Configuration and backups

Locations follow `os.UserConfigDir()` unless `--config` is supplied:

| Launch mode | Configuration file |
|---|---|
| Windows executable directly | `%AppData%\FieldScoreboard\config.json` |
| Linux executable directly | `$XDG_CONFIG_HOME/FieldScoreboard/config.json`, or `~/.config/FieldScoreboard/config.json` when unset |
| Either portable launcher | `config.json` in the extracted application folder |
| Explicit `--config` | The supplied path (relative paths resolve from the process working directory) |

Next to the active configuration are `profiles/` (layout JSON), `backgrounds/` (original hash-named images) and, on Windows, `fieldscoreboard.log`. The Windows tray's Open data folder opens this directory. Profile files reference shared images; copying a profile alone does not copy its artwork.

There is **no automatic backup/export feature**. Stop the application, then copy `config.json`, `profiles/` and `backgrounds/` together to a private backup location. To restore or move a portable setup, stop the destination instance and restore these into its active data directory. Keep the same launch mode after an upgrade so the intended configuration is used. Avoid deleting artwork still referenced by any preset. Runtime clock progress is not saved or restored.

## Known limits and feedback

This is an x64 preview, not a competition rules engine. Linux has no native tray, and OBS Browser Source availability depends on its installation. Local test.12 includes independent ScoreSight match/shot clock, home/away score/foul and numeric period mappings; NDI, direct OBS integration and dedicated live Companion feedback are absent. Timing displays can lag with browser/network load; rehearse before a broadcast.

Report reproducible problems through [GitHub issues](https://github.com/ninoleto/FieldScoreboard/issues), including version, platform, launch mode and steps. Remove tokens, personal artwork and private configuration before attaching diagnostics. [Verification](VERIFICATION-v0.1.0-test.8.md) distinguishes automation from outstanding manual tests.
