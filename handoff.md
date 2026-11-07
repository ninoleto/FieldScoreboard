# Field Scoreboard handoff

Prepared version: **v0.1.2**, continuing from local v0.1.1 commit `52f3458ae7a7e774de6d16d3c6135a07274a83da`, on **2026-11-07**, branch `prepare/v0.1.2`. This is a local visual-review build; acceptance/publication are pending. Repository: [ninoleto/FieldScoreboard](https://github.com/ninoleto/FieldScoreboard). Field Timer was untouched.

Read [AGENTS.md](AGENTS.md), [user guide](docs/USER_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [v0.1.2 notes](docs/RELEASE_NOTES-v0.1.2.md) and [verification](docs/VERIFICATION-v0.1.2.md). Historical release notes/evidence remain unchanged.

## v0.1.2 changes

- Background Sizing is four always-visible buttons: Fit entire image, Fill canvas, Original size and Stretch to canvas. Each includes its requested explanatory text. Desktop uses a balanced 2×2 grid; narrow screens stack readable large targets. Selection uses the existing green color, border and checkmark.
- Buttons call the unchanged background preset handler and shared sizing calculations. Their pressed state reflects the draft mode. Manual positioning/resizing or Center image shows Custom sizing with no selected preset; Custom is a status, not another action. No hidden sizing select remains.
- Aspect lock/numeric controls stay below; Center image, Reset to fit, explicit background drag/resize, import/removal, legacy stretch, Save Layout/Discard and profiles retain their behavior. The editor displays drafts; live preview/OBS keep the saved layout until Save Layout. Both desktop editor cards still share top/bottom edges, with Layout profiles separately below.
- Runtime/UI and current documentation now use 0.1.2. Tests cover all four presets and Custom transitions with portrait/landscape images, aspect locking, save/discard/profile restoration, saved preview/OBS geometry, touch/keyboard, small screens and zoom. Fresh binaries/packages are built, not renamed v0.1.1 artifacts.

## Preserved v0.1.1 behavior and checkpoint

Keep `prepare/v0.1.1` at `52f3458` and all local `releases/v0.1.1/` files. The release-file hash manifest verifies earlier archives are unchanged. ScoreSight Connect/Disconnect, cancellation/generation safeguards, retained values, paused owned clocks and explicit following after reconnect remain unchanged. Successful polling still does not prove camera freshness. Top editor actions remain Restore Defaults, Discard, Save Layout with the same reset scope; coordinate help and toolbar order remain.

## Review delivery

Review files live under the workspace's `releases/v0.1.2/` outside the checkout: Windows/Linux/source ZIPs, SHA256SUMS.txt, updated screenshots and screenshot ZIP/checksum. Packages exclude runtime settings, credentials, caches and personal graphics. Tests use isolated configurations and generated artwork. See [verification](docs/VERIFICATION-v0.1.2.md) for final automated evidence and limitations.

## Publication after acceptance

1. Await the owner's visual acceptance. This review pass publishes, tags or deletes nothing remotely.
2. Integrate accepted source into main without force-pushing and publish **v0.1.2 as Latest**, normal release (`draft=false`, `prerelease=false`). This supersedes the planned v0.1.1 publication; preserve its local checkpoint/packages.
3. Verify unauthenticated public access and download every replacement asset; compare SHA-256 against accepted artifacts.
4. Only after successful public verification, delete the **v0.1.0 GitHub release entry and attached assets**. Preserve its Git tag, history and local release archives, and leave unrelated releases alone.

README download links still target public v0.1.0 during review. Update them to v0.1.2 for accepted publication before deleting the old release entry. If documentation is repackaged, retain tested executable bytes and regenerate/verify checksums. Never rewrite tagged history.

## Operator checks

Visual acceptance is pending. Physical touchscreen, Windows tray, production OBS, real seven-field capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain operator checks. Historical test.8 Linux OBS Flatpak/test.9 home OCR reports remain scoped reports. Preserve the test.10/test.11 HTTP reset investigation and do not hide transport failures with retries. Automatic sport rules, NDI, direct OBS control and verified video freshness remain future work.
