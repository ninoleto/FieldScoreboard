# v0.1.2 release verification

Date: 2026-11-07. The owner accepted the interface at checkpoint `e9f19cdc2e1dd2b9942dc94010422a043d736a16`, reported **Linux test PASSED**, and explicitly authorized normal Latest publication and removal of all older GitHub release entries/assets after verifying the replacement. This report does not establish additional physical touchscreen, venue OCR or OBS testing.

## Accepted application and reused evidence

Publication changes documentation and ZIP permission metadata only. Go, embedded HTML/CSS/JavaScript, launchers and runtime behavior match the accepted checkpoint. Windows GUI/console and Linux executable bytes match the accepted review packages. No redesign or feature change was made.

The [historical review verification](VERIFICATION-v0.1.2-review.md) records the actual automated runs: Windows Go tests/vet and JavaScript syntax, Linux Go tests/vet/race under Alpine x64 emulation, offline UI and native background/display/elements/font/clock/team-name suites, simulated seven-field OCR, extracted Windows GUI/console and Linux HTTP smoke tests, and 1,500 connection-close action responses without retries on each OS. These runtime results are reused for identical application source/executable bytes; they are not described as new physical or runtime tests in this documentation and packaging publication pass.

Review checks covered all four sizing modes with portrait/landscape PNG/JPG/WebP images, Custom transitions, aspect locking, Save/Discard, profile restoration, draft isolation from saved preview/OBS, desktop panel alignment, 375/500/1000/1440/1920 px, emulated touch, keyboard and native 200%/400% browser zoom. The accepted 31 screenshots and original review archives remain local and unchanged.

## Final release checks

Windows-created ZIP entries previously carried a DOS host marker despite Unix permission bits. The packager now sets the Unix host marker explicitly for portable permission metadata. The archive verifier checks executable bits and that marker for Linux executables/shell scripts, plus LF-only shell-script bytes. Application and launcher contents remain identical.

Final packaging checks passed: ZIP integrity, regenerated SHA-256, source allowlist/content identity, embedded assets, x64 executable formats/Windows subsystems, Linux executable permission metadata and LF-only shell scripts. All 117 relative documentation links/anchors passed. Expanded-archive Gitleaks found no leaks, and personal-path/data checks passed. Platform ZIPs contain the final documentation with unchanged accepted executables/launchers. Existing local archives matched their pre-publication hash manifest. Before upload, every source ZIP file is also compared byte-for-byte with the final release commit; the publication receipt records that commit.

Public verification is recorded on the [v0.1.2 release page](https://github.com/ninoleto/FieldScoreboard/releases/tag/v0.1.2) and in the local publication receipt after upload: unauthenticated downloads of all four assets, byte/hash matches, normal Latest metadata and agreement of main, tag and source ZIP. This document does not pre-claim network checks performed after the release commit was created.

## Retention and evidence boundaries

The accepted v0.1.1/v0.1.2 checkpoints and all local archives are preserved. The owner authorized removal of **all older releases in ninoleto/FieldScoreboard**, including test/prerelease entries, only after replacement verification. Preserve their full metadata and attached assets locally before deletion. Retain every Git tag and all commit history; other repositories are outside this authorization. The final local receipt records the removed release names and preserved tag refs.

Browser touch is emulated and automated OCR sources are simulated. No additional physical touchscreen, Windows tray interaction, production OBS, venue OCR/video freshness, separate-machine LAN/firewall or Companion hardware pass is claimed. Historical test.8 Linux/OBS Flatpak and test.9 home OCR reports retain their original scope. Successful ScoreSight polling still does not prove camera freshness.
