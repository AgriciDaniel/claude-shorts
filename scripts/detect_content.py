#!/usr/bin/env python3
"""Auto-detect video content type: talking-head, screen recording, or podcast.

Samples N frames evenly across the video, runs MediaPipe face detection,
and classifies based on face count, size, and position patterns.

Usage:
    python3 detect_content.py INPUT_VIDEO --output content_type.json

Output:
{
    "content_type": "talking-head",
    "confidence": 0.92,
    "face_stats": {"avg_count": 1.0, "avg_size_pct": 15.2, "center_bias": 0.85},
    "frames_sampled": 10
}

Classification rules:
- talking-head: 1 face, large (>8% frame area), centered
- podcast: 2+ faces consistently, medium size (5-15%)
- screen: <0.5 avg faces OR very small faces (<5%) — code, slides, browser
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time


def sample_frames(video_path, num_frames=10):
    """Extract N evenly-spaced frames from video as JPEG files."""
    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    try:
        duration = float(result.stdout.strip())
    except (ValueError, AttributeError):
        print(json.dumps({"error": f"Could not determine video duration: {video_path}"}))
        sys.exit(1)

    tmpdir = tempfile.mkdtemp(prefix="detect_content_")
    timestamps = [duration * (i + 0.5) / num_frames for i in range(num_frames)]
    frame_paths = []

    for i, ts in enumerate(timestamps):
        out_path = os.path.join(tmpdir, f"frame_{i:03d}.jpg")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(ts), "-i", video_path,
             "-vframes", "1", "-q:v", "2", out_path],
            capture_output=True, text=True
        )
        if os.path.exists(out_path):
            frame_paths.append(out_path)

    return frame_paths, tmpdir


def detect_faces(frame_paths):
    """Run MediaPipe face detection on frames, return stats."""
    import mediapipe as mp
    import cv2
    import numpy as np

    mp_face = mp.solutions.face_detection
    detector = mp_face.FaceDetection(
        model_selection=1,  # Full range model (works for far faces too)
        min_detection_confidence=0.5
    )

    face_counts = []
    face_sizes = []  # as percentage of frame area
    face_centers_x = []  # normalized x position (0-1)

    for path in frame_paths:
        img = cv2.imread(path)
        if img is None:
            continue

        h, w = img.shape[:2]
        frame_area = h * w

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = detector.process(rgb)

        if results.detections:
            face_counts.append(len(results.detections))
            for det in results.detections:
                bbox = det.location_data.relative_bounding_box
                face_w = bbox.width * w
                face_h = bbox.height * h
                face_area_pct = (face_w * face_h) / frame_area * 100
                face_sizes.append(face_area_pct)
                center_x = bbox.xmin + bbox.width / 2
                face_centers_x.append(center_x)
        else:
            face_counts.append(0)

    detector.close()

    avg_count = float(np.mean(face_counts)) if face_counts else 0
    avg_size = float(np.mean(face_sizes)) if face_sizes else 0
    center_bias = 0.0
    if face_centers_x:
        # How close to center (0.5)? 1.0 = perfectly centered
        center_bias = 1.0 - float(np.mean([abs(x - 0.5) for x in face_centers_x])) * 2

    return {
        "avg_count": round(avg_count, 2),
        "avg_size_pct": round(avg_size, 2),
        "center_bias": round(center_bias, 3),
        "frames_with_faces": sum(1 for c in face_counts if c > 0),
        "total_frames": len(face_counts),
    }


def classify(face_stats):
    """Classify content type based on face detection stats."""
    avg_count = face_stats["avg_count"]
    avg_size = face_stats["avg_size_pct"]
    center_bias = face_stats["center_bias"]
    face_ratio = face_stats["frames_with_faces"] / max(face_stats["total_frames"], 1)

    # Screen recording: few/no faces or very small faces
    if avg_count < 0.5 or (avg_size < 5 and face_ratio < 0.5):
        confidence = min(1.0, (1.0 - avg_count) * 0.5 + (1.0 - face_ratio) * 0.5)
        return "screen", round(confidence, 3)

    # Podcast: multiple faces consistently
    if avg_count >= 1.8 and face_ratio > 0.7:
        confidence = min(1.0, (avg_count - 1.0) * 0.3 + face_ratio * 0.3 + 0.4)
        return "podcast", round(confidence, 3)

    # Talking head: single face, large, centered
    if avg_count >= 0.5 and avg_size >= 5:
        confidence = min(1.0, center_bias * 0.4 + min(avg_size / 20, 1.0) * 0.3 + face_ratio * 0.3)
        return "talking-head", round(confidence, 3)

    # Default to screen if uncertain
    return "screen", 0.5


def main():
    parser = argparse.ArgumentParser(description="Detect video content type")
    parser.add_argument("input", help="Input video file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--frames", type=int, default=10,
                        help="Number of frames to sample (default: 10)")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(json.dumps({"error": f"Input file not found: {args.input}"}))
        sys.exit(1)

    start = time.time()

    # Sample frames
    frame_paths, tmpdir = sample_frames(args.input, args.frames)

    if not frame_paths:
        print(json.dumps({"error": "No frames could be extracted"}))
        sys.exit(1)

    # Detect faces
    face_stats = detect_faces(frame_paths)

    # Classify
    content_type, confidence = classify(face_stats)

    elapsed = time.time() - start

    # Clean up temp frames
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    output = {
        "content_type": content_type,
        "confidence": confidence,
        "face_stats": face_stats,
        "frames_sampled": len(frame_paths),
        "detection_time_sec": round(elapsed, 2),
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
