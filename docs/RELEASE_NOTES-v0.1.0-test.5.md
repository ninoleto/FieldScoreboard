# Field Scoreboard v0.1.0-test.5

> Historical checkpoint before the first public preview. For current release and manual-test status, see [test.8 verification](VERIFICATION-v0.1.0-test.8.md).

Touch interface test build, based on v0.1.0-test.4. Not published to GitHub. Field Timer is unchanged.

- Every dropdown opens the approved centered choice dialog, including on a maximized desktop with a mouse. All 11 selectors, saved profiles and detected adapters use 60px rows, 18px text, clear selection and a 64px Close control. Finger scrolling, mouse, keyboard navigation, Escape, outside dismissal and focus restoration are supported.
- Narrow screens show Menu and the current page name. Navigation choices are vertical, mark the active page, close after selection and preserve unsaved forms. Desktop tabs remain where they fit.
- Minutes and Seconds have separate groups with 64px minus/number/plus controls, 28px numerals and visible gaps. Narrow layouts stack the groups, Direction and Set match clock. Shot duration uses the same control sizing.
- Both clocks has its own box above the individual panels with the requested explanation and 72px Start both / Pause both buttons. Their existing transport actions retain the current times. Independent clock controls and shot reset behavior remain.

Production Go clock logic, config schema, shot auto-hide, OT, layout coordinates, authentication, OBS assets and Companion API routes are retained. Apart from the release version, backend Go source is identical to test.4. No config migration or reset is required. Restart still puts clocks in Ready.

See [verification details](VERIFICATION-v0.1.0-test.5.md) for automated evidence and test environments. Physical touchscreen use, native tray interaction, installed OBS and separate-machine field checks remain operator-pending.

Extract a fresh package directory for testing. Keep your existing config/data folder and any imported graphics. Use the same configuration path when testing an upgrade. `start-portable.cmd` / `start-portable.sh` use the package directory's config; they do not automatically find another portable installation's data.
