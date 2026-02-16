import { AbsoluteFill } from "remotion";
import { VideoFrame } from "./components/VideoFrame";
import { Captions } from "./components/Captions";
import { HookOverlay } from "./components/HookOverlay";
import { ProgressBar } from "./components/ProgressBar";
import { fontFaceCSS } from "./styles/fonts";
import type { ShortVideoProps } from "./types";

export const ShortVideo: React.FC<ShortVideoProps> = ({
  clipSrc,
  sourceWidth,
  sourceHeight,
  crop,
  cropKeyframes,
  captions,
  captionStyle,
  hookLine1,
  hookLine2,
  showProgressBar,
  durationInSeconds,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* Load custom fonts for captions and hook overlay */}
      <style dangerouslySetInnerHTML={{ __html: fontFaceCSS }} />

      {/* Reframed video (cropped and scaled to fill 1080x1920) */}
      <VideoFrame
        clipSrc={clipSrc}
        sourceWidth={sourceWidth}
        sourceHeight={sourceHeight}
        crop={crop}
        cropKeyframes={cropKeyframes}
      />

      {/* Animated captions */}
      <Captions captions={captions} style={captionStyle} />

      {/* Hook text overlay (first 3.5 seconds) */}
      {(hookLine1 || hookLine2) && (
        <HookOverlay line1={hookLine1 ?? ""} line2={hookLine2 ?? ""} />
      )}

      {/* Progress bar at bottom */}
      {showProgressBar && (
        <ProgressBar durationInSeconds={durationInSeconds} />
      )}
    </AbsoluteFill>
  );
};
