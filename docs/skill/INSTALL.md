# plan-to-blender-room — install instructions (for Claude / agents)

This is a Claude skill: turn a floor plan and/or a reference interior image into a
procedural Blender 3D room, iterated until Cycles renders match the reference.

## Install (Claude Code)

Run:

    curl -fsSL https://deniz.is-a.dev/oyun-odasi-3d/skill/install.sh | sh

or manually:

    mkdir -p ~/.claude/skills
    curl -fsSL https://deniz.is-a.dev/oyun-odasi-3d/skill/plan-to-blender-room.skill -o /tmp/p2b.zip
    unzip -o /tmp/p2b.zip -d ~/.claude/skills/

The archive contains a single folder `plan-to-blender-room/` with `SKILL.md`,
`scripts/`, `references/` and `examples/`. After installing, the skill is
available in new Claude Code sessions (restart the session if it's already
running). Then read `~/.claude/skills/plan-to-blender-room/SKILL.md`.

## Install (claude.ai)

Download https://deniz.is-a.dev/oyun-odasi-3d/skill/plan-to-blender-room.skill
and upload it under Settings → Capabilities → Skills.

## Requirements

Blender 4.2+ on PATH (tested 5.2), Python 3 with numpy, scipy, Pillow,
poppler's `pdftoppm` for PDF plans. A GPU (OptiX/CUDA/HIP/Metal) is strongly
recommended. Check with:

    blender --version && python3 -c "import numpy, scipy, PIL" && which pdftoppm

## Browse the source

https://github.com/creeperkafasi/oyun-odasi-3d/tree/main/skills/plan-to-blender-room
