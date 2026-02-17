#!/usr/bin/env bash
# Post-render validation for exported shorts
# Usage: bash scripts/validate.sh --output-dir DIR
# Output: JSON with pass/fail per file, issues[], and summary
set -euo pipefail

OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [ -z "$OUTPUT_DIR" ]; then
    echo '{"pass":false,"error":"Usage: validate.sh --output-dir DIR"}'
    exit 1
fi

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "{\"pass\":false,\"error\":\"Output directory not found: $OUTPUT_DIR\"}"
    exit 1
fi

# Platform file size limits (bytes)
LIMIT_YT=$((256 * 1024 * 1024))
LIMIT_TT=$((287 * 1024 * 1024))
LIMIT_IG=$((250 * 1024 * 1024))

RESULTS=()
TOTAL=0
PASSED=0
FAILED=0

for file in "$OUTPUT_DIR"/short_*.mp4; do
    [ -f "$file" ] || continue
    TOTAL=$((TOTAL + 1))
    ISSUES=()
    basename=$(basename "$file")

    # 1. Check file is playable (ffprobe returns valid streams)
    if ! ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$file" &>/dev/null; then
        ISSUES+=("File is not playable or corrupt")
    fi

    # 2. Check video stream exists and resolution is 1080x1920
    width=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width -of csv=p=0 "$file" 2>/dev/null || echo "0")
    height=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=height -of csv=p=0 "$file" 2>/dev/null || echo "0")
    if [ "$width" != "1080" ] || [ "$height" != "1920" ]; then
        ISSUES+=("Resolution is ${width}x${height}, expected 1080x1920")
    fi

    # 3. Check audio track exists
    audio_codec=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$file" 2>/dev/null || echo "")
    if [ -z "$audio_codec" ]; then
        ISSUES+=("No audio track found")
    fi

    # 4. Check audio isn't silent (mean volume above -60 dB)
    if [ -n "$audio_codec" ]; then
        mean_vol=$(ffmpeg -i "$file" -af "volumedetect" -f null /dev/null 2>&1 \
            | grep "mean_volume:" | sed 's/.*mean_volume: //' | sed 's/ dB//' || echo "")
        if [ -n "$mean_vol" ]; then
            # Compare as integer (bash can't do float comparison natively)
            mean_int=$(printf "%.0f" "$mean_vol" 2>/dev/null || echo "-99")
            if [ "$mean_int" -le -60 ]; then
                ISSUES+=("Audio appears silent (mean volume: ${mean_vol} dB)")
            fi
        fi
    fi

    # 5. Check duration is within shorts range (3-90 seconds)
    duration=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$file" 2>/dev/null || echo "0")
    dur_int=$(printf "%.0f" "$duration" 2>/dev/null || echo "0")
    if [ "$dur_int" -lt 3 ] || [ "$dur_int" -gt 90 ]; then
        ISSUES+=("Duration ${dur_int}s is outside 3-90s range")
    fi

    # 6. Check file size against platform limit
    file_size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
    size_mb=$(echo "scale=1; $file_size / 1048576" | bc)

    platform="unknown"
    limit=0
    case "$basename" in
        *_yt.mp4) platform="youtube"; limit=$LIMIT_YT ;;
        *_tt.mp4) platform="tiktok"; limit=$LIMIT_TT ;;
        *_ig.mp4) platform="instagram"; limit=$LIMIT_IG ;;
    esac

    if [ "$limit" -gt 0 ] && [ "$file_size" -gt "$limit" ]; then
        limit_mb=$((limit / 1048576))
        ISSUES+=("File size ${size_mb}MB exceeds ${platform} limit of ${limit_mb}MB")
    fi

    # 7. Check video codec is H.264
    video_codec=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$file" 2>/dev/null || echo "")
    if [ "$video_codec" != "h264" ]; then
        ISSUES+=("Video codec is ${video_codec}, expected h264")
    fi

    # Build result for this file
    if [ ${#ISSUES[@]} -eq 0 ]; then
        PASSED=$((PASSED + 1))
        RESULTS+=("{\"file\":\"$basename\",\"platform\":\"$platform\",\"pass\":true,\"duration\":\"${dur_int}s\",\"size_mb\":$size_mb,\"issues\":[]}")
    else
        FAILED=$((FAILED + 1))
        issues_json=$(printf '"%s",' "${ISSUES[@]}" | sed 's/,$//')
        RESULTS+=("{\"file\":\"$basename\",\"platform\":\"$platform\",\"pass\":false,\"duration\":\"${dur_int}s\",\"size_mb\":$size_mb,\"issues\":[$issues_json]}")
    fi
done

if [ $TOTAL -eq 0 ]; then
    echo '{"pass":false,"error":"No short_*.mp4 files found in output directory"}'
    exit 1
fi

# Build JSON output
RESULTS_JSON=$(printf '%s\n' "${RESULTS[@]}" | paste -sd ',' | sed 's/^/[/' | sed 's/$/]/')
ALL_PASS="false"
[ $FAILED -eq 0 ] && ALL_PASS="true"

cat <<EOF
{
  "action": "validate",
  "pass": $ALL_PASS,
  "total": $TOTAL,
  "passed": $PASSED,
  "failed": $FAILED,
  "files": $RESULTS_JSON
}
EOF
