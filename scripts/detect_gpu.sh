#!/usr/bin/env bash
# Detect NVIDIA GPU and available NVENC encoders for FFmpeg
# Usage: bash scripts/detect_gpu.sh
# Output: JSON with gpu_name, driver, encoders[], cuda_filters[]
set -euo pipefail

json_output() {
    local gpu_name="${1:-none}"
    local driver="${2:-none}"
    local has_nvenc="${3:-false}"
    local encoders="${4:-[]}"
    local cuda_filters="${5:-[]}"

    cat <<EOF
{
  "gpu_detected": $([ "$gpu_name" != "none" ] && echo "true" || echo "false"),
  "gpu_name": "$gpu_name",
  "driver_version": "$driver",
  "nvenc_available": $has_nvenc,
  "encoders": $encoders,
  "cuda_filters": $cuda_filters,
  "recommendation": $([ "$has_nvenc" = "true" ] && echo '"Use NVENC for 5-10x faster encoding"' || echo '"No GPU detected, using CPU encoding"')
}
EOF
}

# Check for nvidia-smi
if ! command -v nvidia-smi &>/dev/null; then
    json_output
    exit 0
fi

# Get GPU info
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | xargs) || GPU_NAME="none"
DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 | xargs) || DRIVER="none"

if [ "$GPU_NAME" = "none" ]; then
    json_output
    exit 0
fi

# Check FFmpeg NVENC encoders
ENCODERS="[]"
if command -v ffmpeg &>/dev/null; then
    ENC_LIST=$(ffmpeg -hide_banner -encoders 2>/dev/null | grep -oP '(h264|hevc|av1)_nvenc' | sort -u)
    if [ -n "$ENC_LIST" ]; then
        ENCODERS=$(echo "$ENC_LIST" | jq -R . | jq -s .)
    fi
fi

# Check CUDA filters
CUDA_FILTERS="[]"
if command -v ffmpeg &>/dev/null; then
    FILTER_LIST=$(ffmpeg -hide_banner -filters 2>/dev/null | grep -oP '\S*cuda\S*' | sort -u)
    if [ -n "$FILTER_LIST" ]; then
        CUDA_FILTERS=$(echo "$FILTER_LIST" | jq -R . | jq -s .)
    fi
fi

HAS_NVENC="false"
if [ "$ENCODERS" != "[]" ]; then
    HAS_NVENC="true"
fi

json_output "$GPU_NAME" "$DRIVER" "$HAS_NVENC" "$ENCODERS" "$CUDA_FILTERS"
