# ScoreSight connection: current scope and future work

## Local test.10 setup

Test.10 adds independent **match clock, shot clock, home score and away score** mappings to test.9. It is a local development build; the published test.8 release remains unchanged. The entire ScoreSight section is at the **bottom of Live control**, after scores, fouls, period, Both clocks and both individual clock panels, before the footer. Polling does not scroll or move focus there.

1. Enter the ScoreSight address, default `http://127.0.0.1:18099`. The connection is made by the Field Scoreboard server, not the browser/tablet. A private LAN IP is also supported.
2. Choose **Connect / Check connection**. One connection monitors all discovered fields, without taking control. Suggested mappings are selected only when the corresponding names actually exist:

   | Target | Suggested source | Accepted values |
   |---|---|---|
   | Match clock | Time | M:SS / MM:SS (one to five minute digits, exactly two second digits, at most 10080:00) |
   | Shot clock | Shot Clock | Whole seconds or M:SS / MM:SS, 0–3600 seconds |
   | Home score | Home Score | Whole numbers, 0–999 (one to three digits) |
   | Away score | Away Score | Whole numbers, 0–999 (one to three digits) |

3. Each card has its own large source selector, recognised value, last accepted value, reading status and warnings. Choose another discovered field if needed. **Unconfigured — manual** explicitly removes a mapping and prevents automatic re-suggestion. Missing suggested fields remain unconfigured/manual. A saved mapping whose source disappears shows a missing-field warning.
4. Choose **Follow OCR** separately for each target. Mixed operation is supported: for example OCR match time and scores with a manual shot clock. Merely connecting or selecting a source never changes displayed values.
5. **Take manual control** immediately releases that target, retains its displayed value and leaves a clock paused. Press Start / Resume to time manually. Other targets keep following. Monitoring can continue, but following again always requires an explicit action.

Clocks follow accepted source values without an independent internal countdown. Source pauses and resets appear in subsequent readings; a valid zero is accepted. Missing, rejected or malformed readings never clear a field or turn it into zero. Failure of one field does not block the others. Connection loss holds all displayed values; recovery resumes only targets still following.

Manual controls and API/Companion actions cannot change an OCR-owned field. **Both clocks actions reject the entire operation when either clock follows**, leaving both unchanged. Reset scores & fouls rejects the entire operation while either score follows. Other manual controls remain available. Because OCR cannot prove running status, a manual shot Reset/Set/preset stays Ready while the match clock follows OCR; start the shot clock explicitly. Normal conditional shot-reset behavior returns in manual mode. Auto-hide compares the effective match and shot values (configured duration minus elapsed for count-up match time).

Fouls, names and period/OT are not mapped. Layout edits/presets preserve game values and OCR ownership.

## Validation and freshness

ScoreSight v0.4.3's observed full JSON format is an array:

```json
[{"name":"Time","text":"12:34","state":"SameNoChange","rect":{"x":1,"y":2,"width":100,"height":50}}]
```

Only `Success` and `SameNoChange` are accepted. `FailedFilter`, `Empty`, unknown statuses and malformed values are rejected independently. Seconds in colon-formatted times must be 00–59. No decimal times, signs, surrounding whitespace, guessed digits or silent clamping are allowed. Duplicate names or invalid value/status types reject that source field without blocking valid other fields. An invalid whole response, timeout or HTTP error holds all values.

The observed `/json` endpoint supplies **no detection timestamp, frame sequence or video heartbeat**. HTTP Date, no-cache headers and repeated responses do not prove live video. Shared freshness guidance appears once above the four cards. After three seconds without a numeric change, a card warns that its source may be paused or stale. This cannot distinguish an intentional pause from frozen/cached video; inspect ScoreSight. Last-change age measures observed numeric changes, not detection freshness.

The schema/status contract was checked against the [official HTTP API guide](https://royshil.github.io/scoresight/http_server.html) and a live endpoint in test.9; test.10 directly observed Time and Home Score. An optional overlay change counter is not a video heartbeat.

## Backend, persistence and API

One Go worker polls approximately five times per second with an 800 ms request timeout, bounded response size and no overlapping requests. It uses fixed `/json` GET requests, disables redirects/proxies and sends no Field Scoreboard credentials upstream. HTTP(S) addresses accept localhost or literal loopback/private IPs; credentials, query strings and arbitrary paths/public hosts are rejected. A pasted `/json` suffix is normalized.

Address and mappings persist in optional config `ocr`. Test.9 `field` settings migrate to the main mapping. Suggestions are saved; an explicit empty mapping stays empty. Connection, observations, ownership and clock progress are runtime-only. Accepted score changes use normal game persistence, without writing identical reads repeatedly. **Restart is manual/Ready and disconnected** with saved scores and mappings retained. Take all fields manual before changing/rechecking the connection; an individual manual target can be remapped while others follow.

All routes below require JSON content type and the existing bearer header for remote callers:

| POST route | Body |
|---|---|
| `/api/ocr/connect` | `{"address":"http://127.0.0.1:18099"}` |
| `/api/ocr/field` | `{"target":"main","field":"Time"}` (empty field unconfigures) |
| `/api/ocr/follow` | `{"target":"main"}` |
| `/api/ocr/manual` | `{"target":"main"}` |

Targets are `main`, `shot`, `home_score`, `away_score`; omitted target means `main` for test.9 API compatibility. `/api/state` exposes per-target status under `ocr.targets` and retains legacy main aliases. The read-only OBS feed exposes effective clock/score values, without OCR address, source list or warnings.

Connection generations and per-target revisions discard late responses only for changed targets. Takeover does not wait for network I/O. Browser poll responses begun before a control action are also discarded. OCR never repeatedly invokes Set/Start or alters configured durations/direction.

## Evidence and future work

See [test.10 verification](VERIFICATION-v0.1.0-test.10.md) and historical [test.9 verification](VERIFICATION-v0.1.0-test.9.md). On 2026-11-06 the operator reported match-clock OCR working in the home setup with test.9. **This is not venue validation.** Automated source pauses/resets/failures are simulations; Field Timer and the live source were not controlled by those tests.

Future work: OCR fouls/period, verified detection freshness if supplied upstream, confidence/stability policy, multiple sources and venue evaluation. Automatic sport rules and guaranteed OCR accuracy are not included.
