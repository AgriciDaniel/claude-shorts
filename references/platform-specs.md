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
    -af loudnorm=I=-14:TP=-1:LRA=11 \
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
    -af loudnorm=I=-14:TP=-1:LRA=11 \
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
    -af loudnorm=I=-14:TP=-1:LRA=11 \
    -c:a aac -b:a 128k -ar 44100 \
    -pix_fmt yuv420p -movflags +faststart \
    output_tt.mp4
```

**FFmpeg (NVENC)**:
```bash
ffmpeg -y -i input.mp4 \
    -c:v h264_nvenc -preset p5 -tune hq \
    -cq 18 -maxrate 10M -bufsize 20M \
    -af loudnorm=I=-14:TP=-1:LRA=11 \
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
    -af loudnorm=I=-14:TP=-1:LRA=11 \
    -c:a aac -b:a 128k -ar 44100 \
    -pix_fmt yuv420p -movflags +faststart \
    output_ig.mp4
```

## Safe Zones

All platforms have UI overlays that consume screen space. Values below are the median of 10+ community-measured sources at 1080x1920 (no platform publishes official pixel specs). Bottom margins vary with caption/description length — values reflect typical organic content.

| Zone | TikTok | YouTube Shorts | Instagram Reels | Universal |
|------|--------|----------------|-----------------|-----------|
| Top | 150px | 150px | 210px | 210px |
| Bottom | 320px | 350px | 340px | 450px |
| Left | 60px | 60px | 40px | 60px |
| Right | 120px | 150px | 100px | 150px |
| Safe Area | 900x1450px | 870x1420px | 940x1370px | 870x1260px |

Caption position at 350px from bottom clears TikTok (320px) and Instagram (340px). For YouTube Shorts safety, 400px+ is recommended. For universal cross-platform safety, 450px+ is ideal.

## Audio Normalization

All exports normalize audio to -14 LUFS (EBU R128) using FFmpeg's `loudnorm` filter:
- `I=-14` — integrated loudness target (-14 LUFS, YouTube/streaming standard)
- `TP=-1` — true peak max (-1 dBFS headroom, prevents clipping)
- `LRA=11` — loudness range (dynamic variation allowed)

## NVENC Encoding Notes

For RTX GPUs (this system: RTX 5070 Ti):
- `h264_nvenc -preset p5 -tune hq` provides best quality
- 5-10x faster than CPU `-preset slow`
- Quality is comparable to CPU at same bitrate
- `-preset p7` for maximum quality (slower but still faster than CPU)
- Always verify NVENC availability: `ffmpeg -encoders | grep nvenc`
