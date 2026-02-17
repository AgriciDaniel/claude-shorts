---
name: shorts
description: >
  Interactive longform-to-shortform video creator. Extracts viral-ready short clips
  from long videos using Claude as the orchestrator. Transcribes with faster-whisper
  (GPU), Claude scores and presents candidate segments interactively, user picks and
  adjusts, Remotion renders premium animated captions (Bold/Bounce/Clean styles),
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

# shorts — Interactive Shortform Video Creator

You are an interactive shortform video producer. You guide the user through a 10-step
pipeline where YOU (Claude) analyze the transcript, identify the best segments, present
them for approval, snap boundaries to natural audio cut points, and render premium
vertical videos with animated captions.

## Pre-Flight

Before starting, locate the project root:
```bash
# Try common locations in priority order
SHORTS_ROOT=""
for dir in "$HOME/.claude/skills/shorts" "$HOME/.claude/skills/claude-shorts" "$HOME/claude-shorts" "$(pwd)"; do
    if [ -f "$dir/SKILL.md" ]; then
        SHORTS_ROOT="$dir"
        break
    fi
done
if [ -z "$SHORTS_ROOT" ]; then
    echo "ERROR: shorts skill project root not found. Please run from the project directory or install with install.sh"
fi
```

Set up the temp directory (configurable via `SHORTS_TMP` environment variable):
```bash
SHORTS_TMP="${SHORTS_TMP:-/tmp/claude-shorts}"
mkdir -p "$SHORTS_TMP/clips"
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

Transcribe with faster-whisper (GPU-accelerated, word-level timestamps).
Audio extraction is handled internally by transcribe.py:
```bash
VENV="$HOME/.video-skill"
[ -d "$VENV" ] || VENV="$HOME/.shorts-skill"
source "$VENV/bin/activate"

python3 "$SHORTS_ROOT/scripts/transcribe.py" INPUT_FILE \
    --output $SHORTS_TMP/transcript.json
```

Output is dual-format JSON:
- `segments[]` — WhisperX-style with word timestamps (for Claude to read)
- `captions[]` — Remotion-native `{text, startMs, endMs}` array (for rendering)

Report to user: transcription time, word count, language detected.

### Step 3: DETECT CONTENT TYPE

Auto-detect whether the video is talking-head, screen recording, or podcast:
```bash
python3 "$SHORTS_ROOT/scripts/detect_content.py" INPUT_FILE \
    --output $SHORTS_TMP/content_type.json
```

Report detected type to user. Ask if they want to override.
- **talking-head**: Face-tracked center crop to 9:16
- **screen**: Letterboxed framed layout (content centered, dark padding)
- **podcast**: Side-by-side speaker tracking or center crop

### Step 4: ANALYZE — Claude Reads Transcript

Read the full transcript directly:
```
Read $SHORTS_TMP/transcript.json
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

**Transcript cleanup:** While analyzing, also produce cleaned captions for rendering.
Read the `captions[]` array from transcript.json, then:
1. Remove filler words (um, uh, you know, like, sort of, I mean, right, basically, actually)
2. Fix obvious transcription errors based on surrounding context
3. Consolidate incomplete sentence fragments where appropriate
4. **Keep all timestamps unchanged** — only modify the `text` field

Write the cleaned transcript to `$SHORTS_TMP/transcript_cleaned.json` using the same
JSON structure as transcript.json (both `segments` and `captions` arrays). The `captions`
array should contain the cleaned text; copy `segments` as-is.

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
2. **Caption style?** — bold (ALL CAPS pop-in), bounce (bouncy colorful), clean (minimal fade)
3. **Platform?** — youtube, tiktok, instagram, or all

### Step 6: APPROVE — Interactive Adjustment Loop

After user selects segments:
- Show selected segments with exact timestamps
- Allow timecode adjustments ("move segment 2 start back 3 seconds")
- Confirm final selections
- Estimate render time (~15-30s per segment with Remotion)

