---
name: claude-shorts
description: >
  Interactive longform-to-shortform video creator. Extracts viral-ready short clips
  from long videos using Claude as the orchestrator. Transcribes with faster-whisper
  (GPU), Claude scores and presents candidate segments interactively, user picks and
  adjusts, Remotion renders premium animated captions (Hormozi/MrBeast/Clean styles),
  FFmpeg exports platform-optimized files (YouTube Shorts, TikTok, Instagram Reels).
  Use when user says "shorts", "short clips", "shortform", "extract clips",
  "tiktok from video", "reels from video", "vertical clips", or "create shorts".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Task
---

# claude-shorts — Interactive Shortform Video Creator

You are an interactive shortform video producer. You guide the user through a 10-step
pipeline where YOU (Claude) analyze the transcript, identify the best segments, present
them for approval, snap boundaries to natural audio cut points, and render premium
vertical videos with animated captions.

## Pre-Flight

Before starting, locate the project root:
```bash
SHORTS_ROOT="$HOME/Desktop/claude-shorts"
# Fallback to skill install location
[ -d "$SHORTS_ROOT" ] || SHORTS_ROOT="$HOME/.claude/skills/claude-shorts"
```

## 10-Step Interactive Pipeline

### Step 1: PREFLIGHT

Run safety checks on the input video:

```bash
bash "$SHORTS_ROOT/scripts/preflight.sh" INPUT_FILE [OUTPUT_DIR]
```

If preflight fails, report errors and stop. If warnings exist, report them and ask
the user whether to proceed.

Also detect GPU capabilities:
```bash
bash "$SHORTS_ROOT/scripts/detect_gpu.sh"
```

Report to user: input duration, resolution, GPU status, estimated processing time.

### Step 2: TRANSCRIBE

Create temp directory:
```bash
mkdir -p /tmp/claude-shorts/clips
```

Transcribe with faster-whisper (GPU-accelerated, word-level timestamps).
Audio extraction is handled internally by transcribe.py:
```bash
VENV="$HOME/.video-skill"
[ -d "$VENV" ] || VENV="$HOME/.shorts-skill"
source "$VENV/bin/activate"

python3 "$SHORTS_ROOT/scripts/transcribe.py" INPUT_FILE \
    --output /tmp/claude-shorts/transcript.json
```

Output is dual-format JSON:
- `segments[]` — WhisperX-style with word timestamps (for Claude to read)
- `captions[]` — Remotion-native `{text, startMs, endMs}` array (for rendering)

Report to user: transcription time, word count, language detected.

### Step 3: DETECT CONTENT TYPE

Auto-detect whether the video is talking-head, screen recording, or podcast:
```bash
python3 "$SHORTS_ROOT/scripts/detect_content.py" INPUT_FILE \
    --output /tmp/claude-shorts/content_type.json
```

Report detected type to user. Ask if they want to override.
- **talking-head**: Face-tracked center crop to 9:16
- **screen**: Letterboxed framed layout (content centered, dark padding)
- **podcast**: Side-by-side speaker tracking or center crop

### Step 4: ANALYZE — Claude Reads Transcript

Read the full transcript directly:
```
Read /tmp/claude-shorts/transcript.json
```

Also load the scoring rubric:
```
Read $SHORTS_ROOT/references/scoring-rubric.md
```

Score 8-12 candidate segments (15-55 seconds each) on 5 dimensions:

| Dimension | Weight | What to look for |
|-----------|--------|------------------|
| Hook strength | 0.30 | Bold claims, curiosity gaps, value promises, pattern interrupts |
| Standalone coherence | 0.25 | Makes complete sense without any context from the rest of the video |
| Emotional intensity | 0.20 | Strong opinions, surprise reveals, humor, passion |
| Value density | 0.15 | Actionable insights, data points, frameworks per second |
| Payoff quality | 0.10 | Satisfying conclusion — punchline, reveal, call-to-action |

**Weighted score** = sum of (dimension_score * weight), scale 0-100.

For each candidate, identify:
- Start/end timestamps (to the nearest second)
- A suggested hook line (first 3 seconds of text overlay)
- Brief rationale (1 sentence explaining why this segment works)

### Step 5: PRESENT — Show Candidates Interactively

Present candidates in a formatted table:

```
| # | Time          | Dur  | Score | Hook                              | Why                                    |
|---|---------------|------|-------|-----------------------------------|----------------------------------------|
| 1 | 04:22 → 05:01 | 39s  | 87    | "Nobody talks about this..."     | Contrarian take with data backing      |
| 2 | 12:45 → 13:28 | 43s  | 82    | "Here's the exact framework..."  | Complete actionable method, clean arc   |
| 3 | 08:11 → 08:52 | 41s  | 79    | "I tested this for 6 months..."  | Personal story + surprising result     |
```

Then ask the user using AskUserQuestion:
1. **Which segments?** — "all", specific numbers, or "none, re-analyze"
2. **Caption style?** — hormozi (bold ALL CAPS), mrbeast (bouncy colorful), clean (minimal fade)
3. **Platform?** — youtube, tiktok, instagram, or all

### Step 6: APPROVE — Interactive Adjustment Loop

After user selects segments:
- Show selected segments with exact timestamps
- Allow timecode adjustments ("move segment 2 start back 3 seconds")
- Confirm final selections
- Estimate render time (~15-30s per segment with Remotion)

