# Field Scoreboard user guide

[Download and quick start](../README.md) · [Companion setup](COMPANION_SETUP.md) · [v0.1.2 verification](VERIFICATION-v0.1.2.md)

## Starting and stopping

Download v0.1.2 from the [release page](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.2) and extract the complete Windows or Linux ZIP into a writable folder. On Windows, double-click `fieldscoreboard.exe` to start. Windows x64 has a GUI executable (`fieldscoreboard.exe`) and a diagnostic console executable (`fieldscoreboard-console.exe`); both use the native tray. Double-click the tray icon to reopen the control panel. Right-click for Open Field Scoreboard, Open data folder or Exit Field Scoreboard. Closing a browser tab does not stop the server or clocks.

For Windows portable storage, use `start-portable.cmd`. For Linux portable storage, open a terminal in the extracted folder:

```bash
chmod +x start-portable.sh fieldscoreboard
./start-portable.sh
```

**Sudo is unnecessary.** The terminal stays open while Field Scoreboard runs; press Ctrl+C to stop. Linux has no tray. Running `./fieldscoreboard` directly uses the user configuration directory instead. Both platforms open the browser automatically unless launched with `--open=false`. Open **http://127.0.0.1:8790** manually if needed.

Do not start two instances using the same configuration or listening port. A port-in-use error usually means an instance is already running. Windows startup errors appear in a dialog; its log is `fieldscoreboard.log` next to the active configuration. Linux logs to the terminal. For a custom location, use `--config /path/to/config.json` (quote paths containing spaces).

## Operating a match

**Foul indicators** sits directly below the preview on wide screens. On narrow screens it follows the primary scores and clock controls, before OCR. Choose home/away foul indicator format and maximum dots per team (1–20) here. Each clock output-format selector is in its own clock card. Changes apply immediately to preview and OBS and persist after restart; no Layout editor Save is needed. Counts, clock times/running state, periods and OCR ownership are unchanged. Unfinished dot-count edits survive polling. Display changes never commit or discard unrelated layout edits. Layout Save, Discard and Restore Defaults keep the latest display preferences. Explicitly loading a layout preset restores its saved foul/clock display preferences, as before; it never changes live game values or the separate Period format.

Field Scoreboard places **ScoreSight OCR at the bottom of Live control**, after all manual panels. Use the large **Connect** and **Disconnect** buttons. The top-right status badge reads **Not connected** (red), **Connecting…** (amber), **Connected** (green), or **Connection lost / Connection failed** (red). Connect is unavailable while connecting or connected. Disconnect is available while monitoring, including during connection loss or source polling; controls prevent duplicate pending requests. Status describes the backend connection independently of field ownership. A successful connection does not prove fresh camera video. **Disconnect** stops polling, cancels the pending source request and releases every followed field without changing its displayed value. Followed clocks remain paused; independent manual clocks keep their existing state. The saved address and mappings remain. Disconnect before editing the address. Reconnecting, or explicitly choosing Connect after an error, requires fresh **Follow OCR** choices and never starts clocks. Connect once, then select a discovered source and **Follow OCR** independently for match time, shot time, home/away scores, home/away fouls or numeric period. Missing fields remain unconfigured/manual. **Take manual control** retains that field’s displayed value; clocks stay paused until Start / Resume. Rejected/missing readings and connection failures keep values. Both-clock actions require both clocks manual, and game reset requires scores, fouls and period manual. Manual shot reset stays Ready while match time follows OCR because source running status is unknown. Mappings persist; restart is manual/Ready and disconnected. See [setup, validation and freshness limits](OCR_PLAN.md). Fouls accept 0–30; period OCR accepts numbers, valid ordinals and Q-prefixed values representing 1–20 (for example 3, 3rd and Q3). Case and surrounding whitespace are ignored; malformed values retain the last accepted number. Numeric OCR changes the saved period number without toggling OT. The OT switch remains manual; turning it off reveals the latest accepted period. The manual behavior below applies to fields not following OCR.

**Live control** contains immediate score, foul, name and period updates. Scores allow 0–999, fouls 0–30 and periods 1–20. Tap a score/foul/period value, or focus it and press Enter/Space, for exact entry. OT changes only the displayed period label; turning it off restores the selected format using the current numeric period. Reset game clears scores, fouls and OT and returns the period to 1; use clock controls separately to reset timing. Reset game retains the display-format setting.

