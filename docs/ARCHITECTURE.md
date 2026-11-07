# Architecture

Field Scoreboard is one Go process with embedded browser assets. It owns the live game and serves the control panel, editor, HTTP API and transparent OBS overlay. There is no database, Node runtime, OBS plugin or external service dependency.

## Source map

| Location | Responsibility |
|---|---|
| `cmd/fieldscoreboard/main.go` | Flags, config location, listener, browser launch and shutdown. |
| `cmd/fieldscoreboard/tray_windows.go` / `tray_other.go` | Native Win32 tray; Linux terminal lifecycle. |
| `internal/scoreboard/model.go` | Schema/defaults/validation, file writes, monotonic clock model and formatting. |
| `internal/scoreboard/engine.go` | Mutex-protected game state, clock actions, snapshots and layout profiles. |
| `internal/scoreboard/display.go` / `display_test.go` | Immediate single-preference updates and stale-editor-save merge under the config mutex; no game/clock/ownership mutation. |
| `internal/scoreboard/ocr.go` / `ocr_test.go` / `ocr_mappings_test.go` / `ocr_seven_test.go` | Bounded ScoreSight polling, payload validation, runtime ownership/freshness status and regression tests. |
| `internal/scoreboard/web/ocr.js` | Touch OCR connection, actual field options, drafts, follow/takeover and operator warnings. |
| `internal/scoreboard/period.go` / `period_test.go` | Strict period OCR normalization, numeric/ordinal/quarter labels and regression tests. |
| `internal/scoreboard/background.go` | Image dimension parsing, orientation, transform defaults and validation. |
| `internal/scoreboard/network.go` | Private IPv4 interface discovery and address validation. |
| `internal/scoreboard/server.go` | Embedded files, HTTP/SSE, authentication, uploads and sanitized overlay feed. |
| `internal/scoreboard/web/app.js` / `app.css` / `index.html` | Operator panel, editor drafts, choice dialogs, numeric controls and HTTP Builder. |
| `internal/scoreboard/web/elements.js` | Editor-only optional Free transform mode, selection bounds/handles, pointer-to-logical resize, aspect lock and numeric drafts. |
| `internal/scoreboard/web/background.js` | Explicit image selection, drafts, pointer/keyboard move and resize. |
| `internal/scoreboard/web/render.js` | Shared logical-canvas layout, background placement and field rendering. |
| `internal/scoreboard/web/overlay.*` | Transparent OBS page, read-only events and reconnect behavior. |
| `*_test.go`, `scripts/test_*.py`, `scripts/ui_*_checks.py` | Engine/security/image tests, native HTTP smoke and browser regression checks. |
| `scripts/build.*`, `package.py`, `verify_packages.py`, `check_docs.py` | Cross-platform builds, clean packaging and release checks. |

## State and clock ownership

`App` protects configuration and two runtime `Clock` values with a mutex. Timing uses elapsed monotonic time, not browser animation ticks. Snapshots settle clocks and format values. The server's background loop settles expired clocks even without an overlay client.

Persisted data includes game values, durations/direction, OT, period display format, auto-hide and layout. Runtime elapsed/paused progress is not persisted: constructing a new App creates Ready clocks. Match and shot actions remain independent; combined Start/Pause is explicit. Shot Reset/Set resumes only when main is running. Shot visibility and the OT label are computed without changing clock timing or discarding the numeric period.

Explicit OCR ownership is per target: main, shot, home_score, away_score, home_fouls, away_fouls and period. Accepted clock readings write the held clock base under the same mutex; no internal countdown runs, and the snapshot identifies either owned clock as `ocr`. Scores, fouls and numeric period use existing game persistence, writing only when their numeric value changes. Manual/API controls guard the affected owner, combined actions reject before any mutation if either clock follows, and game reset rejects if any score/foul/period follows. Shot reset resumes only from the internal main running state, never an inferred OCR state. Auto-hide compares both effective values.

Numeric period updates preserve the separate `PeriodOvertime` flag; OT remains an explicit manual display toggle. Optional top-level config `period_format` is number/ordinal/quarter. Missing legacy settings normalize to number in NewApp; invalid formats are rejected. It is live presentation state, outside Layout and presets, and survives game reset. `/api/game` updates it independently of numeric period ownership. State formats `period_label` once in Go, with OT taking precedence; the shared renderer and sanitized overlay consume that label, including on transformed elements.

