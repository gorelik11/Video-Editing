# Local qualification — 2026-11-09

Root: `/Volumes/Project 1/Video/Hermes Video Workspace/resolve-skill-qualification-20261109/`.

## Scope and actual evidence

Resolve `21.1.1.10` native scripting plus installed samuelgursky MCP v4.15.2, local Python and ffmpeg. `PRODUCT_READBACK.json` independently records `GetProductName() = DaVinci Resolve Studio` and the version. Installed documentation was read at `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/DaVinciResolveScript.pyi`; `INSTALLED_API_CURVE_NOTES.txt` preserves its `ApplyGradeFromDRX` signature and modes: 0=No keyframes, 1=Source Timecode aligned, 2=Start Frames aligned. Those other keyframe modes were not tested. Native built-in MCP was not connected/tested. No paid search/video/model API used; Claude Code consultation is the operator-authorized account route, not claimed free computation. No user footage sent to Claude. Original state: project `No More Blues Magda Multicam 20261102-213037`, timeline ID `eeb68b95-3854-4b61-bdc2-76e6fe61ddc1`, Color, `00:00:15:07`, 3 timelines. All mutation tests use `_skill_qualification_20261109_synthetic_v1` and generated media. User project was saved/exported as `ORIGINAL_BEFORE.drp`, never rebuilt/regraded; each runtime phase restores exposed state (project/timeline/page/playhead). Backups can contain private media paths: keep local.

Evidence files in root:
- `BASELINE.json`: read-only native version/settings/clip graph inventory. Original has 5 video items, one Color node each, no current Fusion comps. This does NOT invalidate earlier Fusion work on earlier versions/timelines.
- `MCP_READONLY.json`: actual SDK initialize/list_tools and 3 read-only calls. 37 compound tools; explicit item graph targeting. Server's own read verification is labelled unverified, not overruled by its success field.
- `SANDBOX_TESTS.json`: 23 PASS, 2 initial assertion FAIL; no fatal. Failures checked `bool(Fusion.SetInput(...))`; direct readback later proved writes succeeded. Original failures retained.
- `CURVE_LIVE_TESTS.json`: 9 PASS. Both gamma and TextPlus verified by GetInput although setter returned None; comp export works. Native Color graph imported from generated identity/raised DRX: 2 nodes with expected labels and Custom Curves tool.
- `YOUTUBE_WORKFLOW_TESTS.json`: 7 PASS. Distinct alternate timeline; empty-interval check; QTRLE alpha asset imported at V2 frame 0–30; occupied/stale plan rejection; audio track disabled/read back; render complete. Fingerprint guard covers the small synthetic picture edit, not every audio/property change and not an atomic lock.
- `FINAL_MEDIA_QA.json`: 7 PASS. All 3 actual renders fully decode, have 30 video frames at 640×360, no audio. Rendered curve center code mean changes 124.7→147.1 (relative effect, not exact spline calibration); overlay MAE inside expected rectangle≈82.18 vs outside≈0.00019. QTRLE asset is argb. CDL still changes actual codes; node bypass restores the original PNG exactly. Numeric QA is not visual artistic approval or listening. Track-disable was verified by API readback only: all renders explicitly used ExportAudio=False, so absent audio streams do not prove the mute affects rendered audio. Overlay locality does not independently qualify straight/premultiplied interpretation or edge quality.

## Frame boundaries and provenance checks

`FRAME_BOUNDARY_SOURCE_QA.json` independently decodes 90 frames in each original ramp.mov/testsrc.mov source (3 seconds, 30 fps), versus the requested 0..30 range and actual 30-frame appended items. This excludes the reviewer's proposed source-end-clamping alternative for these clips. Overlay input is only 30 frames; its boundary result is NOT used to establish source range semantics. Render in/out was checked separately.

Earlier settling and selected-item warnings come from `/Volumes/Project 1/Video/Hermes Video Workspace/no-more-blues-magda-multicam/SCOPES_ACCESS_REPORT.md` lines 19–22, plus `read_resolve_scopes.py`. These are our prior local report, not newly reproduced stale-frame failures in this qualification. MCP_READONLY.json records item_index=0/track_index=1 for the first item, and server.py's graph/timeline_item_color documentation plus installed .pyi document the index domains; source evidence is distinct from exhaustive boundary testing.

`ORIGINAL_STATE_COMPARISON.json` compares before/after exposed settings, IDs, intervals and node-tool summaries: all equal. Restoration readbacks also live in SANDBOX_TESTS.json, CURVE_LIVE_TESTS.json and YOUTUBE_WORKFLOW_TESTS.json. This is not proof that every opaque grade parameter is byte-identical. Original SaveProject was actually executed as a preservation step under the operator's broad practical-test request; no separate save-only confirmation was sought, and it committed the user's current state. The DRP export was not re-import tested. Future production automation must resolve unsaved state explicitly rather than infer save permission from this one-shot test; never delete/overwrite the original to attempt recovery.

