# Field Scoreboard v0.1.1

Focused update to released v0.1.0 for Windows x64 and Linux x64. This build is prepared for the owner's visual test; it has not been published or accepted yet.

## Changes

- Separate large **Connect** and **Disconnect** buttons for ScoreSight. The top-right badge shows Not connected, Connecting…, Connected, Connection lost or Connection failed, with red/amber/green colors and readable text. Backend connectivity is independent of whether fields follow OCR.
- Disconnect stops polling, cancels in-flight requests and returns all followed fields to manual while retaining displayed values and pausing followed clocks. Late responses cannot overwrite values or status, even after reconnect. Address and mappings remain. Reconnecting or explicitly retrying a failed connection requires Follow OCR again; it never starts clocks. Independent manual clocks are unchanged. Duplicate pending/healthy Connect requests do not restart the worker.
- A separate full-width **Layout profiles** card below both editor columns holds Saved profile, Load, Delete, Profile name and Save preset. Existing save/load/delete behavior remains.
- Editor actions now read **Restore Defaults | Discard | Save Layout** at the top. Restore Defaults retains its existing element X/Y, font-size and transform reset scope; it does not reset match data, change the background or delete profiles. Coordinate/anchor help sits directly below X/Y and above Fine position. Free transform remains left and Edit background right.
- Desktop preview/background and Element inspector cards share their top and bottom edges using content-driven grid sizing. Narrow screens stack naturally; touch targets and selection highlighting remain large and visible.

## Install and review

Extract the Windows or Linux ZIP into a writable folder. Windows includes GUI/tray and console executables; Linux includes the CLI and portable launcher. Existing config and preset schemas remain compatible. Keep the same configuration/portable launch mode and stop the older instance before running the new one. Packages contain no runtime configuration, credentials or personal artwork.

Review screenshots cover 375/500/1000/1440/1920 px, OCR connection states and native 200%/400% zoom. See [verification](VERIFICATION-v0.1.1.md), [user guide](USER_GUIDE.md) and [OCR details](OCR_PLAN.md). Successful ScoreSight HTTP responses still do not prove camera freshness.

## Publication plan after acceptance

Publish **v0.1.1 as Latest**, verify public access and all downloaded asset hashes, then delete only the **v0.1.0 GitHub release entry and attached assets**. Preserve the v0.1.0 Git tag, commit history, local release archives and all unrelated releases. Publication and removal are pending the owner's visual acceptance.
