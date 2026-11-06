# v0.1.0-test.7 — Clear background editing and consistent numeric controls

> Historical checkpoint before the first public preview. For current release and manual-test status, see [test.8 verification](VERIFICATION-v0.1.0-test.8.md).

Focused preview build on completed test.6. No sliders were added. No GitHub publication or Field Timer changes.

- **Edit background — move & resize** is prominently beside the preview with a short explanation. Selection shows a green checked state and **Finish editing background**. Existing selection, handles, drag/resize, aspect lock and Save/Discard remain.
- All 21 numeric ± groups use the approved duration-control treatment: clearly labelled groups, 64 px controls, 28 px values, consistent borders and 10 px gaps. Desktop groups sit side by side where they fit; narrow layouts stack them. Score-increase buttons keep their green cue. Server port and Companion adjustment/period now have matching touch buttons in place of native spinners; these still wait for Save/Test. Clock correction buttons are also sized for touch.
- Scores/fouls/period keep immediate updates and the existing exact-value prompt. Their number buttons now support Enter/Space. Duration drafts remain pending until Set. Validation, limits, carry/borrow and polling protection are unchanged.

Clock logic, scores, OT, shot auto-hide, APIs/security, saved layouts/presets and all image transforms/rendering remain intact. Test.6 background manipulation was confirmed working by the operator; this build still needs operator evaluation of the new arrangement.

See [verification](VERIFICATION-v0.1.0-test.7.md) for automated results and remaining physical touchscreen, Windows tray, installed OBS and field checks. Windows GUI/console, Linux x64 and source ZIPs are supplied with SHA256SUMS.txt.