Period OCR alone trims surrounding whitespace and ignores case, then matches an entire numeric, correctly suffixed ordinal or Q-prefixed value in 1–20. No substring digit extraction or clamping occurs. The runtime preserves raw Recognized text and exposes canonical numeric LastAccepted for period. Display changes do not invalidate OCR ownership or mutate period values.

Takeover retains the displayed value (clocks paused). A connection generation and per-target request revisions prevent late responses crossing ownership/mapping changes, without suppressing other valid target updates. Malformed or duplicate individual fields cannot poison the whole array. One context-bound worker owns HTTP polling; timeouts never hold the state mutex. Optional config `ocr` stores address/mappings and a legacy main `field` alias. Test.9 settings migrate without automatic follow; explicit empty mappings disable suggestions. Restart is manual/Ready/disconnected. Runtime statuses stay in the authenticated operator snapshot; OBS receives only effective game/clock values. See [source contract and freshness limitations](OCR_PLAN.md).

## Embedded frontend and rendering

Go embeds `web/*`; asset changes need a new build. The operator UI polls `/api/state` every 250 ms, guards overlapping operations and keeps unfinished form/layout drafts separate from the last server snapshot. Full-state SSE exists for local consumers, but the current operator UI uses polling. OCR command epochs prevent earlier browser polls repainting state after takeover. The connection button derives its pending/red/green label from backend connection state plus the pending browser request, never field-following or source freshness. A visible explanation covers connection-change ownership locks. The whole OCR section stays last in Live control; polling does not focus or scroll it. Remote browser tokens are held in session storage and sent as headers.

The editor paints a draft layout while live preview and OBS paint the saved layout. Save commits geometry/styling; Discard restores saved geometry/styling. Five live display preferences retain their existing Layout representation for backward compatibility: foul_style_home, foul_style_away, foul_dots_max, main_clock_format, shot_clock_format. POST /api/display patches one validated preference under updateConfig without copying an editor draft. The editor merges current preferences into its draft during polling and uses PUT /api/layout?preserve_display=1; the server merges the latest five values under the same mutex, so a stale Save cannot revert a newer preference. Pending browser display writes are serialized; Save/preset actions wait for them. Dot-count input drafts remain polling-safe. Explicit preset loads and legacy full-layout PUT retain their prior complete-layout semantics, including display preferences. Position reset only changes element geometry. Preset loads replace layout without changing match data. A layout save in flight must not erase newer local edits.

`render.js` is shared by editor, preview and OBS. Coordinates are logical 1920×1080; resize/zoom only applies a presentation scale. Pointer movement is converted back into logical pixels. Scoreboard fields sit above the graphic. Background transform metadata holds width, height, X/Y, sizing mode, original dimensions and aspect lock. Missing metadata deliberately means legacy full-canvas stretch. Optional `elements[id].transform` stores `scale_x`, `scale_y` and `lock_aspect` (finite scales .05–20). Nil preserves legacy OBS geometry. The renderer scales actual text/dot content around the left/center/right anchor, with natural width/height and no fixed clipping box; values can grow while scales persist. Width/height controls convert current logical bounds to scale factors. Pointer deltas divide by the measured canvas scale, and resize anchors use the opposite side/corner. Transforms are deep-copied in snapshots/configuration and travel with layout presets. Editor borders are outside content geometry; foul-dot box sizing matches legacy OBS. Selection/resize decorations are editor-only; clipping and alpha are shared with the transparent overlay. `elements.js` owns an ephemeral Free transform flag, initially false. Normal selection/dragging keeps only a thin outline; handles and guides are hidden with no hit area or keyboard stop. The flag resets on a different selection (including background), tab departure and reload. Mode switches never call layout mutation/save/discard. Numeric controls and saved/draft scales are independent of this flag; it is absent from APIs, configuration and presets.

OBS uses `/api/overlay-events` with `/api/overlay-state` as fallback. It reconnects and hides stale graphics after roughly six seconds without data. Browser/network latency affects display delivery, not the engine's clock ownership.

## Persistence

Config schema remains version 1; optional booleans default off and optional background transforms preserve legacy appearance. `config.json` is validated before writes via a same-directory temporary file and rename. Profiles store layout JSON under `profiles/`; original uploaded bytes live under `backgrounds/` using hash-derived filenames. PNG/JPG/WebP uploads have byte/dimension limits. Names and references are validated against arbitrary filesystem access.

