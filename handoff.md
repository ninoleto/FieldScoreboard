# Field Scoreboard handoff

Checkpoint: **2026-11-06**, application **v0.1.0-test.8**, first public preview (prerelease).
[Repository](https://github.com/ninoleto/FieldScoreboard) · [Release](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.0-test.8)

Read [AGENTS.md](AGENTS.md) first. Publication of this preview was explicitly authorized by the owner. Field Timer remains separate and untouched. Source, licence, launchers, build/test scripts and public documentation belong in Git; binaries belong in release assets.

## Completed behavior

- Universal large choice dialogs, responsive Menu navigation, polling-safe drafts and consistent numeric ± groups at every screen size and pointer type. The separate Both clocks box preserves current times.
- Proportional imported backgrounds with Fit/Fill/Original/Stretch/Custom sizing, aspect lock, logical dimensions/position, explicit **Edit background — move & resize** / **Finish editing background**, dragging and generous corner handles. Save/Discard, profile persistence, alpha/clipping and legacy stretch compatibility remain. The owner previously confirmed test.6 background selection/manipulation. **No sliders.**
- Fine-position steps **5/10/20 px**, default **5 px**; all four directional buttons use the selected step and clamp to logical anchor bounds. X/Y ± remains **1 px**. Canvas keyboard shortcuts remain 1 px / Shift+10 px. Large styling and selected highlighting are preserved.
- Scores, fouls, OT, independent clocks, shot reset conditional resume, visual auto-hide, layout-only presets, APIs and authentication remain unchanged.

## Public-preview preparation

The completed test.8 source matched its supplied source ZIP with no additional user changes. Publication work was isolated; original source/packages were preserved. Application files and the Windows GUI, Windows console and Linux executables retain their tested bytes and version.

README now provides download/launch/OBS essentials and links to the detailed [user guide](docs/USER_GUIDE.md). Existing Companion guidance is retained; [CONTRIBUTING.md](CONTRIBUTING.md) and [architecture](docs/ARCHITECTURE.md) document build/run/test commands and actual state, rendering, persistence and API boundaries. Historical test.5–7 notes remain clearly identified as earlier checkpoints.

Packaging includes all linked documentation, uses an explicit public-source allowlist and excludes local configuration, tokens, private images, caches and temporary environments. Release checks cover document links, exact source inventory, embedded assets, ZIP integrity, binary formats, executable preservation, credential scan and fresh archive SHA-256. See the [verification record](docs/VERIFICATION-v0.1.0-test.8.md) for executed/reused evidence and [release notes](docs/RELEASE_NOTES-v0.1.0-test.8.md) for capabilities and limits.

## Evidence and manual status

Completed test.8 automation includes Windows Go tests/vet and JS syntax; Linux Go tests/vet/race; full browser regression at 375/500/1000/1440/1920 px and 200%/400% zoom; direction/boundary tests; real-server image regressions; screenshot review; extracted Windows/Linux HTTP smoke/restart; credential and archive checks. This evidence is reused for unchanged application files, not represented as newly performed hardware tests.

**User-reported manual smoke test on 2026-11-06:** the Linux application and its overlay work with OBS Flatpak. This is the full scope of that report.

Still requiring the operator:

- Physical 24-inch touchscreen usability, scrolling, numeric entry and drag/resize.
- Windows GUI/tray interaction, exit/restart and upgrade using a real production configuration.
- Installed Windows OBS, detailed image/transparency/scene-nesting checks, and separate-machine LAN OBS/firewall behavior.
- Actual Companion device/actions, token rotation and remote session behavior on the production network.
- Full live-event rehearsal, latency and sport-specific operating procedures.

Browser emulation and HTTP tests do not establish those outcomes. The Linux Flatpak smoke report does not establish LAN, Companion, tray, touchscreen or live-event validation.

## Next steps

1. Collect the remaining manual evidence and reproducible preview issues; keep verified, automated and user-reported results distinct.
2. For future changes, use the next unused test version, preserve the product contracts in AGENTS.md, rerun affected regressions and inspect responsive screenshots.
3. Rehearse with real scenes/configuration before production. OCR, automatic rules and live Companion feedback remain future work; no implementation is implied by the [OCR research plan](docs/OCR_PLAN.md).
4. A release is complete only after public repository/release access and downloads of all four assets have been verified against final local SHA-256. Record that post-publication result in the GitHub release notes; it cannot be measured inside the archives before upload.
