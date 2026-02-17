import { z } from "zod";

export const CaptionSchema = z.object({
  text: z.string(),
  startMs: z.number(),
  endMs: z.number(),
});

export type Caption = z.infer<typeof CaptionSchema>;

export const CropSchema = z.object({
  x: z.number(),
  y: z.number(),
  w: z.number(),
  h: z.number(),
});

export type Crop = z.infer<typeof CropSchema>;

export const CropKeyframeSchema = z.object({
  t: z.number(),
  x: z.number(),
});

export type CropKeyframe = z.infer<typeof CropKeyframeSchema>;

export const CaptionStyle = z.enum(["bold", "bounce", "clean"]);
export type CaptionStyleType = z.infer<typeof CaptionStyle>;

export const ShortVideoPropsSchema = z.object({
  clipSrc: z.string(),
  sourceWidth: z.number(),
  sourceHeight: z.number(),
  crop: CropSchema,
  cropKeyframes: z.array(CropKeyframeSchema).optional().default([]),
  captions: z.array(CaptionSchema),
  captionStyle: CaptionStyle,
  hookLine1: z.string().optional().default(""),
  hookLine2: z.string().optional().default(""),
  showProgressBar: z.boolean().optional().default(true),
  durationInSeconds: z.number(),
});

export type ShortVideoProps = z.infer<typeof ShortVideoPropsSchema>;
