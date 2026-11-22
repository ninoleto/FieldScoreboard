# Field Scoreboard v0.1.3

Stable release for Windows x64 and Linux x64, 2026-11-22. Free and open source under the MIT licence. [Download](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.3) · [User guide](USER_GUIDE.md) · [Verification](VERIFICATION-v0.1.3.md).

## Changes since v0.1.2

- Optional **Automatically change clock format in the final minute** for the ScoreSight Match clock. Choose whole seconds or tenths and Show zeros, Hide zeros or Seconds only, with matching examples and large accessible choices. It is off by default and changes display only.
- Match OCR accepts strict minutes/seconds or final-minute seconds/tenths independently of that switch. Exact observed values remain held between readings; the normal manual output format returns on takeover. Clean seconds with tenths use natural text width and saved anchors. Invalid or missing readings retain the last accepted value.
- ScoreSight cards follow Home/Away score, Home/Away fouls, Period/Shot clock, then full-width Match clock, including narrow-screen keyboard order.
- Optional floating previews keep saved Live control output or the unsaved Layout editor draft visible while scrolling. Each page has its own browser preference. Moving/resizing the preview does not change the layout or game.
- Background **Custom sizing** uses the standard blue status. Preset selection remains green, and sizing, aspect lock, Save/Discard and rendering behavior are unchanged.

Independent clocks, manual controls, seven-field OCR ownership, profiles, authentication and sanitized OBS output remain intact. No new runtime dependencies, accounts or services are required. All previous releases, tags, development archives and evidence are retained.

## Packages and upgrade

Download `FieldScoreboard-Windows-v0.1.3.zip`, `FieldScoreboard-Linux-v0.1.3.zip`, or `FieldScoreboard-Source-v0.1.3.zip`, and verify against `SHA256SUMS.txt`. Windows includes GUI and console executables; Linux runs in a terminal and has no tray. Native ZIPs contain launchers and documentation; the source ZIP contains the simulator and regression tools.

Stop the old instance and back up `config.json`, `profiles/` and `backgrounds/` together. Extract into a separate writable folder and retain the same configuration location and launch mode. Portable users copy that data into the new folder. Existing settings/profiles remain compatible. Restart leaves clocks Ready and OCR manual/disconnected; reconnect and follow explicitly. See [configuration and backups](USER_GUIDE.md#configuration-and-backups).

## Isolated rehearsal

From a separately extracted Windows package:

```powershell
.\fieldscoreboard-console.exe --config .\release-test\config.json --listen 127.0.0.1:18790 --open=false
```

From a separately extracted Linux package:

```bash
chmod +x fieldscoreboard
./fieldscoreboard --config ./release-test/config.json --listen 127.0.0.1:18790 --open=false
```

Open `http://127.0.0.1:18790`. From the source checkout, run `python scripts/simulate_ocr_clock.py --port 18199`. Connect the test scoreboard to `http://127.0.0.1:18199`, map Time and explicitly Follow OCR. Compare `01:00`, `59.9` and `55.4` with automatic formatting on and off, both precision options and all three appearances. Check retained invalid readings, paused takeover, saved manual format and disconnected restart. Match final-minute input accepts only seconds below 60 with at most one dot-separated tenth; `55:4`, `00:55.4`, `55,4`, `55.44` and `60.0` are rejected.

Compare the preview with `/overlay`, then exercise floating saved/draft previews and Custom sizing with Save/Discard. Keep production configurations and the real source separate. For a real ScoreSight rehearsal, point only the isolated scoreboard at the source and observe an operator-controlled rehearsal; never reset another application's live event just to test.

## Verification limits

Automated browser touch and zoom tests do not establish physical touchscreen validation. Windows tray interaction, actual ScoreSight/camera freshness, production OBS, separate-machine LAN/Companion and live-event checks remain operator work. Cached HTTP success cannot prove fresh video, and polling cannot promise every source tenth. The owner's historical v0.1.2 Linux PASS is separate from this release's Linux VM checks. NDI, direct OBS control and automatic sport rules remain future work.
