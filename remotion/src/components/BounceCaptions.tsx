import { useCurrentFrame, useVideoConfig, spring } from "remotion";
import { useCaptionPages } from "../hooks/useCaptionPages";
import { BOUNCE_THEME } from "../styles/theme";
import type { Caption } from "../types";

interface BounceCaptionsProps {
  captions: Caption[];
}

/**
 * Bounce-style captions: Bouncy scale spring, rotating bright colors,
 * 1-2 words per page for maximum impact.
 *
 * Font: Bangers (Google Fonts, OFL)
 * Words per page: 1-2 (600ms combine window)
 * Animation: Scale spring 70% → 120% → 100% {mass:1, damping:8}
 */
export const BounceCaptions: React.FC<BounceCaptionsProps> = ({
  captions,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;

  const pages = useCaptionPages(captions, 600);

  const currentPage = pages.find(
    (p) =>
      currentTimeMs >= p.startMs &&
      currentTimeMs < p.startMs + p.durationMs
  );

  if (!currentPage) return null;

  const pageStartFrame = Math.floor((currentPage.startMs / 1000) * fps);
  const localFrame = frame - pageStartFrame;
  const pageIndex = pages.indexOf(currentPage);

  // Bouncy scale spring: starts at 0.7, overshoots to ~1.2, settles at 1.0
  const rawScale = spring({
    frame: localFrame,
    fps,
    config: { mass: 1, damping: 8, stiffness: 180 },
  });
  const scale = 0.7 + rawScale * 0.3;

  // Rotating color per page
  const color = BOUNCE_THEME.rotatingColors[pageIndex % BOUNCE_THEME.rotatingColors.length];

  return (
    <div
      style={{
        position: "absolute",
        bottom: 350,
        left: 40,
        right: 40,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        transform: `scale(${scale})`,
      }}
    >
      <span
        style={{
          fontFamily: "'Bangers', cursive",
          fontSize: 84,
          color,
          textShadow: `
            4px 4px 0 ${BOUNCE_THEME.shadowColor},
            -4px -4px 0 ${BOUNCE_THEME.shadowColor},
            4px -4px 0 ${BOUNCE_THEME.shadowColor},
            -4px 4px 0 ${BOUNCE_THEME.shadowColor}
          `,
          textAlign: "center",
          lineHeight: 1.0,
          textTransform: "uppercase",
        }}
      >
        {currentPage.text.trim().toUpperCase()}
      </span>
    </div>
  );
};
