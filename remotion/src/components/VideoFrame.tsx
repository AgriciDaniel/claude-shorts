import { OffthreadVideo, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { Crop, CropKeyframe } from "../types";

interface VideoFrameProps {
  clipSrc: string;
  sourceWidth: number;
  sourceHeight: number;
  crop: Crop;
  cropKeyframes?: CropKeyframe[];
}

/**
 * Renders the reframed video using OffthreadVideo + CSS transforms.
 *
 * Supports two modes:
 * 1. Static crop: uses crop.x directly (no keyframes)
 * 2. Animated pan: interpolates crop.x from keyframes (cursor tracking)
 *
 * Strategy: The source video is scaled and positioned so that only the
 * cropped region is visible within the 1080x1920 container. Uses
 * overflow:hidden to clip, and CSS transform to position the crop area.
 */
export const VideoFrame: React.FC<VideoFrameProps> = ({
  clipSrc,
  sourceWidth,
  sourceHeight,
  crop,
  cropKeyframes,
}) => {
  if (!clipSrc) return null;

  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Scale factor: how much to scale source so crop.w fills 1080px
  const outputWidth = 1080;
  const outputHeight = 1920;
  const scale = outputWidth / crop.w;

  // Determine current crop X (animated or static)
  let cropX = crop.x;
  if (cropKeyframes && cropKeyframes.length >= 2) {
    const times = cropKeyframes.map((k) => k.t);
    const xPositions = cropKeyframes.map((k) => k.x);
    cropX = interpolate(currentTime, times, xPositions, {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  // Scaled source dimensions
  const scaledWidth = sourceWidth * scale;
  const scaledHeight = sourceHeight * scale;

  // Offset to position the crop region at (0,0)
  const translateX = -cropX * scale;
  const translateY = -crop.y * scale;

  // Auto-detect framed layout: video doesn't fill full output height.
  // Position in content zone (below 200px hook text area) for screen recordings.
  const hookZone = 200;
  const topOffset = scaledHeight < outputHeight ? hookZone : 0;

  return (
    <div
      style={{
        position: "absolute",
        top: topOffset,
        left: 0,
        width: outputWidth,
        height: scaledHeight < outputHeight ? scaledHeight : outputHeight,
        overflow: "hidden",
      }}
    >
      <OffthreadVideo
        src={clipSrc}
        style={{
          position: "absolute",
          width: scaledWidth,
          height: scaledHeight,
          transform: `translate(${translateX}px, ${translateY}px)`,
        }}
      />
    </div>
  );
};
