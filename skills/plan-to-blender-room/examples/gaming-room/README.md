# Example: gaming room (finished project)

A 5.24 × 3.63 m room from a ground-floor plan, matched to an AI-generated
night render: built-in shelving with backlit compartments, slatted walls,
pegboard, desk with three monitors and an RGB PC, racing chair, modular sofa,
shag rugs, VR zone, suspended LED ring, track lights, terrace and garden.
18 iterations; final renders and a live viewer: https://deniz.is-a.dev/oyun-odasi-3d/
(source: https://github.com/creeperkafasi/oyun-odasi-3d).

Files here are that project's `scene/` modules. To run them, put them in one
folder together with `../../scripts/*.py`, generate textures with
`python3 gen_textures.py` (writes `../tex/`), then
`blender -b -P build.py -- --out out/x.png --pct 50 --samples 64 [--cam main|back|desk|sofa|top]`.

Useful to grep for:
- `joinery.py`: `tower()` open shelving with LED + compartment registry, console, slat wall, pegboard, desk carcass
- `furniture.py`: `gaming_chair` + `_chair_surface` (parametric shell), `sofa_group`, `throw_blanket`, `ceiling_ring`, `track_lights` (returns spot positions), `rugs` + fur
- `props.py`: `monitor`, `pc_tower`, `keyboard`, `gamepad`, `headphones`, `vr_headset`, `figure`, `game_cases`, `frame`, `potted`
- `arch.py`: sliding door, window + venetian blinds, door with lever, curtains
- `exterior.py`: terrace, outdoor sofa, planters, garden tree rows
- `build.py`: material palette, light rig (spots, shelf areas, fills, light-linked sun), cameras incl. axonometric cutaway, render setup
- `room.json`, `points.json`: inputs for `template_build.py` / `camsolve.py`
- `site/index.html`: comparison page (wipe slider, gallery, three.js GLB viewer)
