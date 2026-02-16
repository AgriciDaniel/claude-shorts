import type { Caption, CaptionStyleType } from "../types";
import { HormoziCaptions } from "./HormoziCaptions";
import { MrBeastCaptions } from "./MrBeastCaptions";
import { CleanCaptions } from "./CleanCaptions";

interface CaptionsProps {
  captions: Caption[];
  style: CaptionStyleType;
}

/**
 * Style dispatcher — routes to the correct caption renderer.
 */
export const Captions: React.FC<CaptionsProps> = ({ captions, style }) => {
  if (!captions || captions.length === 0) return null;

  switch (style) {
    case "hormozi":
      return <HormoziCaptions captions={captions} />;
    case "mrbeast":
      return <MrBeastCaptions captions={captions} />;
    case "clean":
      return <CleanCaptions captions={captions} />;
    default:
      return <HormoziCaptions captions={captions} />;
  }
};
