#!/usr/bin/env bash
# Install claude-shorts skill to ~/.claude/skills/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$HOME/.claude/skills/claude-shorts"

echo "=== Installing claude-shorts skill ==="

# Create skill directory
mkdir -p "$SKILL_DIR"
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/references"
mkdir -p "$SKILL_DIR/remotion"

# Copy SKILL.md (the skill definition)
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

# Copy scripts
for f in "$SCRIPT_DIR"/scripts/*.sh "$SCRIPT_DIR"/scripts/*.py; do
    [ -f "$f" ] && cp "$f" "$SKILL_DIR/scripts/"
done

# Make scripts executable
chmod +x "$SKILL_DIR"/scripts/*.sh 2>/dev/null || true
chmod +x "$SKILL_DIR"/scripts/*.py 2>/dev/null || true

# Copy references
for f in "$SCRIPT_DIR"/references/*.md; do
    [ -f "$f" ] && cp "$f" "$SKILL_DIR/references/"
done

# Copy Remotion project (excluding node_modules)
rsync -a --exclude='node_modules' --exclude='.remotion' \
    "$SCRIPT_DIR/remotion/" "$SKILL_DIR/remotion/"

echo ""
echo "Installed to: $SKILL_DIR"
echo ""
echo "Files copied:"
find "$SKILL_DIR" -type f | sort | while read -r f; do
    echo "  ${f#$SKILL_DIR/}"
done
echo ""
echo "Next steps:"
echo "  1. Run 'bash setup.sh' to install dependencies (if not done)"
echo "  2. Use /shorts in Claude Code to start the interactive pipeline"
