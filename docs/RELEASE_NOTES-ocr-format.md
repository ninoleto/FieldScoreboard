# Local test build v0.1.2-ocr-format.4

This is an unpublished feature build based on v0.1.2 (`2f85c9a`), on local branch `feature/ocr-automatic-time-format`. No remote branch, tag, release or older asset is changed. Public v0.1.2 remains the normal release. These packages are for local testing; publication requires separate owner approval.

## Changes

The operator accepted .3 functionality. This .4 build only improves ScoreSight Match clock wording and usability; the OCR engine, manual output menu, shared renderer and saved layout geometry are unchanged.

- **Automatically change clock format in the final minute** replaces the technical switch label, with a short explanation and a separate message when automatic switching is off. Following OCR continues in either state.
- **Time precision** offers **Whole seconds — 30** and **Tenths of a second — 30.6**. The saved values remain `SS` and `SS.t`.
- **Final-minute appearance** offers **Show zeros**, **Hide zeros** and **Seconds only**, with brief descriptions inside the existing selection dialog. Examples update from 00:30 / :30 / 30 to 00:30.6 / :30.6 / 30.6 when tenths are selected. Saved values remain `visible`, `invisible` and `clean`.
- Choices remain full-width buttons, at least 64 px high, with selected highlighting, keyboard navigation and restored focus. Closed selectors show the same clear labels/examples. No extra preview is added.
- A short explanation makes clear that these settings affect only display and that normal Match Clock formatting returns on manual takeover. Detailed precision, rounding and alignment rules remain in the [user guide](USER_GUIDE.md) and [OCR plan](OCR_PLAN.md).

All accepted .3 behavior is retained: decimal recognition with the switch on or off; exact held source time; whole-second prefix alignment; natural clean SS.t positioning; ordered ScoreSight cards; floating saved/draft previews; upright interface typography. Windows GUI/console and Linux binaries are rebuilt because embedded UI assets changed. All .1/.2/.3 archives and evidence are preserved.

## Safe Windows test

1. Extract `FieldScoreboard-Windows-v0.1.2-ocr-format.4.zip` into a new test folder. Keep the existing production installation/configuration separate.
2. From PowerShell in that extracted folder, run:

   ```powershell
   .\fieldscoreboard-console.exe --config .\ocr-format-test\config.json --listen 127.0.0.1:18790 --open=false
   ```

   Open `http://127.0.0.1:18790`. If that test port is occupied, use another unused loopback port. The explicit config and listen flags isolate this instance from the production scoreboard. Closing the browser does not stop the Windows app; exit its test instance through the tray menu.
3. In a separate terminal at the source checkout (or extracted source ZIP), run the standard-library-only simulator with Python 3:

   ```powershell
   python scripts/simulate_ocr_clock.py --port 18199
   ```

   In the prepared development workspace, `.\.venv\Scripts\python.exe` can be used instead of `python`. The simulator listens only on loopback and never contacts ScoreSight. Stop it with Ctrl+C.
4. In the test scoreboard, set a distinctive manual Output format such as **HH:MM:SS**. Under ScoreSight enter `http://127.0.0.1:18199`, choose Connect, enable **Automatically change clock format in the final minute**, select **Time**, then choose **Follow OCR**. Do not use the live source address for this test.
5. The simulator holds each source reading for four seconds and repeats: `01:01`, `01:00`, `59.9`, `55.4`, `55.3`, malformed/rejected readings, `9.7`, `0.1`, `0.0`, `20:00`. Check SS/SS.t in all three final-minute styles, last-value retention on the invalid readings, and the reset back to MM:SS. The value must stay still between source updates.
6. Open `http://127.0.0.1:18790/overlay` in another tab to compare the preview/output. An isolated OBS Browser Source can use that URL with 1920×1080 dimensions.
7. Choose **Take manual control**: the same time remains paused, now using the saved manual format. Stop/restart the test app with the same command: the preference should remain enabled, but the clock should be Ready and OCR disconnected/manual. Reconnect and follow explicitly to resume this simulator test.

The simulator ships in the **source ZIP**. Native packages contain the application and documentation; they need no Python to run. Automated reproduction is also available from the checkout with `python scripts/test_ocr.py <test-console-binary> --ui`.

## Focused operator checks for .4

First open **Time precision** and **Final-minute appearance**. Check both precision choices, all three appearance descriptions and their matching examples; use touch or keyboard and confirm focus returns to the selector. Turn automatic switching off and confirm the short normal-format explanation appears.

