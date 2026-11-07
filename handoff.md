# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.12**, local development build on `ocr/scoresight-match-clock`. Started from clean test.11 commit `b7d2716`; existing source history and earlier packages are preserved. Field Timer and production configuration were untouched.

**Do not publish test.12. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) stays unchanged until a separately authorized release task.

Read [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.12.md) and [verification](docs/VERIFICATION-v0.1.0-test.12.md). Historical [test.11 evidence](docs/VERIFICATION-v0.1.0-test.11.md) remains unchanged.

## Completed change

- Element Free transform is an explicit, optional editor mode. Normal mode is the default: select and drag fields with only a thin outline. Hidden handles/guides/bounds have no hit area or keyboard stops. Numeric position, size, font and aspect controls remain available, and saved/draft transforms still render.
- The prominent 64 px Free transform button shows the existing 56 px handles, an active style and Done transforming label. Corners remain proportional by default; unlocked side handles resize independently. No sliders.
- Done, another selected element, background editing, leaving Layout editor and reload exit the mode. It is ephemeral browser state, absent from configuration/presets. Mode changes never save, discard or reset layout edits; existing Save layout / Discard remains authoritative. Background editing retains its separate explicit selection workflow.
- Shared renderer, logical coordinates, element transform schema, seven OCR targets/ownership/OT/atomic reset guards, bottom dark OCR container, clocks, APIs, authentication and the bounded HTTP action-body fix are unchanged.

## Source and verification

Focused changes are in `web/elements.js`, editor integration in `web/app.js`, button/help markup and scoped CSS. `scripts/test_elements_ui.py` covers normal and transform modes, transition/draft behavior, mouse/touch, responsive/zoom handling and shared editor/preview/OBS geometry. Application version and HTTP smoke expectation are test.12.

Windows build/tests/vet/JS syntax, Linux tests/vet/race, full offline UI/background regressions and focused all-nine element tests passed. New checks cover clean/dirty switches, hidden hit areas, default/reload behavior, Save/Discard in transform mode and preserved numeric drafts. Seven-field OCR/browser regressions passed. Actual test.11/test.12 overlay screenshots were pixel-identical in three compatibility scenarios. Extracted Windows/Linux binaries passed native HTTP, OCR/restart and 1,500-request transport checks per platform without recurrence of the historical reset. Final archives passed integrity/hash/inventory/secret checks and include the updated documentation. See the verification record for evidence boundaries.

The test.10 intermittent Windows reset and test.11 reproduction/fix remain in their historical verification records. Never hide any recurrence with retries. Test.11 live ScoreSight observations and scoped 2026-11-06 user reports are retained as history; they are not new test.12 live or venue evidence.

## Next steps and manual checks

- Operator acceptance of normal selection/dragging and optional Free transform on the physical touchscreen, plus actual OBS output using a separate portable configuration.
- Still required: Windows tray, real seven-field OCR/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency. The prior home OCR and Linux OBS Flatpak reports do not cover these checks.
- After explicit acceptance, prepare **v0.1.0 normal release** with refreshed version/docs, verified packages/checksums and separately authorized publication. Do not publish this local development build or create another public test/prerelease by default.
- Optional future work remains detection freshness/confidence policy, multiple OCR sources and automatic sport rules. Preserve manual fallback, image proportions/backwards compatibility, polling-safe editing and authentication boundaries.
