# Remotion Patterns and Best Practices

Key patterns used in claude-shorts, verified against Remotion v4.0.422.

## Bundle-Once-Render-Many

For batch rendering multiple shorts, bundle the project once and reuse the Chrome instance:

```js
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition, openBrowser } from "@remotion/renderer";

// Bundle once
const serveUrl = await bundle({ entryPoint: "src/index.ts" });

// Open shared browser
const browser = await openBrowser("chrome");

try {
  for (const segment of segments) {
    // selectComposition resolves calculateMetadata for dynamic duration
    const composition = await selectComposition({
      serveUrl,
      id: "ShortVideo",
      inputProps: segment.props,
      puppeteerInstance: browser,
    });

    await renderMedia({
      composition,
      serveUrl,
      codec: "h264",
      crf: 18,
      outputLocation: segment.outputPath,
      inputProps: segment.props,
      puppeteerInstance: browser,
    });
  }
} finally {
  await browser.close();
}
```

**Critical**: Always use `selectComposition()` before `renderMedia()`. Never pass inline composition objects. `selectComposition()` evaluates `calculateMetadata` to resolve dynamic duration per segment.

## OffthreadVideo + CSS Reframing

Reframing is done via CSS transforms on OffthreadVideo, not FFmpeg pre-processing:

```tsx
const scale = outputWidth / crop.w;
const translateX = -crop.x * scale;
const translateY = -crop.y * scale;

<div style={{ width: 1080, height: 1920, overflow: "hidden" }}>
  <OffthreadVideo
    src={clipPath}
    style={{
      width: sourceWidth * scale,
      height: sourceHeight * scale,
      transform: `translate(${translateX}px, ${translateY}px)`,
    }}
  />
</div>
```

This avoids double-encoding. Remotion handles the crop during render.

## Spring Animations

Spring configs for each caption style:

```ts
// Bold: Snappy pop-in, slight overshoot
spring({ frame, fps, config: { mass: 1, damping: 12, stiffness: 200 } });
// ~0.4s settle, overshoots to ~1.05

// Bounce: Very bouncy, visible overshoot
spring({ frame, fps, config: { mass: 1, damping: 8, stiffness: 180 } });
// ~0.6s settle, overshoots to ~1.2

// Clean style uses interpolate(), not spring
interpolate(localFrame, [0, 6], [0, 1], { extrapolateRight: "clamp" });
```

Spring values guide:
- `damping < 10`: Visible bounce
- `damping 10-15`: Slight overshoot, professional feel
- `damping > 20`: No overshoot, smooth ease
- `stiffness > 150`: Fast, snappy
- `stiffness < 100`: Slow, gentle

## @remotion/captions API

```ts
import { createTikTokStyleCaptions } from "@remotion/captions";

// Input captions format
type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: null;   // required field, always null for our use
  confidence: null;     // required field, always null for our use
};

// Create pages (groups of words)
const { pages } = createTikTokStyleCaptions({
  captions: remotionCaptions,
  combineTokensWithinMilliseconds: 800, // adjust per style
});

// Page structure
type TikTokPage = {
  text: string;       // Combined text of all tokens
  startMs: number;    // Start time of first token
  durationMs: number; // Duration until end of last token
  tokens: Array<{
    text: string;
    fromMs: number;
    toMs: number;
  }>;
};
```

## calculateMetadata for Dynamic Duration

Each segment has a different duration. Use `calculateMetadata` in the Composition:

```tsx
<Composition
  id="ShortVideo"
  component={ShortVideo}
  width={1080}
  height={1920}
  fps={30}
  durationInFrames={30 * 30} // default, overridden by calculateMetadata
  schema={ShortVideoPropsSchema}
  defaultProps={defaultProps}
  calculateMetadata={({ props }) => ({
    durationInFrames: Math.ceil(props.durationInSeconds * 30),
    fps: 30,
    width: 1080,
    height: 1920,
  })}
/>
```

## Zod Schema Validation

Always define inputProps with Zod schemas for type safety:

```ts
import { z } from "zod";

const ShortVideoPropsSchema = z.object({
  clipSrc: z.string(),
  sourceWidth: z.number(),
  sourceHeight: z.number(),
  crop: CropSchema,
  captions: z.array(CaptionSchema),
  captionStyle: z.enum(["bold", "bounce", "clean"]),
  hookLine1: z.string().optional().default(""),
  hookLine2: z.string().optional().default(""),
  showProgressBar: z.boolean().optional().default(true),
  durationInSeconds: z.number(),
});
```

## File Paths in Render

When rendering headless, `clipSrc` must be an `http://` URL. Remotion's renderer proxy does not support `file://` URLs. The render script starts a local HTTP server on a random port (e.g., `http://127.0.0.1:PORT/clip_01.mp4`) to serve clip files. Do NOT use `staticFile()` for dynamic clip sources — that's for bundled assets only.

## Performance Tips

- Use `OffthreadVideo` (not `Video`) — decodes frames in a separate thread
- Pre-extract segments before rendering (don't seek through long files)
- Use `codec: "h264"` with `crf: 18` for good quality-size balance
- Share browser instance across renders (`openBrowser` + `puppeteerInstance`)
- Bundle once, render many