## Tested Color curve route (not a point-editing API)

`generate_curve_fixtures.cjs` uses local `resolve-advanced/vendor/drx-codec/drx-generator.js`: `createNeutralNodeParams()`, two labelled nodes passed to `generateDRX`, one carrying `customCurves.y=[{x:0,y:0},{x:.5,y:.5 or .7},{x:1,y:1}]`. `CURVE_FIXTURE_ROUNDTRIP.json` records offline parse. `qualify_curves_and_render.py` then calls `item.GetNodeGraph().ApplyGradeFromDRX(path,0)`, reads GetNumNodes/GetNodeLabel/GetToolsInNode and renders each result through Resolve. Offline codec roundtrip alone is not live proof. The actual rendered transfer is not simply “ordinate .7 → output .7”.

ApplyGradeFromDRX replaces the graph: the sandbox item had one Color node (`native_color_graph` in SANDBOX_TESTS.json), then two after the first fixture apply, not three. Both two-node fixture variants were generated with serial connections; native count/labels/tools are read back, but connection topology and other grade-version/keyframe preservation were not independently read back. Synthetic fixture is NOT a way to append to or preserve production user grades. The test did not qualify parallel nodes, HSL curves, arbitrary primaries or OFX parameter injection. Generated identity DRX is not a production backup. Qualification scripts are one-shot evidence scripts, **not safe idempotent production helpers**: do not rerun without inspecting guards/state; copy/adapt into a fresh approved run if required. They continue recording selected test failures to obtain diagnostics; production code must enforce its own stop conditions before dependent writes.

## Capture and proxy scopes

`capture_current_frame.py` exported the current user frame without seek/grade change; `CURRENT_FRAME_RECEIPT.json` preserves TC. This is a stable current-playhead capture, not an independent source-frame oracle. Raw project setting strings can be inactive leftovers under another color-science mode; a PNG does not independently prove effective color pipeline.

Working bundled helper: `scripts/proxy_scopes.py`. Run with existing Hermes venv:
```
/Users/macbook/.hermes/hermes-agent/venv/bin/python /Users/macbook/Knowledge/_skills/davinci-resolve/scripts/proxy_scopes.py input.png --space display-rec709 --output-prefix output
```
`--self-test`: 5 arithmetic known-color checks. `--rect x,y,w,h` selects a fractional region; it is not skin segmentation. Outputs JSON stats and RGB parade/histogram/CbCr proxy PNG. Qualification examples: `current-user-frame-proxy.{json,png}`, `curve-raised-proxy.{json,png}`. Assumed Rec709 weighting on RGB display codes, not linear luminance, calibrated IRE or HDR/legal certification. Endpoint counts are not proof of camera clipping. The screenshot descriptions supplied by user show native UI scopes; we did not calibrate proxy against their trace values.

## Advanced Node dependency state

Original `analyze_scopes.mjs` import failed on missing `zod`. Operator subsequently authorized a bounded Zod install after dependency audit. `ZOD_REGISTRY_PREFLIGHT.json` records exact `4.6.7`: runtime/peer/optional dependencies empty, no engine constraint returned. npm dry-run: 1 added, 0 changed, 0 removed. Installed only in `isolated-node-deps/` with lifecycle scripts disabled; no global install, no Node/npm/Claude/Hermes/Python/Homebrew update command. `ZOD_INSTALL_RECEIPT.json` verifies selected binaries/global npm inventory and project manifests unchanged (not a universal whole-system security audit).

`isolated_zod_hook.mjs` temporarily resolves Zod from this prefix without source edits/symlinks. Retry now fails on **missing fzstd**, not Zod. No further packages installed. Do not continue that dependency-install chain without new, explicit operator approval. Full advanced scope path remains blocked; installed Zod alone does not qualify it, and does not change resolution for ordinary launch of the source server. Direct DRX generator fixture worked independently of this broader module graph. Prefer working Python proxy until full advanced deps are deliberately qualified.

## Known limitations to retain

No tested numeric native-scopes feed; no OFX parameter read/write; Fusion ColorCurves instantiated only (not edited); no full Fairlight mixer/automation; no production artistic grade, tracking or mask-edge approval; no native transcription job/timeout test; no Clipto install/index/privacy validation; no complete multicam/trim/move preservation matrix. User Gamut Mapping is reference evidence, not generic recommendation. Native no-error tool status does not establish rendered or heard correctness.
