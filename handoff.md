# Field Scoreboard handoff

Release: **v0.1.0**, prepared from accepted test.17 commit `c7918be` on **2026-11-07**. The owner explicitly authorized normal public publication, superseding the earlier local-test restrictions. Historical test releases, verification records, packages and configuration compatibility remain intact. Field Timer was untouched.

Repository: [ninoleto/FieldScoreboard](https://github.com/ninoleto/FieldScoreboard). Release: [Field Scoreboard v0.1.0](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0). The release uses `draft=false`, `prerelease=false` and Latest. Main integrates the tested source without force-pushing; the v0.1.0 tag identifies the release source. Earlier test.8 remains available.

Read [AGENTS.md](AGENTS.md), [user guide](docs/USER_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.0.md) and [verification](docs/VERIFICATION-v0.1.0.md).

## Released behavior

- The accepted application includes manual controls, independent/combined clocks, immediate shot presets, pending match presets, seven-field ScoreSight OCR, period formats/OT, optional element Free transform, background transforms and Font-picker Bold. Preserve all existing ownership, polling-safe draft, configuration, layout-preset and HTTP transport behavior.
- The only interface cleanup after test.17 renames the foul-only panel **Foul indicators**, removes its duplicate inner heading and uses **Changes appear immediately in the preview and OBS.** Controls, placement and behavior remain. Footer: **Field Scoreboard · Free & open source · Windows & Linux**.
- Runtime/UI version is 0.1.0. Fresh Windows GUI/console and Linux binaries are built; test ZIPs are not renamed. Source packages use the explicit inventory and contain no runtime configuration, graphics, credentials or temporary test environments.
- Current guides cover startup, OBS, editing, OCR, LAN/API/Companion and development. Historical documents remain unchanged. Future features remain separate from shipped behavior; no sliders or automatic sport rules.

## Verification and delivery

Final release checks and packaging evidence are recorded in [v0.1.0 verification](docs/VERIFICATION-v0.1.0.md). Packages are Windows/Linux/source ZIPs plus `SHA256SUMS.txt`, with local copies under `releases/v0.1.0/` outside the checkout. GitHub release metadata records post-publication public/download verification without changing the tagged source or packaged documentation.

Fresh builds, Go tests/vet/Linux race, JavaScript syntax, all responsive/native UI suites, seven-field OCR/period simulations and extracted Windows GUI/console/Linux startup/API/restart checks passed. Each platform passed 1,500 transport requests without reset recurrence. Screenshots were inspected; archives passed integrity, inventory, embedded-assets, checksum, secret and documentation checks. This repeats the release regression suites against v0.1.0; hardware evidence remains separately scoped below.

## Remaining operator checks and future work

- Owner acceptance is recorded; it is not evidence of unspecified physical tests. Physical touchscreen, actual OBS on the intended production setup, Windows tray, real seven-field capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency still require operator checks.
- Preserve the scoped 2026-11-06 test.9 home match-clock OCR and test.8 Linux OBS Flatpak reports. Successful ScoreSight HTTP polling cannot prove camera freshness.
- Keep the test.10 intermittent Windows reset and test.11 reproduction/fix in history. Investigate any recurrence without retries hiding failures.
- Future work may include verified source freshness/confidence policy, multiple OCR sources and sport rules. Future publication needs separate authorization; never overwrite the v0.1.0 tag/assets.
