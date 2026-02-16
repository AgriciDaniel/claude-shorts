#!/usr/bin/env python3
"""Snap segment boundaries to natural audio cut points.

Takes proposed segment times and the transcript, then adjusts start/end to:
1. Align with word boundaries (never cut mid-word)
2. Extend to sentence completion if close (within 3s)
3. Pad with silence after the last word
4. Optionally use FFmpeg silencedetect to find natural pauses

Usage:
    python3 snap_boundaries.py \
        --segments /tmp/claude-shorts/approved_segments.json \
        --transcript /tmp/claude-shorts/transcript.json \
        --input-video /path/to/source.mp4 \
        --output /tmp/claude-shorts/snapped_segments.json

Output: Same format as approved_segments.json with adjusted start/end times.
"""
import argparse
import json
import os
import subprocess
import sys


def load_word_timeline(transcript_path):
    """Load word-level timestamps from transcript.

    Returns list of {text, start, end} for every word, sorted by start time.
    """
    with open(transcript_path) as f:
        data = json.load(f)

    words = []

    # Use the segments array which has word-level detail
    for seg in data.get("segments", []):
        for w in seg.get("words", []):
            words.append({
                "text": w["word"].strip(),
                "start": w["start"],
                "end": w["end"],
            })

    # Sort by start time
    words.sort(key=lambda w: w["start"])
    return words


