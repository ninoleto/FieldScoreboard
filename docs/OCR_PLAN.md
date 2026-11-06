# Field Scoreboard — OCR integration research plan (NOT implemented in v0.1)

## Purpose

Read values from a physical sports scoreboard using an existing camera feed and update only selected fields: game time, shot/possession time, period, home/away points and fouls. Target sports include futsal, basketball, and water polo. Free, offline-capable tooling only.

## Candidate

Evaluate the open-source [ScoreSight](https://github.com/royshil/scoresight) application before writing OCR from scratch. Validate actual availability of each supported video input, API schema, licence and device-shared capture on current releases before implementation. An operator may already use OBS with a dedicated scoreboard camera; avoid assuming multiple processes can open the same video capture device. Consider OBS's existing video routing where technically supported.

## Input/output architecture

`Dedicated scoreboard camera / local video feed` → `ScoreSight detection regions` → `validated event/HTTP snapshot` → `Field Scoreboard per-field inputs` → `one authoritative state` → `OBS transparent Browser Source`.

The OCR service must never have exclusive ownership of the scoreboard's clocks. OCR provides observations and confidence; manual input must always be available, especially if video feed is unavailable or the scoreboard glitches.

## Technical requirements

- Per-field source mode: **Manual**, **OCR**, **OCR with manual override**. No global forced OCR mode.
- A human can immediately force a field to manual, correcting a score without restarting the overlay.
- Validate strict grammar (`MM:SS`, `SS`, digits); cap periods/scores/fouls to plausible values; reject garbage readings.
- Use per-field stability thresholds (e.g., require repeated matching OCR samples for scores and fouls). Avoid introducing artificial delay on an actual game-clock reading; filter jitter based on game-clock direction and known expected progression.
- Mark stale values when observations age out. Hold last confirmed value; never turn a missed read into zero or blank during a live game.
- Handle shot clock reset (24/14/30) as an expected jump, but reject implausible sporadic jumps unless sustained/confirmed.
- Debounce OCR values independently; provide OCR confidence and source status in the operator UI, **not in the OBS overlay** unless explicitly configured.
- Camera setups: straight-on, manual exposure/shutter to reduce LED rolling refresh artifacts, locked focus, dedicated ROI selection per value.
- No promise of 100% accuracy. Field test at real venues under changing lighting/LED refresh rates, collect opt-in test footage only.

## Validation plan

Run ScoreSight manually on a recorded scoreboard clip. Assess field-level recognition precision, clock latency, shot clock reliability, and false changes. Only then implement a bridge. Do not depend on additional licences, cloud APIs or external equipment.
