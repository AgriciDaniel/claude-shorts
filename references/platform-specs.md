# Platform Export Specifications

Encoding specs for each target platform, optimized for quality and upload compatibility.

## YouTube Shorts

| Property | Value |
|----------|-------|
| Resolution | 1080x1920 |
| Aspect Ratio | 9:16 |
| Max Duration | 60 seconds |
| Video Codec | H.264 (AVC) |
| Profile | High |
| Level | 4.2 |
| Bitrate | 12 Mbps (target) |
| Max Bitrate | 14 Mbps |
| Buffer Size | 24 Mbps |
| Audio Codec | AAC |
| Audio Bitrate | 192 kbps |
| Sample Rate | 48 kHz |
| Container | MP4 |
| Pixel Format | yuv420p |
| Max File Size | 256 MB |

**FFmpeg (CPU)**:
```bash
ffmpeg -y -i input.mp4 \
    -c:v libx264 -preset slow \
    -b:v 12M -maxrate 14M -bufsize 24M \
    -profile:v high -level 4.2 \
    -c:a aac -b:a 192k -ar 48000 \
    -pix_fmt yuv420p -movflags +faststart \
    output_yt.mp4
```

**FFmpeg (NVENC)**:
```bash
ffmpeg -y -i input.mp4 \
    -c:v h264_nvenc -preset p5 -tune hq \
    -b:v 12M -maxrate 14M -bufsize 24M \
    -profile:v high -level 4.2 \
    -c:a aac -b:a 192k -ar 48000 \
    -pix_fmt yuv420p -movflags +faststart \
    output_yt.mp4
```

## TikTok

| Property | Value |
|----------|-------|
| Resolution | 1080x1920 |
| Aspect Ratio | 9:16 |
| Max Duration | 60 seconds (3 min with account) |
| Video Codec | H.264 (AVC) |
| Bitrate Mode | CRF 18 (quality-based) |
| Max Bitrate | 10 Mbps |
| Buffer Size | 20 Mbps |
| Audio Codec | AAC |
| Audio Bitrate | 128 kbps |
| Sample Rate | 44.1 kHz |
| Container | MP4 |
| Pixel Format | yuv420p |
| Max File Size | 287 MB |

**FFmpeg (CPU)**:
```bash
ffmpeg -y -i input.mp4 \
    -c:v libx264 -preset slow -crf 18 \
    -maxrate 10M -bufsize 20M \
    -c:a aac -b:a 128k -ar 44100 \
    -pix_fmt yuv420p -movflags +faststart \
    output_tt.mp4
```

**FFmpeg (NVENC)**:
```bash
ffmpeg -y -i input.mp4 \
    -c:v h264_nvenc -preset p5 -tune hq \
    -cq 18 -maxrate 10M -bufsize 20M \
    -c:a aac -b:a 128k -ar 44100 \
    -pix_fmt yuv420p -movflags +faststart \
    output_tt.mp4
```

## Instagram Reels

| Property | Value |
|----------|-------|
| Resolution | 1080x1920 |
| Aspect Ratio | 9:16 |
| Max Duration | 90 seconds |
| Video Codec | H.264 (AVC) |
| Profile | High |
| Level | 4.2 |
| Bitrate | 4.5 Mbps (target) |
| Max Bitrate | 5 Mbps |
| Buffer Size | 10 Mbps |
| Audio Codec | AAC |
| Audio Bitrate | 128 kbps |
| Sample Rate | 44.1 kHz |
| Container | MP4 |
| Pixel Format | yuv420p |
| Max File Size | 250 MB |

**FFmpeg (CPU)**:
```bash
ffmpeg -y -i input.mp4 \
    -c:v libx264 -preset slow \
    -b:v 4500k -maxrate 5000k -bufsize 10M \
    -profile:v high -level 4.2 \
    -c:a aac -b:a 128k -ar 44100 \
    -pix_fmt yuv420p -movflags +faststart \
    output_ig.mp4
```

## Safe Zones

All platforms have UI overlays. Keep critical content within:

| Zone | TikTok | YouTube Shorts | Instagram Reels |
|------|--------|----------------|-----------------|
| Top | 150px | 120px | 120px |
| Bottom | 150px | 120px | 150px |
| Left | 64px | 48px | 48px |
| Right | 64px | 48px | 48px |

Caption position at 350px from bottom clears all platforms.

## NVENC Encoding Notes

For RTX GPUs (this system: RTX 5070 Ti):
- `h264_nvenc -preset p5 -tune hq` provides best quality
- 5-10x faster than CPU `-preset slow`
- Quality is comparable to CPU at same bitrate
- `-preset p7` for maximum quality (slower but still faster than CPU)
- Always verify NVENC availability: `ffmpeg -encoders | grep nvenc`
