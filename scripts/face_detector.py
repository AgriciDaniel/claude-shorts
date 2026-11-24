"""Face boxes via MediaPipe Tasks BlazeFace short-range model (Tasks has no full-range variant)."""
import urllib.request
from collections import namedtuple
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

Box = namedtuple("Box", "xmin ymin width height")

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_detector/"
    "blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
)
MODEL_PATH = Path.home() / ".cache" / "claude-shorts" / "blaze_face_short_range.tflite"


def create_detector():
    if not MODEL_PATH.exists():
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        partial = MODEL_PATH.with_suffix(".part")
        urllib.request.urlretrieve(MODEL_URL, partial)
        partial.rename(MODEL_PATH)
    options = vision.FaceDetectorOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.IMAGE,
        min_detection_confidence=0.5,
    )
    return vision.FaceDetector.create_from_options(options)


def find_faces(detector, bgr):
    height, width = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    return [
        Box(b.origin_x / width, b.origin_y / height, b.width / width, b.height / height)
        for b in (d.bounding_box for d in result.detections)
    ]
