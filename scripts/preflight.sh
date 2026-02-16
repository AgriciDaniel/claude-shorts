#!/usr/bin/env bash
# Pre-flight safety check before shortform pipeline
# Usage: bash scripts/preflight.sh <input_file> [output_dir]
# Output: JSON with pass/fail status and any warnings
set -euo pipefail

INPUT="${1:-}"
OUTPUT_DIR="${2:-./shorts}"

if [ -z "$INPUT" ]; then
    echo '{"pass":false,"error":"Usage: preflight.sh <input_file> [output_dir]"}'
    exit 1
fi

WARNINGS=()
ERRORS=()

# Check input exists
if [ ! -f "$INPUT" ]; then
    ERRORS+=("Input file not found: $INPUT")
fi

# Check input is a video file (via ffprobe)
if [ -f "$INPUT" ]; then
    if ! ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_type -of csv=p=0 "$INPUT" 2>/dev/null | grep -q "video"; then
        ERRORS+=("Input is not a valid video file: $INPUT")
    fi
fi

# Check output directory
if [ -d "$OUTPUT_DIR" ]; then
    EXISTING=$(find "$OUTPUT_DIR" -name "short_*.mp4" 2>/dev/null | wc -l)
    if [ "$EXISTING" -gt 0 ]; then
        WARNINGS+=("Output directory has $EXISTING existing short_*.mp4 files")
    fi
fi

# Check disk space (estimate 3x input size for temp + output)
if [ -f "$INPUT" ]; then
    INPUT_SIZE_KB=$(du -k "$INPUT" | cut -f1)
    NEEDED_KB=$((INPUT_SIZE_KB * 3))
    AVAIL_KB=$(df -k /tmp 2>/dev/null | tail -1 | awk '{print $4}')
    if [ -n "$AVAIL_KB" ] && [ "$AVAIL_KB" -lt "$NEEDED_KB" ]; then
        WARNINGS+=("Low disk space on /tmp: ${AVAIL_KB}KB available, estimated ${NEEDED_KB}KB needed")
    fi
fi

# Check FFmpeg
if ! command -v ffmpeg &>/dev/null; then
    ERRORS+=("ffmpeg not found — install with: sudo apt install ffmpeg")
fi

# Check ffprobe
if ! command -v ffprobe &>/dev/null; then
    ERRORS+=("ffprobe not found — install with: sudo apt install ffmpeg")
fi

# Check Node.js
if ! command -v node &>/dev/null; then
    ERRORS+=("Node.js not found — install with: nvm install 18")
fi

# Check Python venv
VENV=""
if [ -d "$HOME/.video-skill" ]; then
    VENV="$HOME/.video-skill"
elif [ -d "$HOME/.shorts-skill" ]; then
    VENV="$HOME/.shorts-skill"
fi

if [ -z "$VENV" ]; then
    ERRORS+=("Python venv not found — run: bash setup.sh")
else
    # Check faster-whisper is installed
    if ! "$VENV/bin/python3" -c "import faster_whisper" 2>/dev/null; then
        ERRORS+=("faster-whisper not installed in $VENV — run: bash setup.sh")
    fi
fi

# Check Remotion node_modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ ! -d "$SCRIPT_DIR/remotion/node_modules" ]; then
    ERRORS+=("Remotion dependencies not installed — run: bash setup.sh")
fi

# Get video info
DURATION=""
RESOLUTION=""
if [ -f "$INPUT" ] && command -v ffprobe &>/dev/null; then
    DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$INPUT" 2>/dev/null || echo "")
    RESOLUTION=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$INPUT" 2>/dev/null || echo "")
fi

# Build JSON output
PASS="true"
if [ ${#ERRORS[@]} -gt 0 ]; then
    PASS="false"
fi

ERROR_JSON="[]"
if [ ${#ERRORS[@]} -gt 0 ]; then
    ERROR_JSON=$(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .)
fi

WARN_JSON="[]"
if [ ${#WARNINGS[@]} -gt 0 ]; then
    WARN_JSON=$(printf '%s\n' "${WARNINGS[@]}" | jq -R . | jq -s .)
fi

cat <<EOF
{
  "pass": $PASS,
  "input": "$INPUT",
  "output_dir": "$OUTPUT_DIR",
  "duration": ${DURATION:-null},
  "resolution": "${RESOLUTION:-unknown}",
  "venv": "${VENV:-none}",
  "errors": $ERROR_JSON,
  "warnings": $WARN_JSON
}
EOF

[ "$PASS" = "true" ] && exit 0 || exit 1
