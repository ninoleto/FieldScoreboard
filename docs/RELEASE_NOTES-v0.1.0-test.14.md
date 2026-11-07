# v0.1.0-test.14 — clearer connection and display controls

Local development build from test.13 (`ea0daec`). Do not publish this build. After acceptance, the intended public version is **v0.1.0**, a normal release.

- OCR connection action now shows red Not connected / Connection lost / Connection failed labels, a disabled Connecting state, and green Connected — Check connection. It tracks actual connectivity separately from following and video freshness. Visible help explains ownership restrictions.
- Editor toolbar places Free transform left and background editing right, with selection above and mode-specific help below. Narrow screens stack them in that order. Save/Discard stay separate; normal dragging and optional handles are unchanged.
- Inspector order is Match clock / Shot clock / Period, Home name / score / fouls, Away name / score / fouls, including keyboard order.
- Scoreboard display in Live control now owns the five foul/clock appearance options. It sits below the preview on desktop and after primary controls on narrow screens, before the final OCR section. Changes apply immediately and persist without saving layout edits.
- Stale layout Save, Discard and position reset preserve newer display preferences. Display updates do not commit/discard geometry or change live values, running clocks or OCR ownership. Legacy settings/full-layout API/preset appearance behavior stays compatible. Period format remains beside Period/OT.

Seven OCR mappings, strict period recognition, independent clocks, optional Free transform, touch controls, image transforms and the bounded HTTP transport fix are preserved. No sliders.

See [verification](VERIFICATION-v0.1.0-test.14.md) and [user guide](USER_GUIDE.md). Physical touchscreen, actual OBS, Windows tray, real capture changes/loss, separate-machine LAN, Companion hardware and venue validation remain operator checks. Connection success still cannot prove live video.
