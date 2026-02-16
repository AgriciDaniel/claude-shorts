import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

interface HookOverlayProps {
  line1: string;
  line2: string;
}

/**
 * Hook text overlay shown in the first 3.5 seconds.
 * Line 1: Large white text (main hook)
 * Line 2: Smaller cyan text (subtitle/context)
 *
 * Animation: Spring pop-in at 0.3s, fade-out at 3.0s
 */
export const HookOverlay: React.FC<HookOverlayProps> = ({ line1, line2 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeSec = frame / fps;

  // Only show between 0.3s and 3.5s
  if (currentTimeSec < 0.3 || currentTimeSec > 3.5) return null;

  const enterFrame = Math.max(0, frame - Math.floor(0.3 * fps));

  // Pop-in spring
  const scale = spring({
    frame: enterFrame,
    fps,
    config: { mass: 1, damping: 14, stiffness: 200 },
  });

  // Fade-out starting at 3.0s
  const opacity = interpolate(
    currentTimeSec,
    [3.0, 3.5],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 40,
        left: 40,
        right: 40,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 8,
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      {line1 && (
        <div
          style={{
            fontFamily: "'Montserrat', sans-serif",
            fontWeight: 800,
            fontSize: 48,
            color: "white",
            textShadow: "3px 3px 0 black, -3px -3px 0 black, 3px -3px 0 black, -3px 3px 0 black",
            textAlign: "center",
            lineHeight: 1.2,
          }}
        >
          {line1}
        </div>
      )}
      {line2 && (
        <div
          style={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 600,
            fontSize: 28,
            color: "#00BFFF",
            textShadow: "2px 2px 0 black",
            textAlign: "center",
            lineHeight: 1.3,
          }}
        >
          {line2}
        </div>
      )}
    </div>
  );
};