Editor uploads use `POST /api/background?draft=1`, staging the reference until layout Save. Existing non-draft upload and DELETE APIs change the saved background immediately. Unreferenced draft images are retained to avoid deleting preset assets. There is no automatic backup or garbage collector. See [paths and backups](USER_GUIDE.md#configuration-and-backups).

## HTTP and authentication boundaries

The default listener is loopback `127.0.0.1:8790`. Saved listener changes require process restart; `active_listen`/`restart_required` distinguish running from pending settings. `--listen` overrides only the running instance. LAN mode binds all IPv4 interfaces; selected adapter addresses are destinations for generated URLs, not binding restrictions.

| Endpoint | Access and purpose |
|---|---|
| `GET /api/health` | Public version/name status. |
| Static control UI/assets, `GET /background/<hash-name>` | Public to clients reaching the listener. Hash-named images are not secret storage. |
| `/overlay`, `/overlay.*`, `GET /api/overlay-state`, `GET /api/overlay-events` | Loopback, or permitted private/CGNAT IPv4 clients only when active listen host is `0.0.0.0`. No bearer needed; sanitized output only. |
| `GET /api/events` | Full-state SSE, loopback only, even with a remote bearer. |
| `GET /api/token`, `POST /api/token/rotate`, `GET /api/network-interfaces` | Loopback only. Rotation requires JSON content type; persists a fresh random 256-bit secret and immediately revokes the old one. |
| Other API routes below | Loopback needs no token; remote clients must provide the exact `Authorization: Bearer <token>` header. |

The common remote API gate uses constant-time bearer comparison. Client IP comes from the connection, not forwarded headers. HTTP is unencrypted and intended for a trusted LAN. Sanitized overlay data omits token, listener, restart and adapter data; static assets and images are not protected by that gate. No token belongs in an OBS URL.

| Method/path | Request / behavior |
|---|---|
| `GET /api/state` | Full snapshot; never contains the token. |
| `POST /api/game` | `{"field":"period","value":2}`; also names, scores, fouls, OT, auto-hide and `{"field":"period_format","value":"quarter"}` (number/ordinal/quarter). |
| `POST /api/adjust` | `{"field":"home_score","delta":1}`. |
| `POST /api/reset-game` | Clear scores/fouls/OT and set period to 1; leave clocks and period format unchanged. |
| `POST /api/clock/{main,shot,both}/{start,pause,stop,reset}` | Transport actions; no body. |
| `POST /api/clock/{main,shot}/set` | `{"seconds":24,"direction":"down"}`. |
| `POST /api/clock/{main,shot}/adjust` | `{"seconds":-1}`. |
| `POST /api/display` | `{"field":"foul_style_home","value":"number"}`; one of the five display keys, validated atomically. Dot maximum is an integer 1–20. Same authentication boundary as other control APIs. |
| `PUT /api/layout[?preserve_display=1]` | Validated layout object; editor flag preserves current five display preferences atomically. Omitted flag keeps legacy full-layout replacement. Neither changes live values. |
| `GET /api/profiles`, `POST /api/profiles` | List, or `{"name":"Example","action":"save"}` (`load`/`delete` also supported). |
| `POST /api/background[?draft=1]`, `DELETE /api/background` | Raw image upload / removal; draft upload returns metadata for editor Save. |
| `PUT /api/network` | `{"listen":"127.0.0.1:8790"}`; persists listener for next restart. |
| `POST /api/ocr/connect` | `{"address":"http://127.0.0.1:18099"}`; persist address and start monitoring only. |
| `POST /api/ocr/field` | `{"target":"main","field":"Time"}`; select a discovered field while that target is manual; empty field unconfigures. |
| `POST /api/ocr/follow`, `POST /api/ocr/manual` | `{"target":"main"}`; per-target follow/takeover. Targets: main, shot, home_score, away_score, home_fouls, away_fouls, period. Omitted target retains test.9 main behavior. |

JSON payloads require `Content-Type: application/json`; decoding rejects unknown fields and multiple JSON values. Image uploads use image bytes. The HTTP Builder produces supported action requests; see [Companion setup](COMPANION_SETUP.md). Security/API tests live with the server/engine tests. Preserve these boundaries and saved-config compatibility.

Bodyless clock actions, game reset and token rotation consume optional unused request bodies before state changes and replies (64 KiB maximum, 5-second read deadline), after their existing access checks. This prevents Windows connection resets with unread body bytes and `Connection: close`; empty-body/optional-body API semantics remain compatible. Regression coverage includes `action_body_test.go` and `test_http_transport.py`.
