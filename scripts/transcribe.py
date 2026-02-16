#!/usr/bin/env python3
"""Transcribe video with faster-whisper, output dual-format JSON.

Produces both WhisperX-style segments (for Claude to read) and
Remotion-native captions (for rendering with @remotion/captions).

Usage:
    python3 transcribe.py INPUT_VIDEO --output transcript.json
    python3 transcribe.py INPUT_VIDEO --output transcript.json --model large-v3
    python3 transcribe.py INPUT_VIDEO --output transcript.json --model small  # low VRAM

Output JSON:
{
    "language": "en",
    "duration": 3600.0,
    "word_count": 12000,
    "segments": [
        {
            "start": 0.0, "end": 4.5,
            "text": "Hello and welcome to the show",
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.3},
                {"word": "and", "start": 0.35, "end": 0.5},
                ...
            ]
        },
        ...
    ],
    "captions": [
        {"text": "Hello", "startMs": 0, "endMs": 300},
        {"text": " and", "startMs": 350, "endMs": 500},
        ...
    ]
}
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time


def extract_audio(video_path, audio_path):
    """Extract audio from video as 16kHz mono WAV."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(json.dumps({"error": f"Audio extraction failed: {result.stderr[-300:]}"}))
        sys.exit(1)


def transcribe(audio_path, model_size="large-v3", device="auto", compute_type="auto"):
    """Run faster-whisper transcription with word-level timestamps."""
    from faster_whisper import WhisperModel

    # Auto-detect device
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"

    # Auto-detect compute type
    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments_iter, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=200,
        ),
    )

    segments = []
    captions = []

    for segment in segments_iter:
        seg_data = {
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip(),
            "words": [],
        }

        if segment.words:
            for word in segment.words:
                seg_data["words"].append({
                    "word": word.word.strip(),
                    "start": round(word.start, 3),
                    "end": round(word.end, 3),
                })

                # Remotion caption format: {text, startMs, endMs}
                # faster-whisper preserves leading spaces in word.word
                captions.append({
                    "text": word.word,
                    "startMs": int(word.start * 1000),
                    "endMs": int(word.end * 1000),
                })

        segments.append(seg_data)

    return segments, captions, info, device, compute_type


def main():
    parser = argparse.ArgumentParser(description="Transcribe video with faster-whisper")
    parser.add_argument("input", help="Input video or audio file")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--model", default="large-v3",
                        help="Whisper model size (default: large-v3)")
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"],
                        help="Compute device (default: auto)")
    parser.add_argument("--compute-type", default="auto",
                        choices=["auto", "float16", "int8", "float32"],
                        help="Compute type (default: auto)")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(json.dumps({"error": f"Input file not found: {args.input}"}))
        sys.exit(1)

    start_time = time.time()

    # Extract audio if input is video
    audio_path = args.input
    tmp_audio = None

    # Check if input has video stream (i.e., it's a video file, not audio)
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0", args.input],
        capture_output=True, text=True
    )
    if "video" in probe.stdout:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_audio = tmp_file.name
        tmp_file.close()
        audio_path = tmp_audio
        extract_audio(args.input, audio_path)

    try:
        segments, captions, info, actual_device, actual_compute = transcribe(
            audio_path, args.model, args.device, args.compute_type
        )
    finally:
        if tmp_audio and os.path.exists(tmp_audio):
            os.unlink(tmp_audio)

    elapsed = time.time() - start_time

    # Get video duration
    duration_cmd = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", args.input],
        capture_output=True, text=True
    )
    duration = float(duration_cmd.stdout.strip()) if duration_cmd.stdout.strip() else 0

    # Count total words
    word_count = sum(len(seg.get("words", [])) for seg in segments)

    output = {
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(duration, 1),
        "word_count": word_count,
        "model": args.model,
        "device": actual_device,
        "compute_type": actual_compute,
        "transcription_time_sec": round(elapsed, 1),
        "segments": segments,
        "captions": captions,
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary (not the full transcript)
    summary = {
        "action": "transcribe",
        "input": args.input,
        "output": args.output,
        "language": info.language,
        "duration": round(duration, 1),
        "word_count": word_count,
        "segment_count": len(segments),
        "caption_count": len(captions),
        "model": args.model,
        "transcription_time_sec": round(elapsed, 1),
        "realtime_factor": round(duration / elapsed, 1) if elapsed > 0 else 0,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
