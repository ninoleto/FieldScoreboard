# ScoreSight connection: current scope and future work

## Implemented in v0.1.0-test.9 (local development build)

The first working connector follows **one match-clock field** from ScoreSight's read-only `GET /json` endpoint. It was checked against a running ScoreSight v0.4.3. This build is local-only; the published test.8 release is unchanged.

Under **Live control → ScoreSight OCR — match clock**:

1. Enter the ScoreSight address, default `http://127.0.0.1:18099`. This is relative to the Field Scoreboard server, not the browser/tablet. A private LAN IP is also supported.
2. Choose **Connect / Check connection**. This starts monitoring without changing the match clock. The large field dialog lists actual returned fields and selects **Time** when available. Select a different field if needed.
3. Inspect the recognised text, ScoreSight status and warnings. A valid `MM:SS` reading enables **Follow OCR clock**.
4. Choose Follow explicitly. Accepted readings now supply the displayed match time; the internal clock does not advance between readings. Source time changes, pauses, resets and a valid `00:00` are reflected by subsequent readings.
5. **Take manual control** immediately releases OCR ownership, keeps the displayed time and leaves the match clock paused. Start / Resume starts manual timing. Monitoring can continue, but it cannot change the clock until Follow is explicitly chosen again.

Match/combined transport, Set and adjustment actions are blocked while following; use Take manual control first. Shot controls remain independent. Because this endpoint cannot prove the source's running state, shot reset/set stays Ready during OCR ownership; start the shot clock explicitly. Normal conditional shot-reset behavior returns in manual mode. Auto-hide uses the effective OCR match value (configured duration minus elapsed for count-up).

Only the match clock is mapped. Unconfigured scores, fouls, names, period/OT and shot clock are untouched. The operator can still change those fields manually. Layouts/presets remain independent.

## Source contract and freshness

The observed and documented full JSON format is an array:

```json
[{"name":"Time","text":"12:34","state":"SameNoChange","rect":{"x":1,"y":2,"width":100,"height":50}}]
```

Accept `Success` and `SameNoChange` only. Reject `FailedFilter`, `Empty`, unknown states and malformed time strings. Parsing accepts one to five minute digits and exactly two second digits, seconds 00–59, with a seven-day maximum. No decimal times, substitutions or guessed digits. A missing field, invalid payload, timeout or HTTP error keeps the last match time and shows a warning. Recovery resumes updates only if OCR still owns the clock.

ScoreSight v0.4.3's observed `/json` responses supply **no detection timestamp, frame sequence or video heartbeat**. Its HTTP Date/no-cache headers and repeated `Success`/`SameNoChange` responses do not prove a live video feed. The panel therefore always identifies freshness as unverified. After three seconds without a value change it warns that the source may be paused or stale. That warning cannot distinguish an intentional pause from a frozen source; inspect the ScoreSight video. The last-change age measures observed numeric changes, not detection freshness. No extrapolated countdown or stale-to-zero fallback is used.

The actual schema and status interpretation were checked against the [official HTTP API guide](https://royshil.github.io/scoresight/http_server.html) and the live endpoint. The optional overlay version counter tracks changes, not a video heartbeat, and is not treated as source freshness.

## Backend and persistence

A single Go worker polls approximately five times per second with an 800 ms request timeout, bounded response size and no overlapping requests. It uses fixed `/json` GET requests, disables redirects/proxies and sends no Field Scoreboard credentials upstream. Addresses accept HTTP(S) with localhost or literal loopback/private IPs; credentials, query strings and arbitrary paths/public hosts are rejected. A pasted `/json` suffix is accepted and normalized.

Address and explicitly selected field are optional configuration settings. Connection/following state and observed times are runtime-only. Restart always starts manual/Ready, with no automatic connection or follow. Changed settings require Connect again; field/source changes are blocked while following.

Authenticated operator endpoints are `POST /api/ocr/connect` (`{"address":"http://127.0.0.1:18099"}`), `/api/ocr/field` (`{"field":"Time"}`), `/api/ocr/follow` and `/api/ocr/manual` (both `{}`). All require JSON content type; remote callers require the existing bearer header. The full operator snapshot includes connection/reading status. The read-only overlay receives only the effective match clock through its existing sanitized feed, not the OCR address, field list or warnings.

Generation checks discard in-flight results across connection, field and ownership changes. Manual takeover never waits for network I/O. OCR never repeatedly calls the existing Set/Start APIs, changes configured duration/direction or writes readings to disk.

## Evidence and remaining work

See [test.9 verification](VERIFICATION-v0.1.0-test.9.md). Live observation covers connection, changing readings, follow, takeover and restart against the running source. Source pauses/resets, rejection, missing fields and failures/recovery are separately simulated; Field Timer and the live source were not controlled by these tests.

Future work remains optional: mappings for other fields, verified detection freshness if an upstream API supplies it, field-wise confidence/stability policy, multiple-source/manual overrides and real venue evaluation. No general automatic sport rules or guaranteed OCR accuracy are included.