**Home team / Away team** use bold 21 px labels and full-width name inputs at least 64 px high, with 24 px text. Click/tap the field or its label to edit; Tab or moving focus commits the change. The existing input limit is 32 characters; surrounding whitespace is trimmed and empty names are rejected. Polling leaves an active edit and its caret alone. Name entry remains available while scores/fouls follow OCR. These control-panel sizes do not change scoreboard name typography or positions; use Layout editor for those.

**Period format** beside Period / half and OT has three large single-choice buttons: **Number** (1, 2, 3), **Ordinal** (1st, 2nd, 3rd) and **Quarter** (Q1, Q2, Q3). Number is the default for existing installations. Selection applies immediately, persists after restart, and does not change the period number or manual/OCR ownership. Ordinals include 11th, 12th and 13th. OT overrides all formats until switched off. Layout Save/Discard and presets do not change this live setting. Exact entry and API period commands remain numeric. In the OCR card, Recognised value retains the source text and Last accepted period (number) shows the normalized number; OCR 3rd can therefore display as Q3.

The match clock counts down or up; the shot clock counts down. They are independent. Each has Start, Pause, Stop, Reset and time corrections. **Both clocks → Start both / Pause both** starts or pauses them together without changing their current times.

Both clock cards begin with title/status and current time; Start / Resume, Pause, Stop, Reset; then **−5s / −1s / +1s / +5s**. The shot card next shows **Duration presets**, **Applies immediately**, and large **14s / 24s / 30s** buttons. Directly below is the reminder: “Reset / 14s / 24s / 30s: shot clock resumes automatically if the match clock is running.” A divider then introduces **Clock setup**. Both cards keep a full-width blue **Set match clock** or **Set shot clock** button last. Quick adjustments apply immediately to the selected clock, keeping its running/paused behavior. The existing countdown rule still completes at zero; negative values are prevented, and adjustments above seven days are rejected. Both quick rows use matching large targets and become 2×2 when space is limited. Minute changes use the Minutes setup field and Set, rather than separate minute shortcuts.

Match Clock setup contains Minutes, Seconds, Direction and Output format. Shot Clock setup contains Seconds, Output format and Auto-hide with status/help; its immediate presets sit above the divider. Its help reads: “Duration applies with Set. Output format applies immediately.” **Output format applies immediately and persists independently of Set**, even when time follows OCR. It uses the same layout-draft protection as foul display preferences. Live time adjustments, Set, reset and shot presets respect OCR ownership; take that clock manual first.

Minutes and Seconds are separate editable groups. Their ± buttons retain one-unit increments. Zero minutes is valid when the total is at least one second. Seconds ± carries/borrows across minutes. Edits stay pending until **Set match clock**; the shot duration likewise waits for Set. Polling and navigation preserve unfinished entries. Correct invalid values before applying them.

**Duration presets** above Set match clock offer **5 min / 8 min / 10 min / 12 min / 20 min**. Choose a duration, then press Set match clock. A preset fills Minutes and sets Seconds to 0; it does not change the live clock, even while running. Pending Direction and immediate Output format stay unchanged, as do every other game value and OCR ownership. The matching pending duration is highlighted; custom values clear the highlight. Custom numeric entry remains available. You can prepare setup while following OCR, but Set remains unavailable until explicit manual takeover. These pending match presets are separate from the immediate shot presets.

**Shot reset behavior:** Reset shot clock, Set shot clock and the 14/24/30-second presets restore the shot duration and resume it only when the match clock is currently running. Otherwise it stays Ready. They do not start, pause or reset the match clock. Independent shot Start/Pause/Stop still works.

**Auto-hide** affects only shot-clock output: it hides when shot remaining time is greater than or equal to remaining match time, or the match has expired. For count-up, remaining match time is configured duration minus elapsed time. The shot clock continues internally, and the operator still sees its value. The layout editor keeps the shot field visible for positioning. Auto-hide defaults to off.

Restarting retains scores, fouls, names, period/OT/display format, durations, direction, auto-hide and saved layout. It resets both runtime clocks to Ready; it never resumes play automatically. Sport-specific rules and automatic period advancement are not implemented.

