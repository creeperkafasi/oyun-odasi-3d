# Pitfalls and fixes (learned the hard way)

Each entry: symptom → cause → fix. Most fixes are already baked into `scripts/`.

## Geometry

- **Large flat faces look domed / grey gradient across a panel** (chair backs, desk tops).
  Smooth shading averages the big face's corner normals with the bevel strip.
  → Bevel modifier with `harden_normals = True` (done in `lib.add_bevel`).
- **Faceted triangles on extruded ngons with boolean cuts.** Prisms from concave
  outlines + booleans + bevel shade badly. → Build curved, soft objects (seat
  shells, cushions) as a parametric grid surface + Solidify + Subdivision; leave
  holes by skipping grid faces instead of booleans. See `_chair_surface` in
  `examples/gaming-room/furniture.py`.
- **Venetian blinds read as thin lines.** Slats seen edge-on. → Tilt ~50°,
  slat depth ~25 mm, pitch ~30 mm.
- **Child objects land in the wrong place.** Setting `obj.parent` in Python keeps
  `matrix_parent_inverse` = identity, so the child's location is *local*. That is
  what the helpers expect: build parts around the origin, parent to an empty,
  then move or rotate the empty.
- **`lib.empty(rot=...)` takes degrees**; `rotation_euler` takes radians. Mixing
  them once made every prop spin wildly.
- **Extra cameras all look straight down.** `matrix_world` is not updated in a
  script before a depsgraph update. → Set `rotation_euler = quat.to_euler()` from
  the computed quaternion instead of reading `matrix_world`.
- Don't name a module `builtins.py`; it shadows Python's own.

## Materials

- **Rugs or sofas look white or grey at grazing angles.** Sheen at 1.0. → Keep
  sheen at 0.1–0.3 on dark fabrics.
- **Rugs look like flat felt.** Bump alone can't sell shag. → Use `fur.fur()`
  (Geometry Nodes strand instances, ~30k/m², 3.5–4 cm). Cheap in Cycles because
  they are instances. Strand colour comes from world-position noise, since
  object/generated coordinates repeat on every instance.
- **Wood zebra stripes on panels.** Grain axis doesn't match the panel's long
  axis. → Create a second wood material with `axis="Z"` for vertical panels and
  side boards.
- **Glass hides the outside / reflects the whole room.** Physically based glass at
  grazing angles is a mirror. → `materials.thin_glass` (transparent + fresnel
  glossy, max reflection ~0.06–0.10).
- **PC fans or anything behind "dark glass" disappear.** An opaque dark
  Principled acts as a wall. → `thin_glass(tint=...)`.
- **Leaves look like confetti.** Large random quads with per-leaf colour jitter.
  → Cluster leaves (`plants.tree(..., clusters=…)`), keep jitter ≤0.15, use
  smaller leaves in larger numbers, and give each cluster one palette colour.

## Lighting & colour

- **Interior turns blue** once the sky is bright enough to look right through
  windows. The sky is lighting the room. Light Path "Is Camera Ray" does *not*
  survive transparent glass. → Keep the world dim (it only fills the room) and
  add `materials.sky_dome`, an emissive sphere visible to camera and
  transmission rays only.
- **Trees outside are black silhouettes.** Nothing lights them from the viewer's
  side. → Add a low sun aimed toward the camera side, light-linked
  (`light_linking.receiver_collection` *and* `blocker_collection`) to the
  exterior collections, so it never streams into the room. Add a few warm
  uplight spots at the trees for the evening look.
- **A distant "hill" or tree mass blocks the sky in the window.** Check what
  the window actually sees. Keep far geometry low (elevation angle <5°).
- **Blue LEDs turn white or lavender.** AgX desaturates bright saturated blue.
  → Lower the emission (strength 1.5–3 for blue strips) instead of raising
  exposure. Strong blue looks right *dim*.
- **LED emitter strips show up as hard white lines on the ceiling.** →
  `obj.visible_camera = False` (and `visible_glossy = False`) for cove strips;
  they still light the scene.
- **Shelf compartments either dead or blown out.** Add a small area light per
  compartment (~8–12 W) on top of the emissive strips, and keep the shelf back
  panels dark wood so they don't glow cream.
- **Too bright vs too dark is subjective.** Use `scripts/patches.py` with
  hand-picked regions that show the same surface in both images. Calibrate
  until most ratios are 0.8–1.25; ignore regions where the geometry differs.
- View transform: AgX "Medium High Contrast" matched a typical AI archviz render
  best. "Khronos PBR Neutral" keeps blues saturated but goes cold and dark.
- Bloom: Cycles has none. `scripts/post.py` adds a screen-blended multi-scale
  bloom and a light vignette, which matters a lot for LED-heavy scenes.

## Camera matching

- AI renders are **not** geometrically consistent. Expect 12–20 px RMS from the
  least-squares fit, and expect the AI room to look wider than the plan. Keep the
  plan's dimensions; say so to the user rather than silently stretching the room.
- Fit with no pitch (archviz renders keep verticals vertical; the horizon offset
  becomes `shift_y`). Free yaw usually beats forcing yaw=0.
- Give the solver points on **at least three different walls**, including some
  near the camera (window/glass mullions, door jambs). Points from one wall
  only leave depth unconstrained.
- If the solved camera ends up outside the room, constrain it with `bounds`.
  A wider lens (−10–15 %) often matches the overall framing better than the fit.

## Rendering & practicalities

- **Background Blender: Cycles needs the GPU selected explicitly**
  (`template_build.render_setup` tries OptiX → CUDA → HIP → Metal → oneAPI).
  The "HIPEW initialization failed" warning on NVIDIA machines is harmless.
- **Each run rebuilds the scene from Python** (~20–30 s with plants and fur).
  For many camera angles from the same scene, save a `.blend` once and render
  views from it (`blender -b scene.blend -P closeup.py -- …`).
- Fast iteration: `--pct 50 --samples 64` (~10 s on an RTX 2050); finals at 100 %
  and 256–384 samples with OptiX denoise.
- **GLB:** the procedural node graphs don't survive glTF; `export_glb.py`
  flattens them to colours. Draco-compressed GLBs need a decoder fetch that
  sandboxed pages (claude.ai artifacts) block, so export `--nodraco` for web
  viewers. Claude artifacts don't serve `.glb` at all: ship it base64 in a
  `.txt` and use `GLTFLoader.parse`. GitHub Pages serves `.glb` fine.
- Pack textures (`bpy.ops.file.pack_all()`) before saving a `.blend` you will
  share.