def detect_silences(video_path, min_duration=0.3, noise_threshold=-35):
    """Find silence regions in the audio track using FFmpeg silencedetect.

    Returns list of {start, end} for each silence region.
    """
    cmd = [
        "ffmpeg", "-i", video_path,
        "-af", f"silencedetect=noise={noise_threshold}dB:d={min_duration}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    stderr = result.stderr

    silences = []
    current_start = None

    for line in stderr.split("\n"):
        if "silence_start:" in line:
            try:
                current_start = float(line.split("silence_start:")[1].strip().split()[0])
            except (IndexError, ValueError):
                pass
        elif "silence_end:" in line and current_start is not None:
            try:
                parts = line.split("silence_end:")[1].strip().split()
                end = float(parts[0])
                silences.append({"start": current_start, "end": end})
                current_start = None
            except (IndexError, ValueError):
                pass

    return silences


def find_nearest_silence(silences, target_time, search_window=2.0):
    """Find the silence region closest to target_time within search_window.

    Returns the midpoint of the nearest silence, or None if no silence nearby.
    """
    best = None
    best_dist = float("inf")

    for s in silences:
        mid = (s["start"] + s["end"]) / 2
        dist = abs(mid - target_time)
        if dist < search_window and dist < best_dist:
            best = mid
            best_dist = dist

    return best


def snap_start(words, proposed_start, search_window=1.5):
    """Snap start time to the beginning of the nearest word.

    Looks for a word that starts near proposed_start.
    Prefers snapping to a sentence start (after punctuation) if one is nearby.
    """
    # Find words near the proposed start
    candidates = []
    for i, w in enumerate(words):
        if abs(w["start"] - proposed_start) <= search_window:
            candidates.append((i, w))

    if not candidates:
        return proposed_start

    # Check if any candidate is a sentence start (previous word ends with . ? !)
    sentence_starts = []
    for idx, w in candidates:
        if idx == 0:
            sentence_starts.append((idx, w))
        elif words[idx - 1]["text"].rstrip()[-1:] in ".?!":
            sentence_starts.append((idx, w))

    # Prefer sentence start if available and within window
    if sentence_starts:
        # Pick the one closest to proposed start
        best_idx, best_w = min(sentence_starts, key=lambda x: abs(x[1]["start"] - proposed_start))
        return best_w["start"]

    # Otherwise, snap to nearest word start
    best_idx, best_w = min(candidates, key=lambda x: abs(x[1]["start"] - proposed_start))
    return best_w["start"]


def snap_end(words, proposed_end, search_window=3.0, pad_ms=300):
    """Snap end time to after the last complete sentence.

    Extends to the next sentence boundary (. ? !) if within search_window.
    Adds pad_ms of silence after the last word.
    """
    pad = pad_ms / 1000.0

    # Find the last word that ends at or before proposed_end
    last_word_idx = None
    for i, w in enumerate(words):
        if w["end"] <= proposed_end + 0.5:  # small tolerance
            last_word_idx = i

    if last_word_idx is None:
        return proposed_end

    # Check if the last word ends a sentence
    last_word = words[last_word_idx]
    if last_word["text"].rstrip()[-1:] in ".?!":
        return last_word["end"] + pad

    # Look forward for the next sentence-ending word within search_window
    for i in range(last_word_idx + 1, len(words)):
        w = words[i]
        if w["start"] > proposed_end + search_window:
            break
        if w["text"].rstrip()[-1:] in ".?!":
            return w["end"] + pad

    # No sentence boundary found nearby — snap to nearest word end
    # Find the word whose end is closest to proposed_end
    candidates = []
    for i, w in enumerate(words):
        if abs(w["end"] - proposed_end) <= 1.0:
            candidates.append(w)

    if candidates:
        best = min(candidates, key=lambda w: abs(w["end"] - proposed_end))
        return best["end"] + pad

    return proposed_end


def snap_segment(words, silences, seg, video_duration):
    """Snap a single segment's boundaries.

    Returns adjusted (start, end) tuple.
    """
    proposed_start = seg["start"]
    proposed_end = seg["end"]

    # Step 1: Snap to word boundaries
    new_start = snap_start(words, proposed_start)
    new_end = snap_end(words, proposed_end)

    # Step 2: If we have silence data, try to cut at silence points
    if silences:
        # For start: prefer cutting at a silence just before the first word
        silence_start = find_nearest_silence(silences, new_start, search_window=1.5)
        if silence_start is not None and silence_start <= new_start:
            new_start = silence_start

        # For end: prefer cutting at a silence just after the last word
        silence_end = find_nearest_silence(silences, new_end, search_window=2.0)
        if silence_end is not None and silence_end >= new_end - 0.5:
            new_end = silence_end

    # Clamp to video duration
    new_start = max(0.0, new_start)
    new_end = min(video_duration, new_end)

    # Ensure minimum duration (5s) and maximum (60s)
    if new_end - new_start < 5.0:
        new_end = min(new_start + 5.0, video_duration)
    if new_end - new_start > 60.0:
        new_end = new_start + 60.0

    return round(new_start, 3), round(new_end, 3)


def main():
    parser = argparse.ArgumentParser(description="Snap segment boundaries to audio")
    parser.add_argument("--segments", required=True, help="Approved segments JSON")
    parser.add_argument("--transcript", required=True, help="Transcript JSON")
    parser.add_argument("--input-video", required=True, help="Source video for silence detection")
    parser.add_argument("--output", required=True, help="Output snapped segments JSON")
    parser.add_argument("--no-silence", action="store_true",
                        help="Skip silence detection (word-boundary snapping only)")

    args = parser.parse_args()

    # Load data
    words = load_word_timeline(args.transcript)
    if not words:
        print(json.dumps({"error": "No word-level timestamps found in transcript"}))
        sys.exit(1)

    with open(args.segments) as f:
        segments_data = json.load(f)

    # Get video duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", args.input_video],
        capture_output=True, text=True
    )
    video_duration = float(result.stdout.strip())

    # Detect silences (unless disabled)
    silences = []
    if not args.no_silence:
        silences = detect_silences(args.input_video)

    # Snap each segment
    adjustments = []
    for seg in segments_data["segments"]:
        old_start = seg["start"]
        old_end = seg["end"]

        new_start, new_end = snap_segment(words, silences, seg, video_duration)

        seg["start"] = new_start
        seg["end"] = new_end
        seg["duration"] = round(new_end - new_start, 3)

        adj = {
            "id": seg.get("id", "?"),
            "old": f"{old_start:.1f}-{old_end:.1f}",
            "new": f"{new_start:.3f}-{new_end:.3f}",
            "delta_start": f"{(new_start - old_start)*1000:+.0f}ms",
            "delta_end": f"{(new_end - old_end)*1000:+.0f}ms",
        }
        adjustments.append(adj)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(segments_data, f, indent=2)

    # Print summary
    print(json.dumps({
        "action": "snap_boundaries",
        "segments_processed": len(adjustments),
        "silences_detected": len(silences),
        "word_count": len(words),
        "adjustments": adjustments,
    }, indent=2))


if __name__ == "__main__":
    main()