## Touch, mouse and keyboard

Large controls are the default even on a desktop with a mouse. Numeric ± groups use large labelled fields and visible gaps; narrow layouts stack groups. Every dropdown opens a centered choice dialog: scroll the options, select by touch/mouse, or use arrows, Home/End, typing a prefix and Enter/Space. Escape, Close or an outside tap dismisses it and restores focus. Small screens show a Menu button with the current page name; switching pages preserves drafts.

## Layouts and background graphics

The editor always stores **1920×1080 logical coordinates**. Browser size and zoom change only preview scale. Select a scoreboard field using the field controls or drag it in the preview. Configure position, font, size, color, weight, alignment and visibility. Fouls can use numbers or colored dots separately per team; counts beyond the selected dot maximum show an extra-count indicator.

**Move and resize any element:** select its field button or the rendered field. The “Editing:” label identifies the current selection above the toolbar. **Free transform** is on the left; **Edit background — move & resize** is on the right. They stack in that order on narrow screens, with mode-specific instructions below. The top action group is **Restore Defaults | Discard | Save Layout**, separate from the mode toolbar. Inspector buttons follow clock/shot/period, home name/score/fouls, away name/score/fouls order, including keyboard navigation. Normal mode opens by default: drag the field to move it, with only a thin selection outline. Choose **Free transform** beside the preview to reveal the 56 px resize handles. The active button reads **Done transforming**; choose it to hide the handles while retaining draft changes. Drag corner handles to resize proportionally. **Lock aspect ratio** is on by default. Turn it off for independent width/height resizing with the four side handles, or use the large Width/Height ± fields. On small previews, the dotted handle guide expands so handles remain distinct; the solid border shows the actual content bounds. Handles support arrow keys (1 logical pixel; Shift 10). Hidden fields can be made visible using the existing visibility control.

Open **Font** to choose the family and use the large **Bold** switch in its own row. Bold stays visible while the font list scrolls and toggling it leaves the picker open. The closed control shows, for example, **Serif · Bold** or **Serif · Regular**. Family changes keep weight; weight changes keep family. Tab reaches Bold, Space/Enter toggles it, and Close/Escape returns focus to Font. These are selected-element draft edits: Save layout applies them to preview/OBS; Discard restores saved settings. Layout presets and restart retain saved font/weight.

Width/height describe the current rendered value. Saved horizontal/vertical scales (5%–2000%) remain constant when a score changes from 9 to 10, a longer team name arrives, or foul dots change. Content can grow without a fixed clipping box; the canvas edge still clips output. Alignment keeps the left/center/right anchor at X. Font, color, bold and font size remain independently editable. **Reset element size** removes the extra scaling while retaining font settings and position. Legacy layouts have no extra scale and keep their previous OBS output until edited.

Selecting a field and editing the background are mutually exclusive. Free transform exits when selecting another field, entering background editing, leaving Layout editor or reloading the page. It is never stored in layouts or presets. Numeric position, size, font and aspect controls remain available in normal mode; existing transforms always render. Mode switches never save, discard or reset edits. Borders, dotted guides and handles appear only in the editor. Changes stay pending until **Save layout**; **Discard**, presets and restart preserve the chosen transform. Unfinished numeric drafts survive polling/navigation and invalid dimensions block Save. No sliders are used.

The coordinate and text-anchor explanation sits directly below X/Y, above Fine position. **Fine position** uses 5/10/20 px with 5 px selected by default. All four arrow-pad buttons use that step and clamp field anchors to X 0–1920 and Y 0–1080. X/Y ± stays at 1 px. Keyboard arrows on a selected field move 1 px, or 10 px with Shift; they are independent of the step selector. Anchors at the canvas edge may place part of a field outside the visible canvas.

Import PNG, JPG or WebP up to 15 MB and 8192 pixels per side. Original file bytes are kept unchanged. New imports default to centered **Fit entire image**, with **Lock aspect ratio** enabled.

**Sizing** has four large, always-visible buttons in a balanced 2 × 2 grid. Each has a prominent label and an explanation. The active preset uses the selected green color, bright border and checkmark. On narrow screens the buttons stack at full readable size. Tab reaches each button; Enter or Space applies it to the draft. With no background imported, all four remain visible but disabled.

