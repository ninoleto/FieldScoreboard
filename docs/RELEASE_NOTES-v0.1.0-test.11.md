# v0.1.0-test.11 — seven OCR targets and element transformation

Local development build, 2026-11-07. No publication. Earlier packages and the public test.8 release remain unchanged. After user acceptance, the intended public version is **v0.1.0 as a normal release**, not another public test/prerelease.

## Changes

- Added independent **Home fouls**, **Away fouls** and **Period** OCR cards, for seven targets in total. Suggestions use actual Home Fouls/Away Fouls/Period source names only when present. One polling worker, shared freshness guidance and individual follow/takeover remain unchanged.
- Fouls accept 0–30 and numeric periods 1–20. Invalid/missing/rejected observations hold their prior values. Numeric and dot foul displays share the same count. Numeric period observations preserve OT; the operator controls OT separately and sees the latest saved number when turning it off.
- Manual ±, exact entry and API/Companion actions respect each field’s owner. Game reset rejects the entire operation if any score, foul count or period follows OCR. Saved mappings/game values persist, while restart begins manual/Ready/disconnected.
- Kept OCR last in Live control and changed only its outer container to neutral `#141414` with a subtle visible border. Inner cards, controls and status colors retain their styling.
- All nine layout elements have visible bounds, 56 px resize handles and a clear selected-element label. Drag to move; corners resize proportionally by default. Unlock aspect ratio for side handles and independent width/height. Large numeric ± controls provide precise sizing; no sliders.
- Optional element scales transform rendered text and foul dots. Scales and anchors persist as scores gain digits or names grow; there is no fixed clipping rectangle. Fonts, alignment, color, bold, visibility and nudge controls remain available. Save/Discard, presets and restart include the transform. Legacy OBS pixels remain unchanged until editing; preview/editor foul-dot box sizing now agrees with legacy OBS.
- Investigated the intermittent Windows reset recorded in test.10. Clock action requests with unread optional bodies reproduced it. Bodyless actions now consume optional bodies with size/time limits before mutation/reply. Existing authentication and empty/optional-body request semantics remain intact; no automatic retries mask errors.

## Testing and limitations

See [verification](VERIFICATION-v0.1.0-test.11.md), [operation guide](USER_GUIDE.md) and [OCR setup](OCR_PLAN.md). Automated tests cover seven-field ownership/OT/reset/persistence, element gestures and dynamic content, narrow/desktop/zoom geometry, existing regressions and native Windows/Linux packages. Actual test.10/test.11 OBS screenshots were pixel-equal for three untransformed legacy scenarios.

The live ScoreSight check observed Time, Home Score and Away Score. Fouls, period and shot-clock source fields were absent; those mappings and deliberate source failures/resets were simulated. `/json` still provides no video heartbeat or detection timestamp, so cached readings cannot prove live video.

Physical touchscreen ergonomics, Windows tray operation, test.11 inside OBS, LAN/Companion hardware and venue validation remain operator checks. Historical home OCR and Linux OBS Flatpak reports retain their original scope; they are not acceptance of this build. Use a separate extracted portable folder for rehearsal and retain manual fallback.
