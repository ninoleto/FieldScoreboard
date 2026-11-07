# v0.1.0-test.12 — optional element Free transform

Local development build, 2026-11-07, continuing from test.11 commit `b7d2716`. Not published. Earlier packages and the public test.8 release are preserved. After operator acceptance, the intended public version remains **v0.1.0 as a normal release**; publication needs separate authorization.

The Layout editor opens in normal mode. Select and drag any of the nine scoreboard fields to position it, with only a thin selection outline. Resize handles and their guides are hidden and cannot intercept pointer input or keyboard focus. Numeric position, size, font and aspect controls remain available; existing transforms continue rendering.

Choose the prominent **Free transform** button beside the preview to show the existing 56 px handles. Its active label is **Done transforming**. Corners resize proportionally; unlocked side handles resize width/height independently. Done, selecting another field, entering background editing, leaving Layout editor and reloading exit this temporary mode. Switching modes never saves, discards or resets draft edits. **Save layout / Discard** remains authoritative, and the background retains its separate explicit editing workflow. No sliders were added.

Seven-field OCR, its dark outer section at the bottom of Live control, HTTP action-body transport handling, clock behavior, APIs, authentication, transforms and persistence are unchanged. No new configuration fields or migrations are introduced.

See the [operation guide](USER_GUIDE.md), [verification record](VERIFICATION-v0.1.0-test.12.md) and [prior transport investigation](VERIFICATION-v0.1.0-test.11.md#windows-connection-reset-investigation). Browser automation is not physical touchscreen, tray, real OBS, LAN/Companion or venue validation. Historical home OCR and Linux OBS Flatpak reports retain their original scope.
