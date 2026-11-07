# Field Scoreboard v0.1.2

Local visual-review build for Windows x64 and Linux x64, continuing from v0.1.1 commit `52f3458`. Publication and owner acceptance are pending. The v0.1.1 checkpoint and packages are preserved.

## Background sizing

The Sizing dropdown is replaced by four large, always-visible buttons in a balanced 2 × 2 grid:

| Button | Explanation |
|---|---|
| Fit entire image | Show the whole image without stretching. |
| Fill canvas | Fill the canvas; edges may be cropped. |
| Original size | Use the image’s original pixel dimensions. |
| Stretch to canvas | Fill the canvas without preserving proportions. |

The active preset uses the established selected green color, bright border and checkmark. Manual positioning/resizing, dragging or Center image shows **Custom sizing** and clears preset highlights. Custom is a status, not a sizing action. Buttons remain visible but disabled without an imported background, and stack on narrow screens without shrinking labels.

The existing sizing calculations, aspect-ratio switch, numeric controls, Center image, Reset to fit, drag/resize and Save Layout/Discard behavior are retained. Preset selection changes only the editor draft; the live preview and OBS continue using the saved layout until Save Layout. Profiles restore the saved sizing mode, including Custom. Legacy layouts keep their stretched appearance until explicitly edited.

The aligned editor card edges, separate Layout profiles card, top actions and ScoreSight controls from v0.1.1 remain. Existing configuration/profile schemas and original image bytes are unchanged.

## Review and release plan

Fresh Windows, Linux and source ZIPs with SHA-256 checksums and updated screenshots are provided for visual testing. See [verification](VERIFICATION-v0.1.2.md) and the [user guide](USER_GUIDE.md).

After acceptance, publish **v0.1.2 as Latest**, replacing the planned v0.1.1 publication. Verify public downloads and their hashes, then remove only the **v0.1.0 GitHub release entry and attached assets**. Preserve its Git tag, history and local archives, and the local v0.1.1 checkpoint/packages. This review pass publishes or deletes no releases.