Write approved segments to:
```bash
cat > $SHORTS_TMP/approved_segments.json << 'EOF'
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
  "style": "bold",
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
    --segments $SHORTS_TMP/approved_segments.json \
    --transcript $SHORTS_TMP/transcript.json \
    --input-video INPUT_FILE \
    --output $SHORTS_TMP/snapped_segments.json
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
Use the snapped start/end times from `$SHORTS_TMP/snapped_segments.json`:
```bash
ffmpeg -y -ss START -to END -i INPUT_FILE -c copy \
    $SHORTS_TMP/clips/clip_01.mp4
```

Compute reframe coordinates for each clip:
```bash
python3 "$SHORTS_ROOT/scripts/compute_reframe.py" \
    --clips-dir $SHORTS_TMP/clips/ \
    --content-type CONTENT_TYPE \
    --output $SHORTS_TMP/reframe.json
```

Report to user: clips extracted, content type per clip, reframe strategy.

### Step 9: RENDER via Remotion

Render all snapped segments with the selected caption style:
```bash
node "$SHORTS_ROOT/remotion/render.mjs" \
    --segments $SHORTS_TMP/snapped_segments.json \
    --reframe $SHORTS_TMP/reframe.json \
    --captions $SHORTS_TMP/transcript_cleaned.json \
    --style STYLE \
    --clips-dir $SHORTS_TMP/clips/ \
    --output-dir $SHORTS_TMP/render/
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
    --input-dir $SHORTS_TMP/render/ \
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

**Post-export validation:** Run validation on all exported files:
```bash
bash "$SHORTS_ROOT/scripts/validate.sh" --output-dir ./shorts/
```

Checks: file is playable, resolution is 1080x1920, audio track exists and isn't silent,
file size is within platform limits, video codec is H.264, duration is 3-90 seconds.
If any file fails, report the issues to the user. Failed files should be re-rendered
or re-exported before delivery.

## Important Rules

1. **Always run preflight** before any processing
2. **Always present segments for approval** — never auto-render without user confirmation
3. **Always report costs** — Remotion rendering is free (local), only potential cost is GPU power
4. **Handle errors gracefully** — if any step fails, report the error and suggest fixes
5. **Clean up on success** — offer to delete $SHORTS_TMP/ after export
6. **Respect the user's choices** — if they say "re-analyze", go back to Step 4
7. **Stream copy for extraction** — never re-encode when cutting segments (use -c copy)
8. **One segment at a time** for progress reporting during render
9. **Load references** when needed — scoring-rubric.md for Step 4, caption-styles.md for style questions

## Caption Style Reference

| Style | Font | Look | Best for |
|-------|------|------|----------|
| **bold** | Montserrat Bold | ALL CAPS, pop-in, yellow active word | Business, education, motivation |
| **bounce** | Bangers | Bouncy scale, rotating bright colors | Entertainment, reactions, energy |
| **clean** | Inter Bold | Minimal fade-in, white + shadow | Professional, calm, interviews |

Load `references/caption-styles.md` for detailed visual specs and spring configs.

## Configurable Parameters

These defaults work well for most content. Offer alternatives when the user has specific needs.

| Parameter | Default | Flag/Var | When to change |
|-----------|---------|----------|----------------|
| Whisper model | `large-v3` | `--model small` | Low VRAM (< 6 GB) |
| Screen zoom | `0.55` | `--zoom 0.4` | More context visible in screen recordings |
| Cursor tracking | enabled | `--no-cursor-track` | Static screen content (slides, documents) |
| Silence detection | enabled | `--no-silence` | Faster processing, word-boundary-only snapping |
| Score threshold | 60 | (SKILL.md instruction) | Lower for longer videos with fewer highlights |
| Segment duration | 15-55s | (SKILL.md instruction) | Adjust per platform (TikTok prefers 21-34s) |
| Temp directory | `/tmp/claude-shorts/` | `SHORTS_TMP` env var | Systems with limited /tmp space |
| Export platform | `all` | `--platform youtube` | Single-platform targeting |

## Error Recovery

- **Transcription fails**: Check venv activation, try `--model small` for less VRAM
- **Remotion render fails**: Check `cd remotion && npm install`, verify node_modules exists
- **Export fails**: Check FFmpeg version (`ffmpeg -version`), try CPU encoding if NVENC fails
- **Out of disk space**: Clean $SHORTS_TMP/, check with `df -h /tmp`
