# v0.1.0-test.10 — independent ScoreSight mappings

Local test build, 2026-11-06. Not published. Test.9 packages and the published test.8 release remain available unchanged.

## Changes

- Moved the complete ScoreSight OCR section to the bottom of Live control, after all manual panels and before the footer. Connection changes, polling and ownership do not reorder the page or move focus/scroll to OCR.
- Added four touch-friendly cards: match clock, shot clock, home score and away score. Each has a large source selector, recognised/last accepted value, status/warning and independent Follow OCR / Take manual control buttons. Connection and freshness guidance are shared.
- Discover actual fields through one connection and polling worker. Suggest Time, Shot Clock, Home Score and Away Score only when present. Missing targets stay manual; explicit unconfiguration is saved.
- Support mixed manual/OCR operation. Owned clocks hold accepted source values without an internal countdown. Takeover keeps the displayed value, pauses clocks and blocks late source/browser responses from restoring old state.
- Guard manual and API operations by ownership. Combined clock actions reject atomically if either clock follows; game reset rejects atomically if either score follows. A manual shot reset does not infer running status from OCR match time.
- Validate each field independently. Invalid/missing/rejected data holds its last value; one failed field does not block other updates. No clamping or invalid-to-zero fallback. Auto-hide uses effective match and shot values.
- Save mappings and changed scores, with test.9 config compatibility. Restart always begins manual/Ready and disconnected.

Existing clocks, fouls, OT, layouts/presets, background proportions, Save/Discard, authentication, Companion APIs and large touch controls are retained. No sliders were added. Field Timer is unchanged.

## Use and limitations

Extract the local Windows/Linux package into its own folder and use its portable launcher for isolated testing. Open Live control, scroll below the manual panels, connect and choose Follow on each desired target. See the [ScoreSight guide](OCR_PLAN.md) and [verification record](VERIFICATION-v0.1.0-test.10.md).

The operator reported test.9 match-clock OCR working in a home setup on 2026-11-06. This is not venue validation. Test.10 live observations covered Time and Home Score; shot/away mappings and deliberate source failures/resets were tested with simulations.

ScoreSight v0.4.3 `/json` supplies no detection timestamp or video heartbeat. Repeated reads cannot establish live video; an unchanged reading can be paused or stale. Check the source video and retain a manual fallback. OCR fouls/period, automatic sport rules and confidence/stability filtering are not implemented. Physical touchscreen, Windows tray, OBS operation with this build, LAN/Companion hardware and venue use still require operator checks.
