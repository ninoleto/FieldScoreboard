# Field Scoreboard handoff

Checkpoint: **2026-11-06**, **v0.1.0-test.10**, local OCR development build.
Branch: `ocr/scoresight-match-clock`. Test.9 checkpoint `b86ef33` and its packages are preserved. Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged. **Do not publish this OCR build without a new instruction.**

Read [AGENTS.md](AGENTS.md) first. Work began from the clean completed test.9 branch; no user changes were overwritten. Field Timer remains separate and untouched.

## Completed

- Entire OCR section moved last in Live control, after every manual panel and before footer. Stable order at all widths/connection/ownership states; no automatic opening/polling focus or scroll to OCR.
- Four independent mappings: main, shot, home_score, away_score. Large source dialogs, per-target recognised/accepted values and statuses, Follow/takeover buttons; shared connection/freshness once. Suggestions only use actual matching names. Missing fields remain unconfigured/manual; explicit unconfiguration persists.
- One bounded backend poll worker (~5 Hz, 800 ms timeout). Per-field status/format/limit validation isolates invalid or duplicate data; missing/rejected/disconnected values hold instead of becoming zero. Valid zero is accepted.
- OCR-owned clocks hold effective source values without internal countdown. Takeover immediately retains the displayed value, leaves clocks paused and invalidates that target’s pending responses while others continue. Browser command epochs also reject stale poll snapshots.
- Manual/API controls respect ownership. Combined actions reject atomically if either clock follows; game reset rejects atomically if either score follows. Manual shot reset never infers running from OCR match time. Auto-hide compares both effective values.
- Saved address/mappings and changed scores; test.9 `field` config/API compatibility. Restart manual/Ready/disconnected; explicit Follow required again. Fouls/period/names remain unmapped, and layouts/presets cannot replace live values.
- Preserved authentication/public-overlay boundaries, all touch/numeric controls, Fine position 5/10/20 default 5 and X/Y ±1, background proportions/editing, Save/Discard and logical coordinates. No sliders.

## Verification and source map

See [connector guide](docs/OCR_PLAN.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.10.md) and [verification](docs/VERIFICATION-v0.1.0-test.10.md). Implementation: `ocr.go`, engine/server integration, `web/ocr.js`, bottom HTML cards and shared CSS. Regressions: `ocr_test.go`, `ocr_mappings_test.go`, `scripts/test_ocr.py`, `ocr_mapping_checks.py`, `ui_ocr_checks.py`.

Windows Go tests/vet/JS syntax and all three builds passed. Linux Go tests/vet/race and native HTTP/multi-field OCR checks passed. OCR browser checks passed at 375/500/1000/1440/1920, effective 200%/400% zoom, mixed ownership, delayed browser response, focus/scroll, drafts, dynamic dialogs and disconnected restart. Established UI/native zoom, numeric/Fine position and image regressions passed. Responsive screenshots were reviewed, including maximized 1920×1080. Final package gates are recorded in the verification document and checksum manifest.

Live ScoreSight v0.4.3 exposed Time and Home Score, but no Shot Clock or Away Score. An isolated test.10 process observed changing match time (40 samples, 10 values) and stable home score 1 (20 samples), checked independent follow/takeover and manual restart. Changing scores, shot/away readings, deliberate pauses/resets/failures and delays were simulated. No live source or Field Timer controls were changed.

**Freshness remains unavailable:** `/json` has no detection timestamp or video heartbeat. Cached success cannot establish live video. Shared guidance explains this; unchanged fields warn after three seconds. Do not add an extrapolated countdown or false “live” indicator.

## Manual evidence and next checks

- **User-reported, 2026-11-06:** test.9 match-clock OCR works in the operator’s home setup. This is not venue validation or validation of new test.10 mappings.
- Historical **user-reported, 2026-11-06:** test.8 Linux application/overlay works with OBS Flatpak. Do not extend that statement to OCR, physical touchscreen, Windows tray, LAN, Companion or live events.
- Next operator rehearsal: configure actual shot/away fields, exercise mixed ownership and individual takeover, change live scores, pause/reset/freeze the source, and inspect OBS output. Use a separate portable folder/configuration and keep manual fallback available.
- Still needed: physical touchscreen, Windows tray, test.10 OBS, separate-machine LAN/firewall, Companion hardware, venue conditions/accuracy and production latency.
- Further OCR targets, verified source freshness when supplied upstream, confidence/stability policy and automatic sport rules are future work. Preserve existing contracts and keep publication separate from local testing.
