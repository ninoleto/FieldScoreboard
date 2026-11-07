# Field Scoreboard v0.1.0

The first normal release of Field Scoreboard, accepted by the operator. Free and open source under the MIT licence for **Windows x64 and Linux x64**. This release integrates the tested development work since the public **v0.1.0-test.8** preview and builds fresh v0.1.0 binaries.

## Complete application

- A touch-friendly local web control panel, with large choice dialogs at every width, consistent numeric steppers, full-width team-name inputs, keyboard access and mobile Menu navigation.
- Scores, fouls, periods and OT; Number/Ordinal/Quarter period display. Two independent clocks, combined Start/Pause and four immediate time corrections per clock. Match duration presets stay pending until Set. Shot 14/24/30 presets apply immediately and resume only if the match clock is internally running. Optional shot auto-hide changes visibility only.
- A logical 1920×1080 layout editor with nine scoreboard elements, fonts/colors/alignment/visibility, precise position/size controls and optional Free transform. Background Fit/Fill/Original/Stretch/Custom placement, aspect lock, explicit move/resize mode, transparency, Save/Discard and named layout presets. Shared rendering keeps saved preview and OBS geometry consistent.
- Optional ScoreSight connection with seven independent mappings: match/shot clocks, home/away scores, home/away fouls and period. Mixed manual/OCR operation, raw/accepted readings, clear connection/warning states, individual takeover, strict validation and last-value hold. Manual/API ownership guards and atomic combined/reset rejection protect followed fields. Restart retains mappings but starts manual and disconnected.
- Local and private-LAN OBS Browser Sources, authenticated remote control, token rotation, network-interface discovery and a Companion HTTP Builder. Windows GUI/tray and console binaries; Linux terminal application; portable launchers and documented backups.

## Changes since the public test.8 preview

- Added ScoreSight OCR and expanded it to seven independently controlled targets. Period recognition accepts numeric, valid ordinal and Q-prefixed values; display format remains independent and OT stays manual. Successful polling alone never establishes video freshness.
- Added transforms for all nine scoreboard elements, including actual text and foul-dot scaling, compatible optional saved properties and explicit Free transform mode. Background editing remains a separate explicit mode. Font now includes a pinned Bold switch and shows family/weight when closed.
- Refined Live control: dark OCR section always last, unmistakable connection action, immediate foul/clock display preferences with layout-draft protection, enlarged team names, clock-card organization, four matching quick adjustments, pending match presets and clearly immediate shot presets.
- Improved editor toolbar/discoverability and inspector order; retained large targets and polling-safe drafts. Fixed HTTP action-body handling that caused intermittent Windows connection resets in development, with no-retry transport regression coverage.
- Final wording cleanup: the panel under the live preview is **Foul indicators**, with one heading and **Changes appear immediately in the preview and OBS.** The approved footer remains **Field Scoreboard · Free & open source · Windows & Linux**. No other feature/design changes were made after test.17 acceptance.

## Install or upgrade

Extract the complete platform ZIP. On Windows launch `fieldscoreboard.exe`, or `start-portable.cmd` for portable storage. On Linux run `chmod +x fieldscoreboard start-portable.sh`, then `./start-portable.sh`; keep the terminal open and stop with Ctrl+C. Open `http://127.0.0.1:8790`; use `/overlay` as a 1920×1080 OBS Browser Source.

Existing configurations and presets remain compatible. Stop the old instance, back up its data, and keep the same configuration/portable launch mode. Packages contain no user configuration, credentials or imported artwork. See the [user guide](USER_GUIDE.md), [OCR guide](OCR_PLAN.md) and [Companion setup](COMPANION_SETUP.md).

## Verification and limitations

See [release verification](VERIFICATION-v0.1.0.md) for automated final-source, native-package, responsive, security and archive checks. Windows/Linux/source ZIPs and `SHA256SUMS.txt` accompany the GitHub release. The earlier public test.8 release and local development packages are preserved.

ScoreSight v0.4.3's observed JSON feed has no detection timestamp/frame heartbeat. Repeated accepted responses cannot prove fresh video; paused and frozen/cached readings may look identical. OCR accuracy/latency depends on capture and recognition. No automatic basketball/sport rules, NDI, direct OBS integration or dedicated Companion feedback are included. Linux has no tray; OBS Browser Source support depends on its installation.

User-reported 2026-11-06 Linux OBS Flatpak and home match-clock OCR smoke tests remain scoped reports. Release acceptance does not imply unperformed physical touchscreen, venue, Windows tray, separate-machine LAN, Companion hardware or real capture-failure testing. Rehearse the intended production setup.
