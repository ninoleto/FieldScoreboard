# v0.1.0-test.16 — duration presets and Font picker weight

Local development build from test.15 (`65c76c0`); do not publish. The intended public version after acceptance remains **v0.1.0**, a normal release.

- Match **Duration presets** offer **5 min / 8 min / 10 min / 12 min / 20 min** above the final full-width Set button. They fill Minutes and set Seconds to 0, without changing the live clock until **Set match clock**, even while running. The matching pending duration highlights; custom entry remains available. Direction, output format, other game values and OCR ownership stay unchanged. Set retains its OCR guard. Shot presets and both quick-adjustment rows are unchanged.
- The **Font** picker now includes a large **Bold** switch in a dedicated row that stays visible while fonts scroll. Toggling it keeps the picker open. The closed control shows family and weight, such as **Serif · Bold**. Each setting preserves the other; both edit the selected element's layout draft, using the existing Save/Discard and preset behavior. The separate Bold checkbox is removed.
- Both additions retain large targets, narrow-screen wrapping, keyboard access and polling-safe drafts. Existing clocks, seven-field OCR, dark final OCR panel, period formats, optional Free transform, display preferences and HTTP transport fix remain unchanged. No sliders.

See [verification](VERIFICATION-v0.1.0-test.16.md) and the [user guide](USER_GUIDE.md). Physical touchscreen and actual OBS acceptance remain operator work; no new live-source or venue validation is claimed.
