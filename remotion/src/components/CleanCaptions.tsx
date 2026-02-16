import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { useCaptionPages } from "../hooks/useCaptionPages";
import { CLEAN_THEME } from "../styles/theme";
import type { Caption } from "../types";

interface CleanCaptionsProps {
  captions: Caption[];
}

/**
 * Clean-style captions: Minimal fade-in, white text with subtle shadow,
 * 3-5 words per page for readability.
 *
 * Font: Inter Bold
 * Words per page: 3-5 (1500ms combine window)
 * Animation: Fade-in opacity 0 → 1 over 6 frames
 */
export const CleanCaptions: React.FC<CleanCaptionsProps> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;

  const pages = useCaptionPages(captions, 1500);

  const currentPage = pages.find(
    (p) =>
      currentTimeMs >= p.startMs &&
      currentTimeMs < p.startMs + p.durationMs
  );

  if (!currentPage) return null;

  const pageStartFrame = Math.floor((currentPage.startMs / 1000) * fps);
  const localFrame = frame - pageStartFrame;

  // Fade-in over 6 frames
  const opacity = interpolate(localFrame, [0, 6], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 350,
        left: 60,
        right: 60,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        opacity,
      }}
    >
      {currentPage.tokens.map((token, i) => {
        const isActive =
          currentTimeMs >= token.fromMs && currentTimeMs < token.toMs;

        return (
          <span
            key={`${currentPage.startMs}-${i}`}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontWeight: 700,
              fontSize: 56,
              color: isActive
                ? CLEAN_THEME.activeColor
                : CLEAN_THEME.textColor,
              textShadow: `2px 2px 8px ${CLEAN_THEME.shadowColor}`,
              lineHeight: 1.3,
              textAlign: "center",
              marginRight: 8,
            }}
          >
            {token.text.trim()}
          </span>
        );
      })}
    </div>
  );
};
