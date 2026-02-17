import type { Caption, CaptionStyleType } from "../types";
import { BoldCaptions } from "./BoldCaptions";
import { BounceCaptions } from "./BounceCaptions";
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
    case "bold":
      return <BoldCaptions captions={captions} />;
    case "bounce":
      return <BounceCaptions captions={captions} />;
    case "clean":
      return <CleanCaptions captions={captions} />;
    default:
      return <BoldCaptions captions={captions} />;
  }
};
