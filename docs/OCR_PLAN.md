# ScoreSight connection: current scope and future work

## Setup in v0.1.0

Field Scoreboard supports seven independent targets: **match clock, shot clock, home/away scores, home/away fouls and numeric period**, with older saved mappings preserved.  The entire ScoreSight section is at the **bottom of Live control**, after scores, fouls, period, Both clocks and both individual clock panels and Foul indicators, before the footer. Polling does not scroll or move focus there.

1. Enter the ScoreSight address, default `http://127.0.0.1:18099`. The connection is made by the Field Scoreboard server, not the browser/tablet. A private LAN IP is also supported.
2. Choose the red **Not connected — Connect** button. **Connecting…** prevents duplicate requests. A successful check shows green **Connected — Check connection**; failure/loss shows a red Retry/Reconnect label. The button updates with actual connection state, separately from field ownership and camera freshness. Take all fields manual before rechecking/changing the connection; the disabled action has a visible explanation. One connection monitors all discovered fields, without taking control. Suggested mappings are selected only when the corresponding names actually exist:

   | Target | Suggested source | Accepted values |
   |---|---|---|
   | Match clock | Time | M:SS / MM:SS (one to five minute digits, exactly two second digits, at most 10080:00) |
   | Shot clock | Shot Clock | Whole seconds or M:SS / MM:SS, 0–3600 seconds |
   | Home score | Home Score | Whole numbers, 0–999 (one to three digits) |
   | Away score | Away Score | Whole numbers, 0–999 (one to three digits) |
   | Home fouls | Home Fouls | Whole numbers, 0–30 (one or two digits) |
   | Away fouls | Away Fouls | Whole numbers, 0–30 (one or two digits) |
   | Period | Period | Numbers (3), correct ordinals (3rd), or Q-prefixed values (Q3), representing 1–20 |

3. Each card has its own large source selector, recognised value, last accepted value, reading status and warnings. Choose another discovered field if needed. **Unconfigured — manual** explicitly removes a mapping and prevents automatic re-suggestion. Missing suggested fields remain unconfigured/manual. A saved mapping whose source disappears shows a missing-field warning.
4. Choose **Follow OCR** separately for each target. Mixed operation is supported: for example OCR match time and scores with a manual shot clock. Merely connecting or selecting a source never changes displayed values.
5. **Take manual control** immediately releases that target, retains its displayed value and leaves a clock paused. Press Start / Resume to time manually. Other targets keep following. Monitoring can continue, but following again always requires an explicit action.

Clocks follow accepted source values without an independent internal countdown. Source pauses and resets appear in subsequent readings; a valid zero is accepted. Missing, rejected or malformed readings never clear a field or turn it into zero. Failure of one field does not block the others. Connection loss holds all displayed values; recovery resumes only targets still following.

Manual controls and API/Companion actions cannot change an OCR-owned field. **Both clocks actions reject the entire operation when either clock follows**, leaving both unchanged. Reset scores & fouls rejects the entire operation while any score, foul count or period follows; no other value is reset. Other manual controls remain available. Because OCR cannot prove running status, a manual shot Reset/Set/preset stays Ready while the match clock follows OCR; start the shot clock explicitly. Normal conditional shot-reset behavior returns in manual mode. Auto-hide compares the effective match and shot values (configured duration minus elapsed for count-up match time).

Foul observations update the underlying count for either numeric or dot displays. Numeric period observations never toggle OT; they update the saved number shown when the operator turns OT off. OT remains an explicit manual display switch, including during period OCR. Team names are not mapped. Layout edits/presets preserve game values and OCR ownership.

## Validation and freshness

ScoreSight v0.4.3's observed full JSON format is an array:

```json
[{"name":"Time","text":"12:34","state":"SameNoChange","rect":{"x":1,"y":2,"width":100,"height":50}}]
```

Only `Success` and `SameNoChange` are accepted. `FailedFilter`, `Empty`, unknown statuses and malformed values are rejected independently. Seconds in colon-formatted times must be 00–59. No decimal times, signs, guessed digits or silent clamping are allowed. Period alone accepts case variations and surrounding whitespace; other targets retain their strict whitespace rules. Period parsing matches the entire value: 3, 3rd and Q3 normalize to 3; 13rd, Q3rd, Period 3, Q 3 and out-of-range values are rejected. Numeric digits may retain a leading zero (03); suffixes must match the number, including 11th/12th/13th. Duplicate names or invalid value/status types reject that source field without blocking valid other fields. An invalid whole response, timeout or HTTP error holds all values.

