# v0.1.0-test.6 — Background graphic sizing and positioning

> Historical checkpoint before the first public preview. For current release and manual-test status, see [test.8 verification](VERIFICATION-v0.1.0-test.8.md).

Preview build; physical touchscreen and broadcast field validation remain pending. Nothing is published to GitHub. Field Timer is unchanged.

Imported square, portrait and banner artwork no longer defaults to a distorted 1920×1080 rectangle. New PNG/JPG/WebP imports fit proportionally and center on the canvas. The existing large choice dialog provides Fit entire image, Fill canvas, Original size and explicit Stretch to canvas. Manual geometry changes display Custom.

The Background graphic section adds large Width/Height/X/Y fields with ± buttons, original dimensions, aspect-ratio lock, Center image and Reset to fit. Select background explicitly to drag or resize with generous corner handles; scoreboard fields stay in place. Keyboard movement/resizing and numeric adjustments support precise work without dragging.

Transforms use logical canvas coordinates and persist with layouts and presets. Browser resizing/zoom cannot change saved geometry. Editor, live preview and OBS share the renderer. PNG transparency is preserved, overflow is clipped and uncovered OBS canvas remains transparent. Selection decorations never render in output.

Imports, removals and geometry edits in the editor now apply after Save layout; Discard restores the saved graphic. Existing direct upload/delete API calls remain supported. Incomplete image numeric edits survive polling/navigation and block saving until corrected. Original uploaded bytes are kept unchanged.

Existing layouts without transform metadata retain their previous stretched appearance until their background is edited. Opening, saving, resizing or restarting alone does not change them. Config schema remains v1. Upgrading does not change clocks, scores, OT, shot auto-hide, authentication, LAN output or Companion actions. All test.5 touch controls remain.

See [verification and remaining operator checks](VERIFICATION-v0.1.0-test.6.md). Packages contain portable Windows GUI/console binaries, a Linux x64 binary, or source; no external runtime is required. Each ZIP is listed in SHA256SUMS.txt.