| Sizing button | Result |
|---|---|
| Fit entire image | Preserve proportions, show the complete image and center it. |
| Fill canvas | Preserve proportions, cover the canvas and crop overflow. |
| Original size | One image pixel per logical canvas pixel, centered. |
| Stretch to canvas | Explicitly stretch to 1920×1080, allowing distortion. |


**Custom sizing** is a status, not a fifth button. Manual position/size edits, dragging, resizing or Center image switch to Custom and clear all preset highlights. Choosing a preset or Reset to fit restores the corresponding highlight. Changing the aspect-ratio switch alone keeps the current sizing mode. Fit and Reset to fit enable aspect lock; the other presets keep the current switch setting, as before. Discard and profile loading restore the saved sizing mode and selection, including Custom.

The aspect-ratio switch and numeric controls remain below the sizing buttons. In **Background graphic**, edit Width, Height, X and Y using exact values or large ± buttons. With aspect lock enabled, changing either dimension updates the other from the original proportions. Unlock it for independent dimensions. X/Y is the top-left position; negative positions crop the image. **Center image** keeps its size; **Reset to fit** restores fit, centering and aspect lock. Original dimensions appear for reference.

Use **Edit background — move & resize** beside the preview before dragging the graphic or resizing its generous corner handles. The active button reads **Finish editing background**. This explicit selection prevents moving a score or clock while editing the background. Keyboard arrows move the selected image (Shift for larger increments); focused corner handles support keyboard resizing. Escape or Finish editing background leaves this mode. The graphic always stays behind the scoreboard; selection borders and handles appear only in the editor. No sliders are used.

**Save Layout** applies pending changes, including sizing presets and import/removal, to the saved preview and OBS. Sizing buttons update the editor draft immediately; the live preview and OBS keep the saved layout until Save Layout. **Discard** restores the saved layout and graphic. Incomplete numeric drafts survive polling and page navigation and must be corrected before saving. Named layout presets include the graphic reference, placement, original dimensions and aspect lock. Loading a preset changes the layout immediately after any unsaved-change confirmation, without replacing game values or clocks. Saving a preset first saves pending layout edits.

**Restore Defaults** keeps the existing reset scope: it restores element X/Y and font sizes and removes optional element transforms in the draft. It preserves the background, other element styling, live display preferences, match data, clocks and saved profiles. Choose Save Layout to commit or Discard to return to the saved layout.

The full-width **Layout profiles** card below both editor columns contains Saved profile, Load, Delete, Profile name and Save preset. Load applies the chosen preset immediately after any draft-discard confirmation; Delete removes only that preset. Save preset first saves pending layout changes. Background sizing, positioning, Center image and Reset to fit remain together in Background graphic. On desktop the preview/background and Element inspector cards share top and bottom edges; narrow screens stack them above profiles without shrinking controls.

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

**Upgrading to v0.1.2:** stop the old instance and make the backup above. Extract the new application into a separate writable folder. If using a portable launcher, copy the existing `config.json`, `profiles/` and `backgrounds/` together into that folder before starting it. If launching the executable directly, the new version uses the same user configuration directory; retain any existing `--config` argument instead if you use a custom path. Packages contain no user configuration or personal images. Existing settings and profiles remain compatible. Do not switch between portable and direct launch unless you intentionally move the data. On restart, clocks are Ready and OCR is disconnected/manual; reconnect and choose Follow OCR explicitly.

## Known limits and feedback

Field Scoreboard v0.1.2 supports Windows/Linux x64. On 2026-11-07 the owner accepted the interface and reported the Linux test PASSED; that report does not establish additional physical touchscreen, venue OCR or OBS testing. Automatic competition rules are not implemented. Linux has no native tray, and OBS Browser Source availability depends on its installation. The release includes independent ScoreSight match/shot clock, home/away score/foul and numeric period mappings; NDI, direct OBS integration and dedicated live Companion feedback are absent. Timing displays can lag with browser/network load; rehearse before a broadcast.

Report reproducible problems through [GitHub issues](https://github.com/ninoleto/FieldScoreboard/issues), including version, platform, launch mode and steps. Remove tokens, personal artwork and private configuration before attaching diagnostics. [Verification](VERIFICATION-v0.1.2.md) distinguishes automation from outstanding manual tests.
