# Architecture

Field Scoreboard is one Go process with embedded browser assets. It owns the live game and serves the control panel, editor, HTTP API and transparent OBS overlay. There is no database, Node runtime, OBS plugin or external service dependency.

## Source map

| Location | Responsibility |
|---|---|
| `cmd/fieldscoreboard/main.go` | Flags, config location, listener, browser launch and shutdown. |
| `cmd/fieldscoreboard/tray_windows.go` / `tray_other.go` | Native Win32 tray; Linux terminal lifecycle. |
| `internal/scoreboard/model.go` | Schema/defaults/validation, file writes, monotonic clock model and formatting. |
| `internal/scoreboard/engine.go` | Mutex-protected game state, clock actions, snapshots and layout profiles. |
| `internal/scoreboard/ocr.go` / `ocr_test.go` | Bounded ScoreSight polling, payload validation, runtime ownership/freshness status and regression tests. |
| `internal/scoreboard/web/ocr.js` | Touch OCR connection, actual field options, drafts, follow/takeover and operator warnings. |
| `internal/scoreboard/background.go` | Image dimension parsing, orientation, transform defaults and validation. |
| `internal/scoreboard/network.go` | Private IPv4 interface discovery and address validation. |
| `internal/scoreboard/server.go` | Embedded files, HTTP/SSE, authentication, uploads and sanitized overlay feed. |
| `internal/scoreboard/web/app.js` / `app.css` / `index.html` | Operator panel, editor drafts, choice dialogs, numeric controls and HTTP Builder. |
| `internal/scoreboard/web/background.js` | Explicit image selection, drafts, pointer/keyboard move and resize. |
| `internal/scoreboard/web/render.js` | Shared logical-canvas layout, background placement and field rendering. |
| `internal/scoreboard/web/overlay.*` | Transparent OBS page, read-only events and reconnect behavior. |
| `*_test.go`, `scripts/test_*.py`, `scripts/ui_*_checks.py` | Engine/security/image tests, native HTTP smoke and browser regression checks. |
| `scripts/build.*`, `package.py`, `verify_packages.py`, `check_docs.py` | Cross-platform builds, clean packaging and release checks. |

## State and clock ownership

`App` protects configuration and two runtime `Clock` values with a mutex. Timing uses elapsed monotonic time, not browser animation ticks. Snapshots settle clocks and format values. The server's background loop settles expired clocks even without an overlay client.

Persisted data includes game values, durations/direction, OT, auto-hide and layout. Runtime elapsed/paused progress is not persisted: constructing a new App creates Ready clocks. Match and shot actions remain independent; combined Start/Pause is explicit. Shot Reset/Set resumes only when main is running. Shot visibility and the OT label are computed without changing clock timing or discarding the numeric period.

With explicit OCR ownership, accepted readings write the held match-clock base under the same mutex; no internal countdown runs. The snapshot identifies main state as `ocr`. Manual match/combined transport, Set and adjustment are blocked until takeover; the shot clock stays independent. Auto-hide uses the held effective match value. Takeover keeps it paused. A generation check discards requests begun before ownership/source changes. One context-bound worker owns HTTP polling; timeouts never hold the state mutex. Restart connects/follows nothing automatically. Optional config `ocr` stores address/field only; runtime status is exposed to authenticated operators, omitted from sanitized OBS payloads. See [source contract and freshness limitations](OCR_PLAN.md).

## Embedded frontend and rendering

Go embeds `web/*`; asset changes need a new build. The operator UI polls `/api/state` every 250 ms, guards overlapping operations and keeps unfinished form/layout drafts separate from the last server snapshot. Full-state SSE exists for local consumers, but the current operator UI uses polling. Remote browser tokens are held in session storage and sent as headers.

The editor paints a draft layout while live preview and OBS paint the saved layout. Save commits only layout; Discard restores the saved version. Preset loads replace layout without changing match data. A layout save in flight must not erase newer local edits.

`render.js` is shared by editor, preview and OBS. Coordinates are logical 1920×1080; resize/zoom only applies a presentation scale. Pointer movement is converted back into logical pixels. Scoreboard fields sit above the graphic. Background transform metadata holds width, height, X/Y, sizing mode, original dimensions and aspect lock. Missing metadata deliberately means legacy full-canvas stretch. Selection/resize decorations are editor-only; clipping and alpha are shared with the transparent overlay.

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
| `POST /api/game` | `{"field":"period","value":2}`; also names, scores, fouls, OT and auto-hide. |
| `POST /api/adjust` | `{"field":"home_score","delta":1}`. |
| `POST /api/reset-game` | Clear scores/fouls/OT and set period to 1; leave clocks unchanged. |
| `POST /api/clock/{main,shot,both}/{start,pause,stop,reset}` | Transport actions; no body. |
| `POST /api/clock/{main,shot}/set` | `{"seconds":24,"direction":"down"}`. |
| `POST /api/clock/{main,shot}/adjust` | `{"seconds":-1}`. |
| `PUT /api/layout` | Validated layout object, leaving live values alone. |
| `GET /api/profiles`, `POST /api/profiles` | List, or `{"name":"Example","action":"save"}` (`load`/`delete` also supported). |
| `POST /api/background[?draft=1]`, `DELETE /api/background` | Raw image upload / removal; draft upload returns metadata for editor Save. |
| `PUT /api/network` | `{"listen":"127.0.0.1:8790"}`; persists listener for next restart. |
| `POST /api/ocr/connect` | `{"address":"http://127.0.0.1:18099"}`; persist address and start monitoring only. |
| `POST /api/ocr/field` | `{"field":"Time"}`; select a discovered field while manual. |
| `POST /api/ocr/follow`, `POST /api/ocr/manual` | `{}`; explicit match-clock ownership / immediate paused takeover. |

JSON payloads require `Content-Type: application/json`; decoding rejects unknown fields and multiple JSON values. Image uploads use image bytes. The HTTP Builder produces supported action requests; see [Companion setup](COMPANION_SETUP.md). Security/API tests live with the server/engine tests. Preserve these boundaries and saved-config compatibility.
