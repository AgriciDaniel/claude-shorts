# Changelog

## v1.1.0

- Renamed caption styles from creator names to generic: Bold, Bounce, Clean
- Renamed skill command from `/claude-shorts` to `/shorts`
- Audio loudnorm normalization in export pipeline
- Skip existing exports instead of overwriting
- Use segment ID for clip/output filenames instead of array index
- Render retry logic (1 automatic retry before skipping)
- Snap boundaries tolerance fix for edge-case word alignment
- Batch frame extraction for content detection
- Configurable temp directory via `$SHORTS_TMP`

## v1.0.0 — Initial Release

- 10-step interactive pipeline for longform-to-shortform video creation
- 3 caption styles: Bold, Bounce, Clean
- Remotion v4 rendering with spring animations and word-level karaoke highlighting
- GPU-accelerated transcription via faster-whisper
- Audio-aware boundary snapping (never cuts mid-word or mid-sentence)
- Cursor tracking for screen recordings
- Face tracking for talking-head content
- Platform-optimized export for YouTube Shorts, TikTok, and Instagram Reels
- NVENC GPU encoding with automatic CPU fallback
