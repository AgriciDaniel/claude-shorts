import { useMemo } from "react";
import { createTikTokStyleCaptions } from "@remotion/captions";
import type { Caption } from "../types";

/**
 * Converts word-level captions into TikTok-style pages using
 * @remotion/captions createTikTokStyleCaptions().
 *
 * Each page groups N words together based on combineTokensWithinMilliseconds.
 * Returns pages with: text, startMs, durationMs, tokens[{text, fromMs, toMs}]
 */
export const useCaptionPages = (
  captions: Caption[],
  combineMs: number = 800
) => {
  return useMemo(() => {
    if (!captions || captions.length === 0) return [];

    // Convert our Caption format to Remotion's expected format
    const remotionCaptions = captions.map((c) => ({
      text: c.text,
      startMs: c.startMs,
      endMs: c.endMs,
      timestampMs: null as number | null,
      confidence: null as number | null,
    }));

    const { pages } = createTikTokStyleCaptions({
      captions: remotionCaptions,
      combineTokensWithinMilliseconds: combineMs,
    });

    return pages;
  }, [captions, combineMs]);
};
