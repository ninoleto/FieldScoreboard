# v0.1.0-test.9 — Local ScoreSight match-clock test

**Local development packages only. Not published.** Built on the unchanged published test.8 checkpoint, on branch `ocr/scoresight-match-clock`.

- Added a touch-friendly ScoreSight panel under Live control: address, Connect / Check connection, a large dynamic field dialog, recognised/last accepted values, connection/reading warnings, Follow OCR clock and Take manual control.
- Defaults to the local ScoreSight service and selects Time when available. Go polls the full JSON endpoint about five times per second with bounded requests and no overlapping polls.
- Only accepted match-clock readings control time. No independent internal countdown, no repeated Set/Start calls, and no changes to unconfigured scores/fouls/period/shot clock.
- Bad/missing readings and connection failure retain the last value. Source pauses/resets follow subsequent readings. Takeover retains the displayed time paused, rejects late responses and requires explicit Follow to resume.
- Starts manual/Ready after restart. Address/field settings persist; ownership and readings do not.
- Independent shot control and effective-match auto-hide remain. During OCR ownership, shot resets stay Ready because the source does not report a verified running state.
- Preserved large dialogs, numeric steppers, image editing, Save/Discard, logical coordinates, profiles and existing authentication boundaries.

**Freshness limitation:** the observed ScoreSight v0.4.3 /json endpoint has no detection timestamp or video heartbeat. A successful HTTP poll is not proof of live video. The panel warns about unavailable freshness and unchanged values; a paused source and a frozen source cannot be reliably distinguished.

[Setup and behavior](OCR_PLAN.md) · [Verification](VERIFICATION-v0.1.0-test.9.md) · [User guide](USER_GUIDE.md)

Windows: extract the separate test.9 ZIP and run `start-portable.cmd` for isolated portable data. Linux: extract, run `chmod +x fieldscoreboard start-portable.sh`, then `./start-portable.sh`; keep the terminal open, stop with Ctrl+C. Stop any instance using port 8790 before testing, or run the executable with a separate `--config` and `--listen 127.0.0.1:8791`. Keep production backups and the published test.8 packages intact.

The live connection was observed against ScoreSight using OBS Virtual Camera. Source pause/reset, rejection, loss/recovery and timing races were simulated. Physical touchscreen, Windows tray, OBS visual end-to-end, LAN/Companion hardware and live-event checks are not newly claimed. No Field Timer changes.