The observed `/json` endpoint supplies **no detection timestamp, frame sequence or video heartbeat**. HTTP Date, no-cache headers and repeated responses do not prove live video. Shared freshness guidance appears once above the seven cards. After three seconds without a numeric change, a card warns that its source may be paused or stale. This cannot distinguish an intentional pause from frozen/cached video; inspect ScoreSight. Last-change age measures observed numeric changes, not detection freshness.

The schema/status contract was checked against the [official HTTP API guide](https://royshil.github.io/scoresight/http_server.html) and a live endpoint in test.9; test.10 directly observed Time and Home Score. Test.11 live availability/results are recorded separately in its verification record. An optional overlay change counter is not a video heartbeat.

## Backend, persistence and API

One Go worker polls approximately five times per second with an 800 ms request timeout, bounded response size and no overlapping requests. It uses fixed `/json` GET requests, disables redirects/proxies and sends no Field Scoreboard credentials upstream. HTTP(S) addresses accept localhost or literal loopback/private IPs; credentials, query strings and arbitrary paths/public hosts are rejected. A pasted `/json` suffix is normalized.

Recognition is independent of **Period format** (Number/Ordinal/Quarter) beside the manual controls. The period remains numeric; raw source text stays in Recognised value, and the period card's last accepted value is the normalized number. OT overrides the displayed label without changing the chosen format, and OCR never toggles OT.

Address and mappings persist in optional config `ocr`. Test.9 `field` settings migrate to the main mapping. Suggestions are saved; an explicit empty mapping stays empty. Connection, observations, ownership and clock progress are runtime-only. Accepted score, foul and period changes use normal game persistence, without writing identical reads repeatedly. **Restart is manual/Ready and disconnected** with saved scores and mappings retained. Take all fields manual before changing/rechecking the connection; an individual manual target can be remapped while others follow.

All routes below require JSON content type and the existing bearer header for remote callers:

| POST route | Body |
|---|---|
| `/api/ocr/connect` | `{"address":"http://127.0.0.1:18099"}` |
| `/api/ocr/field` | `{"target":"main","field":"Time"}` (empty field unconfigures) |
| `/api/ocr/follow` | `{"target":"main"}` |
| `/api/ocr/manual` | `{"target":"main"}` |

Targets are `main`, `shot`, `home_score`, `away_score`, `home_fouls`, `away_fouls`, `period`; omitted target means `main` for test.9 API compatibility. `/api/state` exposes per-target status under `ocr.targets` and retains legacy main aliases. The read-only OBS feed exposes effective clock/score values, without OCR address, source list or warnings.

Connection generations and per-target revisions discard late responses only for changed targets. Takeover does not wait for network I/O. Browser poll responses begun before a control action are also discarded. OCR never repeatedly invokes Set/Start or alters configured durations/direction.

## Evidence and future work

See [v0.1.0 release verification](VERIFICATION-v0.1.0.md) and the historical [test.17 shot/name verification](VERIFICATION-v0.1.0-test.17.md), [test.16 preset/font verification](VERIFICATION-v0.1.0-test.16.md), [test.15 clock verification](VERIFICATION-v0.1.0-test.15.md), [test.14 interface verification](VERIFICATION-v0.1.0-test.14.md), [test.13 period verification](VERIFICATION-v0.1.0-test.13.md), historical [test.12 regression checks](VERIFICATION-v0.1.0-test.12.md), [test.11 verification](VERIFICATION-v0.1.0-test.11.md) and historical [test.9 verification](VERIFICATION-v0.1.0-test.9.md). On 2026-11-06 the operator reported match-clock OCR working in the home setup with test.9. **This is not venue validation.** Automated source pauses/resets/failures are simulations; Field Timer and the live source were not controlled by those tests.

Future work: verified detection freshness if supplied upstream, confidence/stability policy, multiple sources and venue evaluation. Automatic sport rules and guaranteed OCR accuracy are not included.