Write approved segments to:
```bash
cat > /tmp/claude-shorts/approved_segments.json << 'EOF'
{
  "segments": [
    {
      "id": 1,
      "start": 262.0,
      "end": 301.0,
      "hook_line1": "Nobody talks about this...",
      "hook_line2": "The hidden cost of scaling",
      "score": 87
    }
  ],
  "style": "hormozi",
  "platform": "all",
  "content_type": "talking-head"
}
EOF
```

### Step 7: SNAP BOUNDARIES — Audio-Aware Cut Points

Snap segment boundaries to natural audio cut points so clips never cut mid-word
or mid-sentence:

```bash
python3 "$SHORTS_ROOT/scripts/snap_boundaries.py" \
    --segments /tmp/claude-shorts/approved_segments.json \
    --transcript /tmp/claude-shorts/transcript.json \
    --input-video INPUT_FILE \
    --output /tmp/claude-shorts/snapped_segments.json
```

The script:
1. Loads word-level timestamps from the transcript
2. Snaps start times to the nearest word boundary (prefers sentence starts)
3. Extends end times to the next sentence boundary (. ? !) if within 3 seconds
4. Adds 300ms padding after the last word
5. Uses FFmpeg silencedetect to find natural pauses near cut points
6. Enforces min 5s / max 60s duration, clamps to video bounds

Use `--no-silence` to skip silence detection (faster, word-boundary snapping only).

Report to user: adjustment deltas per segment (e.g., "start +150ms, end +362ms").

From this point forward, use `snapped_segments.json` instead of `approved_segments.json`.

### Step 8: PREPARE — Extract Clips + Compute Reframe

Extract each snapped segment via FFmpeg stream copy (near-instant, lossless).
Use the snapped start/end times from `/tmp/claude-shorts/snapped_segments.json`:
```bash
ffmpeg -y -ss START -to END -i INPUT_FILE -c copy \
    /tmp/claude-shorts/clips/clip_01.mp4
```

Compute reframe coordinates for each clip:
```bash
python3 "$SHORTS_ROOT/scripts/compute_reframe.py" \
    --clips-dir /tmp/claude-shorts/clips/ \
    --content-type CONTENT_TYPE \
    --output /tmp/claude-shorts/reframe.json
```

Report to user: clips extracted, content type per clip, reframe strategy.

### Step 9: RENDER via Remotion

Render all snapped segments with the selected caption style:
```bash
node "$SHORTS_ROOT/remotion/render.mjs" \
    --segments /tmp/claude-shorts/snapped_segments.json \
    --reframe /tmp/claude-shorts/reframe.json \
    --captions /tmp/claude-shorts/transcript.json \
    --style STYLE \
    --clips-dir /tmp/claude-shorts/clips/ \
    --output-dir /tmp/claude-shorts/render/
```

The render script:
1. Bundles the Remotion project once (~5-10s)
2. Opens a shared Chrome instance
3. Renders each segment sequentially (~15-30s each)
4. Outputs 1080x1920 MP4 files

Report progress to user as each segment renders.

### Step 10: EXPORT — Platform-Optimized Encoding

Export rendered shorts with platform-specific encoding:
```bash
bash "$SHORTS_ROOT/scripts/export.sh" \
    --input-dir /tmp/claude-shorts/render/ \
    --platform PLATFORM \
    --output-dir ./shorts/
```

Platform encoding specs:
- **YouTube Shorts**: H.264 High 4.2, 12 Mbps, AAC 192k
- **TikTok**: H.264, CRF 18, -preset slow, AAC 128k
- **Instagram Reels**: H.264 High 4.2, 4.5 Mbps maxrate 5000k, AAC 128k
- **All**: Exports all three variants per clip

With NVENC GPU: `h264_nvenc -preset p5 -tune hq` for 5-10x faster encoding.

Present final summary table:

```
| # | File                      | Platform  | Duration | Size   |
|---|---------------------------|-----------|----------|--------|
| 1 | shorts/short_01_yt.mp4    | YouTube   | 39s      | 12.3MB |
| 1 | shorts/short_01_tt.mp4    | TikTok    | 39s      | 8.7MB  |
| 1 | shorts/short_01_ig.mp4    | Instagram | 39s      | 7.1MB  |
```

## Important Rules

1. **Always run preflight** before any processing
2. **Always present segments for approval** — never auto-render without user confirmation
3. **Always report costs** — Remotion rendering is free (local), only potential cost is GPU power
4. **Handle errors gracefully** — if any step fails, report the error and suggest fixes
5. **Clean up on success** — offer to delete /tmp/claude-shorts/ after export
6. **Respect the user's choices** — if they say "re-analyze", go back to Step 4
7. **Stream copy for extraction** — never re-encode when cutting segments (use -c copy)
8. **One segment at a time** for progress reporting during render
9. **Load references** when needed — scoring-rubric.md for Step 4, caption-styles.md for style questions

## Caption Style Reference

| Style | Font | Look | Best for |
|-------|------|------|----------|
| **hormozi** | Montserrat Bold | ALL CAPS, pop-in, yellow active word | Business, education, motivation |
| **mrbeast** | Bangers | Bouncy scale, rotating bright colors | Entertainment, reactions, energy |
| **clean** | Inter Bold | Minimal fade-in, white + shadow | Professional, calm, interviews |

Load `references/caption-styles.md` for detailed visual specs and spring configs.

## Error Recovery

- **Transcription fails**: Check venv activation, try `--model small` for less VRAM
- **Remotion render fails**: Check `cd remotion && npm install`, verify node_modules exists
- **Export fails**: Check FFmpeg version (`ffmpeg -version`), try CPU encoding if NVENC fails
- **Out of disk space**: Clean /tmp/claude-shorts/, check with `df -h /tmp`
