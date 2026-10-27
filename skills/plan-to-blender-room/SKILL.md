---
name: plan-to-blender-room
description: Turn a floor plan (PDF/image) and/or a reference interior image (often an AI-generated render) into a procedural Blender 3D model of the room, built entirely from Python and iterated until Cycles renders look like the reference. Covers plan measuring, camera matching to the reference by least squares, procedural materials, furniture, plants, shag rugs (Geometry Nodes), archviz lighting, comparison loops, and delivery (.blend, .glb, alternate views, cutaway). Use this whenever someone wants to "make this render 3D", recreate an interior/room/architectural visualization in Blender, turn a floor plan into a 3D room, match a 3D scene to a photo or AI image, or model an interior to look like a picture — even if they don't say "Blender" or "procedural".
compatibility: Blender 4.2+ (tested 5.2) on PATH; Python 3 with numpy, scipy, Pillow; pdftoppm (poppler) for PDF plans. A GPU (OptiX/CUDA/HIP/Metal) makes iteration practical.
---

# Plan + reference image → procedural Blender room

The job: produce a real 3D model whose renders, from a camera matched to the
reference, look as much like the reference as possible, while the
architecture follows the plan. Everything is built from Python scripts,
which makes it repeatable: change one number, rebuild, re-render, compare.

Work **iteratively, coarse to fine**. People who ask for this want to see
the model converge, so show interim renders as you go.

## 0. Set up

```sh
blender --version; nvidia-smi -L 2>/dev/null
python3 -c "import numpy, scipy, PIL"
```

Create a project folder with a `scene/` subfolder and **copy all of
`scripts/*.py` into `scene/`**. The modules import each other (`import lib`),
so they must sit together; your own build code goes next to them. Put the
inputs in `ref/` and renders in `out/`. Scratch images (crops, comparisons)
pile up fast, so keep them in `out/` subfolders.

| script | what it is |
|---|---|
| `lib.py` | geometry helpers: `box`, `cyl`, `torus`, `ring_band`, `prism`, `uv_plane`, `ellipsoid`, `capsule_between`, curves, `empty` (rot in **degrees**), `aim`, `add_bevel`, collections, simple `mat`/`emission_mat` |
| `materials.py` | node materials: `concrete`, `plaster`, `wood(axis=)`, `fabric`, `leather`, `shag`, `shag_fiber`, `leaf_vc`, `curtain`, `thin_glass`, `image_emit` (screens), `sky_world`, `sky_dome` |
| `plants.py` | `leafy_plant`, `ficus`, `bush`, `pothos`, `pot`, `tree` (clustered foliage), `conifer` |
| `fur.py` | Geometry Nodes strand instancing for shag rugs |
| `lighting.py` | `spot`, `area`, `point` light helpers + warm/blue presets |
| `template_build.py` | **starting scene**: room shell from `room.json`, openings, matched camera, sky dome, light-linked sun, GPU Cycles setup, AgX |
| `camsolve.py`, `backproj.py` | camera fit from 3D↔pixel pairs; pixel → plan position |
| `gridcrop.py`, `compare.py`, `patches.py`, `post.py` | read pixel coordinates; side-by-side comparison; region brightness ratios; bloom/vignette |
| `closeup.py`, `export_glb.py` | extra views from a saved .blend; glTF export |

`examples/gaming-room/` is a complete finished project built this way:
built-in shelving, desk, racing chair, modular sofa, monitors, PC, figurines,
terrace and garden. When you need a piece of furniture, **grep it for a
similar builder and adapt it** rather than starting from zero; don't read the
whole folder into context. `references/pitfalls.md` lists the problems that
cost the most time. Read it before the lighting pass.

## 1. Read the plan → `room.json`

1. Rasterize at 300 dpi (`pdftoppm -r 300 -png plan.pdf ref/plan`) and look at it.
2. **Find which room the reference shows.** Match its openings: which wall has
   the big glass, where the window and door are relative to the view. State your
   conclusion and the camera direction; if two rooms fit, ask.
3. Get the scale from a dimension annotation, e.g. a window labelled "130".
   Measure its pixel length → px/cm, and cross-check with a second annotation.
   Then crop the room and read the interior faces, wall thickness, and each
   opening's start/end along its wall. Use `gridcrop.py` for exact pixels.
4. Pick coordinates: origin at the interior SW corner, X east, Y north, Z up,
   metres. Write `room.json` (format in the `template_build.py` docstring).
   Ceiling height is rarely on a plan; 2.6–2.8 m clear is typical. Choose one
   and note it.
5. Run `template_build.py --quick` to check the shell.