With the simulator or an operator-controlled rehearsal, follow Match clock with the automatic format switch OFF. Confirm decimal readings continue updating and remain exact internally. Try all five existing Output formats: at 48.2 seconds, countdown MM:SS displays `00:49`, M:SS `0:49`, HH:MM:SS `00:00:49`, SS `49`, and MM:SS.t `00:48.2`. Turn the automatic override ON and OFF while following; it must change presentation without freezing, resetting, taking control of another field or losing precision.

Choose clean SS.t and compare `30.6` at left, center and right anchors in editor, floating draft preview, saved preview and OBS. It must use natural text width without a hidden `00:` prefix. Whole-second clean/invisible styles retain their alignment space. Check the four desktop ScoreSight rows and the same mobile reading order.

## Floating-preview rehearsal

In Live control enable **Floating preview when scrolling**, then scroll below the main preview. Verify the floating values match the saved preview/overlay. Drag the title to move, use the corner to resize, try the size buttons, and reload. Close it to disable only Live control's preference.

In Layout editor enable its separate switch, make an unsaved position/font/background change and scroll away from the editor canvas. The floating **Layout draft** should show that change while OBS stays saved. Discard should restore it; Save Layout should update OBS. Verify 375 px and desktop widths, keyboard arrows on move/resize (Shift for one pixel), and 200%/400% zoom. No floating control should change clock/game values.

## Safe Linux test

Extract `FieldScoreboard-Linux-v0.1.2-ocr-format.4.zip` into a new writable test folder. From that folder:

```bash
chmod +x fieldscoreboard
./fieldscoreboard --config ./ocr-format-test/config.json --listen 127.0.0.1:18790 --open=false
```

Open `http://127.0.0.1:18790` and follow the same simulator and UI checks above. Use `python3 scripts/simulate_ocr_clock.py --port 18199` from the source checkout or extracted source ZIP. Stop the Linux scoreboard with Ctrl+C; Linux has no tray. Keep the explicit test config and port when restarting.

## Operator check against ScoreSight

After the simulator rehearsal, keep using the isolated test scoreboard. In its ScoreSight section, **Disconnect**, replace the simulator address with your running ScoreSight HTTP server address (for example `http://127.0.0.1:18099` when ScoreSight runs on this computer), and **Connect**. This reads ScoreSight's `/json` endpoint; it does not control the source. Select the actual match-clock field, usually **Time**, enable **Automatically change clock format in the final minute**, choose **Tenths of a second — 30.6**, and explicitly **Follow OCR** for Match clock. Other fields can stay manual.

During an operator-controlled rehearsal, compare **Recognised value**, **Last accepted value**, the preview and `/overlay` as the real source crosses `01:00` to `59.9` and `55.4`. Confirm MM:SS at 60 seconds and above, exact observed tenths below 60, SS truncation when selected, and MM:SS again when the source resets to `20:00`. Take manual control or Disconnect and confirm the saved manual format returns with the same paused duration. Reconnect must not resume following automatically. Do not change a production event merely to exercise these cases.

Record actual source strings and any warnings if a value is rejected; the supported forms are listed below. Connection status alone does not prove live video. This real-source operator check is still outstanding; automated tests used simulated sources only.

## Local package files

The completed set is copied to `dist/v0.1.2-ocr-format.4/`: Windows, Linux and source ZIPs named above, plus `SHA256SUMS.txt`. The source ZIP is `FieldScoreboard-Source-v0.1.2-ocr-format.4.zip`. Earlier candidate files at the top of `dist/` and all older archives remain preserved. Use the final ZIPs and checksum manifest from this version's folder. See [verification results](VERIFICATION-ocr-format.md) for new checks, reused evidence and executable hashes.

## Input and real-world limits

The supported match-clock source forms, regardless of the automatic display setting, are M:SS/MM:SS (existing minute-width/range limits), or final-minute SS/SS.t with exactly one dot-separated tenth and a value below 60. Inputs such as `55:4`, `00:55.4`, `55,4`, `55.44` and `60.0` are deliberately rejected; the 60-second boundary is `01:00`. Other targets keep their existing strict validation.

Polling remains approximately five times per second; the app may skip source tenths between observations and cannot promise to show every tenth. It never invents missing readings. HTTP success still cannot prove fresh video. This build has simulated-source/browser verification only, plus native OS tests listed in [development verification](VERIFICATION-ocr-format.md). Real ScoreSight/camera behavior at the venue, physical touch hardware, Windows tray interaction, production OBS and LAN/Companion require separate operator checks. No live ScoreSight or production scoreboard was contacted during this work.
