# test.9 verification — 2026-11-06

## Scope and starting point

Started from clean published test.8 commit `ca813da60d9d2fc295ca46766d115c990922c58e`. Created the separate local branch `ocr/scoresight-match-clock`. No original user edits were present. Published repository main/tag/release and test.8 packages remain unchanged; this build is not published.

## Live observations

Read the running ScoreSight v0.4.3 endpoint directly. `GET /json` returned an array with a single field named `Time`, text in MM:SS, a detection state and rectangle coordinates. Both `Success` and `SameNoChange` were observed. Responses have no detection/frame timestamp or heartbeat; HTTP Date/no-cache headers do not establish source freshness.

A native Windows test.9 process used its own temporary configuration and loopback port. It connected to the live source, selected Time, followed readings and took manual control. Over 40 observations at 200 ms spacing, nine distinct match times were observed. Takeover retained a paused value while monitoring continued; unrelated game/shot fields stayed unchanged. Restart retained settings but returned manual/Ready and disconnected.

The setup was reported as OBS Virtual Camera displaying Field Timer. The test read ScoreSight only; it did not manipulate Field Timer, pause/reset the real source, inspect the video visually or claim a physical OBS/touchscreen test.

## Simulated regression coverage

- Strict time parsing, accepted/rejected/empty/unknown detection states, valid zero, malformed/oversize/duplicate JSON fields and bounded source addresses.
- Connect/check without changing clocks, Time default, dynamic field discovery/selection and source/field changes.
- Accepted time progression, repeated paused readings, reset jumps, missing field, malformed text, HTTP loss and recovery without clearing the last value.
- Manual takeover during an in-flight request; generation-based late-result rejection; no automatic following after recovery/takeover or restart.
- Internal time remains held during follow; manual transport/Set/adjust and combined controls cannot bypass ownership. Explicit manual Start works after takeover.
- Scores/fouls/names/period/shot values unchanged by OCR; independent shot controls and auto-hide use effective match time, including count-up remaining duration.
- Repeated cached responses do not reset the value-change age or establish video freshness.
- Poll serialization, request timeout, shutdown and no upstream bearer header; remote OCR mutations require existing authentication, JSON is required and sanitized overlay data omits OCR metadata.
- Native HTTP/Chromium checks at 375/500/1000/1440/1920 px: actual field options, large dialog, Escape/focus restoration, keyboard/touch controls, disabled states, address drafts across polling/navigation, unique IDs and no overflow.
- Existing full UI suite: 21 numeric groups, Fine position directions/bounds, drafts, all pages, mouse/emulated touch, keyboard and 200%/400% zoom.
- Background regression with square/portrait/banner/1920×1080 PNG/JPG/WebP, shared rendering, aspect lock, legacy layouts, profiles and Save/Discard.

Automated result details and final package checks are recorded after the release gates below. Local screenshots and raw logs are excluded from archives.

## Remaining manual checks

Physical 24-inch touchscreen operation; native Windows tray interaction; real OBS display of the new OCR output; deliberately pausing/resetting the real source; disconnecting/freezing actual capture hardware; remote LAN/Companion devices; field accuracy and latency during a live event.

The earlier **user-reported Linux application/overlay smoke test with OBS Flatpak on 2026-11-06** belongs to test.8. It is not new validation of this OCR build.

## Executed results

| Check | Result |
|---|---|
| Windows Go tests/vet and JavaScript syntax; Windows GUI/console + Linux amd64 builds | PASS |
| Final Linux Go tests/vet and race detector | PASS |
| Full existing offline UI, touch/mouse/keyboard and 200%/400% zoom | PASS |
| Real-server background/image regression | PASS |
| New native OCR simulated regression on extracted Windows and Linux binaries | PASS |
| OCR browser controls and geometry at all five widths | PASS |
| Narrow/desktop OCR panel screenshots and maximized 1920×1080 review | PASS |
| Existing extracted Windows/Linux HTTP smoke and restart | PASS |
| Live ScoreSight connection/follow/takeover observation | PASS within the scope above |
| Source/document links, archive CRC/SHA-256, executable formats and embedded assets | PASS |
| Exact source and expanded archive secret scans | PASS; no leaks found |

Linux checks ran in an isolated Alpine 3.22.8 amd64 VM with Go 1.24.13; Windows used Go 1.27.3, Node 24.18.0 and Chrome/Playwright. Windows native HTTP tests use the console executable; GUI/tray interaction is still manual-pending.

The final documentation-only packaging pass retains the tested executable bytes. The separate release folder contains Windows, Linux and source ZIPs plus `SHA256SUMS.txt`; no local configurations, source credentials, personal graphics, logs or temporary environments are included. Published test.8 archive hashes were compared and remain unchanged. No GitHub publication was performed for test.9.
