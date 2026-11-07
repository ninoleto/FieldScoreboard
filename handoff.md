# Field Scoreboard handoff

Checkpoint: **2026-11-07**, **v0.1.0-test.13**, local development build on `ocr/scoresight-match-clock`, starting from clean test.12 commit `c142d53`. Earlier source history/packages and production settings are preserved. Field Timer was untouched.

**Do not publish test.13. After user acceptance, the intended public version is v0.1.0 as a normal release, not another public test/prerelease.** Published [test.8](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8) remains unchanged until separately authorized publication.

Read [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0-test.13.md) and [verification](docs/VERIFICATION-v0.1.0-test.13.md). Historical verification files remain intact.

## Completed change

- Large single-choice **Period format** buttons beside Period / half and OT: Number, Ordinal, Quarter, defaulting to Number for existing settings. Narrow layouts stack buttons; keyboard arrows/Home/End and Enter/Space work. Format changes apply immediately without altering the number or ownership.
- Period OCR normalizes full numeric, correct ordinal and Q-prefixed values to 1–20, ignoring case/surrounding whitespace only for period. Invalid suffixes/text/ranges are rejected without clearing/clamping. Other targets retain strict parsing. The card preserves raw Recognised value and shows canonical Last accepted period (number).
- Top-level config `period_format` persists independently of Layout/presets. Numeric API/Companion/exact/± behavior remains compatible. Game reset preserves the format. Go generates one label for editor, preview and sanitized OBS state; transformed fields keep their scales/anchors. Ordinals include 11th/12th/13th.
- OT overrides the label without losing number/format; turning it off reveals the current number in the selected format. OCR never toggles OT. Seven-field ownership, atomic reset guards, late-response protection and manual restart remain intact.
- Test.12 optional Free transform, the bottom dark OCR section, touch controls, polling-safe editing, clocks, authentication, background proportions and the HTTP transport fix are preserved. No sliders.

## Source and verification

`period.go` owns parsing/labels; model/engine add the optional persisted display setting and snapshot value. `ocr.go` keeps raw Recognized and normalizes period LastAccepted. UI integration uses the existing `/api/game` action boundary and polling epoch protection. `period_test.go`, `period_checks.py` and `ui_period_checks.py` extend the existing OCR test runner.

Go tests/vet, Linux race, JavaScript/build checks, native simulated period/OCR tests, full offline UI and all-nine element/background regressions passed. Focused period controls/OT/transformed geometry passed at all five widths with mouse/emulated touch/keyboard; screenshots were inspected. Test.12/test.13 legacy overlay screenshots were pixel-identical in three scenarios. Extracted Windows/Linux packages passed HTTP, OCR/period/restart and 1,500-request transport checks per platform with no recurrence of the historical reset. Archives passed integrity, inventory, embedded-asset, checksum and secret checks; final documentation-only repackaging retained tested executables. See the verification record for exact evidence and remaining operator checks.

Live ScoreSight exposed Period 3rd with SameNoChange. An isolated test.13 observed it 15 times in each format, displaying 3 / 3rd / Q3; OT, takeover and restart passed while other fields stayed manual/unchanged. Time was absent. These stable observations do not establish capture freshness or venue validation. Changing periods/failures were simulated.

## Remaining checks and next steps

- Operator acceptance on the physical touchscreen and actual OBS, especially formatted/transformed periods, OT and mixed OCR/manual use, using a separate portable configuration.
- Windows tray, real seven-field changes/capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain unverified by automation. Preserve the scoped 2026-11-06 test.9 home OCR and test.8 Linux OBS Flatpak reports.
- Keep the test.10 intermittent connection reset and test.11 reproduction/fix in history; investigate any recurrence without hiding failures with retries.
- After acceptance, prepare **v0.1.0 normal release** with refreshed version/docs and separately authorized publication. Do not publish this build or create another public test/prerelease by default.
- Future optional work remains verified source freshness/confidence policy, multiple OCR sources and automatic sport rules. Preserve manual fallback, compatibility and authentication boundaries.