No plan, only an image? Estimate the room from the image (standard door 0.9 × 2.1 m,
desk height 0.75 m, etc.), tell the user these are estimates, and continue.

## 2. Study the reference

Crop the reference into regions at 2× and look at each one: back wall, each side
wall, ceiling, foreground. Write down, per wall, every element (joinery,
openings, furniture, props, light sources) and the lighting mood: key colour,
accent colours, which surfaces glow. This list is your build plan and your
checklist for later comparisons.

## 3. Match the camera

1. With `gridcrop.py ref.jpg x0 y0 x1 y1 scale out.png [step]`, read exact pixel
   coordinates of points whose 3D position the plan fixes: window and glass
   corners, mullion feet, door jamb tops, the door handle (z ≈ 1.0), corners of
   built-ins. Spread them over **≥3 walls**, near and far.
2. Write `points.json` and run `python3 camsolve.py points.json > camera.json`.
   Check `rms_px` and the residuals. 10–20 px is normal for AI images, which
   aren't perspective-consistent. Drop or fix outliers. Use `bounds` if the
   camera leaves the room. Free yaw is usually better than yaw = 0.
3. Render with `--cam camera.json --quick`, then `compare.py` side-by-side. If
   the reference shows more of the room than the plan allows (common), a
   10–15 % wider lens keeps the overall framing closer. Tell the user the room
   in the image is wider than the plan and that you kept the plan.
4. Place furniture with `backproj.py camera.json u,v[,z]`. Pick the pixel where
   a sofa foot, rug edge or chair base meets the floor (z = 0), or a desk-top
   edge (z = 0.75). Average a few points and round to sensible positions.
   Where image and plan disagree, the plan wins for walls; for furniture,
   choose what reads closest to the image from the camera.

## 4. Build in passes, rendering after each

Grow `template_build.py` into your `build.py`, or start from
`examples/gaming-room/build.py`. Keep dimensions in a `cfg.py` and group code
by area (architecture, joinery, furniture, props, exterior).

1. **Massing:** boxes for every major element in the right place. Use `--quick`
   and compare framing with the reference.
2. **Materials + lighting:** Cycles at `--pct 50 --samples 64` (~10 s). Get
   floor, walls, wood and the overall mood right before adding detail; lighting
   changes everything downstream. Use `patches.py` with regions you pick
   (same surface in both images) to see which areas are too bright or too dark.
3. **Hero furniture:** the objects the eye goes to first (desk, chair, sofa,
   shelving). Model them properly. Parametric surfaces + Solidify + Subdivision
   for upholstery; bevelled boxes for joinery.
4. **Props and plants:** fill shelves and surfaces the way the reference does.
   Repetition reads as clutter in a good way: rows of books, figurines, plants.
   Procedural textures for screens and posters can come from a small
   PIL script; see `examples/gaming-room/gen_textures.py`.
5. **Exterior:** anything seen through glass needs a sky (`sky_dome`), lit
   trees (sun with light linking plus uplights), and a ground. A dark exterior
   makes glass read as a mirror.
6. **Polish:** `post.py` bloom, DOF on near foreground objects, exposure.

After each pass, look at the side-by-side **and** at 2× crops of each region
compared with the reference. List the 4–6 biggest differences, fix them in one
batch, render again. Tell the user in a line or two what changed and what's
next, and offer an interim image when one shows real progress.

## 5. Deliver

- Final render from the matched camera (100 %, 256–384 samples) + `post.py`.
- **Alternate views** prove it is a real 3D model and catch hidden errors:
  2–3 interior angles plus an orthographic **axonometric cutaway** (hide
  ceiling and the two near walls from camera with `visible_camera = False`,
  film transparent). Missing backs, floating props and empty corners show up
  here; fix them.
- `.blend` with `bpy.ops.file.pack_all()` before saving.
- `.glb` via `export_glb.py` on a copy of the .blend (`--nodraco --lite` for
  web viewers).
- A short report: what matches, and the **deliberate deviations** (plan vs
  image disagreements and which one you followed).

A comparison page (wipe slider reference ↔ render, gallery, three.js GLB viewer)
is a good way to share results; `examples/gaming-room/site/index.html` is one.

## Judgment calls

- Floor plans show someone's home. Don't publish the plan (public repo,
  public page) without asking; renders of a single room are usually fine.
- Overshooting on detail is better than undershooting; the reference is the
  bar. But one hour of iteration should yield a clearly recognisable match.
  Stop polishing when remaining differences come from the AI image's own
  inconsistencies.
- Renders and builds can take minutes. Run long jobs in the background and
  keep working (write the next module, prepare the report) instead of idling.
