import { Composition } from "remotion";
import { ShortVideo } from "./ShortVideo";
import { ShortVideoPropsSchema } from "./types";

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="ShortVideo"
        component={ShortVideo}
        width={1080}
        height={1920}
        fps={30}
        durationInFrames={30 * 30}
        schema={ShortVideoPropsSchema}
        defaultProps={{
          clipSrc: "",
          sourceWidth: 1920,
          sourceHeight: 1080,
          crop: { x: 0, y: 0, w: 607, h: 1080 },
          cropKeyframes: [],
          captions: [],
          captionStyle: "hormozi" as const,
          hookLine1: "",
          hookLine2: "",
          showProgressBar: true,
          durationInSeconds: 30,
        }}
        calculateMetadata={({ props }) => {
          return {
            durationInFrames: Math.ceil(props.durationInSeconds * 30),
            fps: 30,
            width: 1080,
            height: 1920,
          };
        }}
      />
    </>
  );
};
