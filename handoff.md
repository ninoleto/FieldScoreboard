# Field Scoreboard handoff

Version **v0.1.2**, 2026-11-07. Repository: [ninoleto/FieldScoreboard](https://github.com/ninoleto/FieldScoreboard). Release: [Field Scoreboard v0.1.2](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.2). The owner accepted the interface at `e9f19cdc2e1dd2b9942dc94010422a043d736a16`, reported **Linux test PASSED** and explicitly authorized publication as the normal Latest release. Final publication changes documentation and ZIP permission metadata only; application source, launchers and tested executable bytes remain unchanged. Field Timer was untouched.

Read [AGENTS.md](AGENTS.md), [user guide](docs/USER_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [release notes](docs/RELEASE_NOTES-v0.1.2.md) and [verification](docs/VERIFICATION-v0.1.2.md). The [original review evidence](docs/VERIFICATION-v0.1.2-review.md) is a historical record and its review-stage status is superseded by the acceptance above.

## Included behavior

- ScoreSight has independent Connect/Disconnect controls and a text/color backend status badge. Disconnect cancels polling/in-flight I/O, returns followed fields to manual with values retained and leaves owned clocks paused. Address/mappings persist; reconnect never restores ownership or starts clocks. Successful HTTP polling cannot prove camera freshness.
- The editor has top Restore Defaults, Discard, Save Layout actions, coordinate help beneath X/Y, Free transform left and Edit background right, aligned desktop card edges and a separate Layout profiles card below. Reset scope is unchanged.
- Background Sizing uses four visible Fit/Fill/Original/Stretch buttons with explanations and green selected border/checkmark. Manual adjustments show Custom sizing with no preset selected. Aspect lock, numeric controls, Center/Reset, gestures, draft Save/Discard, profiles and shared saved preview/OBS geometry are preserved. Narrow screens stack large targets.

## Startup and configuration

Windows: extract the complete ZIP into a writable folder, then double-click `fieldscoreboard.exe`; exit through its tray menu. Use `start-portable.cmd` for data beside the executable.

Linux: from the extracted application directory:

```bash
chmod +x start-portable.sh fieldscoreboard
./start-portable.sh
```

Sudo is unnecessary. The terminal stays open while the app runs; Ctrl+C stops it. The interface is at http://127.0.0.1:8790. Linux has no tray. Portable launchers use the extracted folder's config; direct executables use the user config directory unless `--config` is supplied. Upgrades must retain the launch mode/path and `config.json`, `profiles/`, `backgrounds/` together. See the guide for exact locations.

## Release and retention

The final release is integrated into main without force-pushing and tagged `v0.1.2`; normal release flags are draft=false/prerelease=false, with Latest selected. The final source ZIP must agree with that commit and platform documentation. Final packages/checksums and publication receipts live under the workspace's `releases/v0.1.2-published/`; original review files remain in `releases/v0.1.2/`. Keep `prepare/v0.1.1` at `52f3458` and `prepare/v0.1.2` at `e9f19cd`.

The owner's current removal authorization covers **all older GitHub releases and attached assets in ninoleto/FieldScoreboard**, including tests/prereleases, superseding the earlier v0.1.0-only plan. Removal follows successful unauthenticated download/hash verification and main/tag/source agreement. Preserve full release/asset metadata and all attached assets in the local GitHub archive first; retain all Git tags, history and existing local release archives. Initial remote inventory contained v0.1.0 and v0.1.0-test.8. The local publication receipt and release-page verification record report the final outcome; do not infer future cleanup authorization from this one-time operation. Other repositories are out of scope.

## Verification boundaries

The accepted interface and owner-reported Linux PASS are recorded accurately. Reuse the historical Go/vet/Linux race, responsive/zoom, OCR/clock/layout and native-package tests only for the identical application/executable bytes. Final documentation/archive/link/permission checks and public download verification are separate publication checks.

No additional physical touchscreen, Windows tray, production OBS, venue OCR or live-video freshness, separate-machine LAN/firewall or Companion hardware pass is claimed. Historical test.8 Linux OBS Flatpak/test.9 home OCR reports remain scoped reports. Preserve the test.10/test.11 HTTP reset investigation and never hide transport failures with retries. Automatic sport rules, NDI, direct OBS control and verified video freshness remain future work.
