#!/bin/sh
# Installs the plan-to-blender-room skill for Claude Code into ~/.claude/skills/
set -e
URL="https://deniz.is-a.dev/oyun-odasi-3d/skill/plan-to-blender-room.skill"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
TMP="$(mktemp -d)"
mkdir -p "$DEST"
curl -fsSL "$URL" -o "$TMP/skill.zip"
rm -rf "$DEST/plan-to-blender-room"
unzip -q "$TMP/skill.zip" -d "$DEST"
rm -rf "$TMP"
echo "Installed: $DEST/plan-to-blender-room"
ls "$DEST/plan-to-blender-room"
