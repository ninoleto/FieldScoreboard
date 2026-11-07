# Field Scoreboard handoff

Prepared version: **v0.1.1**, based on released v0.1.0 commit `12e81de`, on **2026-11-07**, on local branch `prepare/v0.1.1`. This is a local review build; owner visual acceptance and publication are pending. Repository: [ninoleto/FieldScoreboard](https://github.com/ninoleto/FieldScoreboard). Field Timer was untouched.

Read [AGENTS.md](AGENTS.md), [user guide](docs/USER_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [v0.1.1 notes](docs/RELEASE_NOTES-v0.1.1.md) and [verification](docs/VERIFICATION-v0.1.1.md). Historical notes/evidence remain unchanged.

## Prepared changes

- ScoreSight has separate Connect/Disconnect buttons and a backend-driven top-right status badge. `POST /api/ocr/disconnect` accepts `{}`, uses the existing authorization gate, cancels active source I/O, stops polling and invalidates the whole connection generation. All followed fields become manual with values held and followed clocks paused; independent manual clocks are unaffected. Address/mappings remain. Reconnect or explicit Connect retry requires new Follow OCR actions. Healthy/pending repeated Connect is idempotent. One worker remains; successful polling still does not establish camera freshness.
- Layout profiles is its own full-width card below aligned preview/background and inspector cards. Top actions: Restore Defaults, Discard, Save Layout. Restore Defaults retains its existing draft position/font-size/transform reset scope. Coordinate/anchor help is immediately below X/Y; Free transform stays left and Edit background right. Large touch targets, responsive stacking and selected states remain.
- Runtime/UI version is 0.1.1. User/developer guides and API details are updated. New Go/native/browser regression coverage exercises connection cancellation, retained values, explicit reconnect ownership and editor organization. Existing config/layout/profile schemas remain compatible.

## Verification and review files

Go/JavaScript, Linux race, responsive/native UI, OCR and existing clock/layout regressions passed; detailed evidence and final package checks are tracked in [verification](docs/VERIFICATION-v0.1.1.md). Review delivery is under the workspace's `releases/v0.1.1/` outside the checkout: fresh Windows/Linux/source ZIPs, SHA256SUMS.txt, screenshots and a screenshot ZIP with its own checksum. Executables use isolated test configurations; production data and personal graphics are excluded.

The only corrected historical test assumption was a live-preview gap threshold reproduced identically in v0.1.0; the application live layout was unchanged. New screenshots show desktop/narrow editor arrangements, all connection states and browser zoom. OCR/touch automation is simulated, not evidence of camera or physical touchscreen testing.

## Publication after visual acceptance

1. Obtain the owner's visual acceptance of these packages. This pass does not publish, tag or delete anything remotely.
2. Integrate accepted tested source into main without force-pushing; publish **v0.1.1 as Latest**, normal release (`draft=false`, `prerelease=false`). Never overwrite an existing tag.
3. Verify unauthenticated public access and download every attached package/checksum; compare hashes against the accepted local artifacts.
4. Only after successful public verification, delete the **v0.1.0 GitHub release entry and attached assets** as requested. Preserve its Git tag, commit history and local archives, and leave unrelated releases/assets alone. This owner-requested scoped cleanup supersedes the earlier general instruction to preserve that release entry.

README download links still target the current public v0.1.0 release during review. On accepted publication, update them to v0.1.1 before removing the old release; if documentation is repackaged, retain tested executable bytes and regenerate/verify checksums. Record public verification without rewriting tagged history.

## Remaining operator checks

Visual acceptance is pending. Physical touchscreen, Windows tray interaction, production OBS, real seven-field capture pause/reset/freeze/loss, separate-machine LAN/firewall, Companion hardware and venue accuracy/latency remain operator checks. Preserve scoped historical test.8 Linux OBS Flatpak/test.9 home OCR reports and the test.10/test.11 HTTP reset investigation. Investigate any transport recurrence without retry masking. Automatic sport rules, NDI, direct OBS control and verified video freshness remain future work.
