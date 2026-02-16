import { useCurrentFrame, useVideoConfig } from "remotion";

interface ProgressBarProps {
  durationInSeconds: number;
}

/**
 * Thin progress bar at the bottom of the video.
 * White bar that fills left-to-right over the video duration.
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  durationInSeconds,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const totalFrames = Math.ceil(durationInSeconds * fps);
  const progress = Math.min(frame / totalFrames, 1);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        width: 1080,
        height: 4,
        backgroundColor: "rgba(255, 255, 255, 0.2)",
      }}
    >
      <div
        style={{
          width: 1080 * progress,
          height: 4,
          backgroundColor: "white",
        }}
      />
    </div>
  );
};
