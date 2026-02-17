# Caption Styles — Visual Specifications

Three premium caption presets for different content tones. Each uses `@remotion/captions` createTikTokStyleCaptions() for word-level timing.

## Bold Style

Best for: Business, education, motivation, "guru" content.

| Property | Value |
|----------|-------|
| Font | Montserrat Bold (800 weight) |
| Font Size | 72px |
| Text Transform | UPPERCASE |
| Words Per Page | 2-3 |
| Combine Window | 800ms |
| Text Color | White (#FFFFFF) |
| Active Word | Yellow (#FFD700) |
| Text Shadow | 3px solid black outline (all 4 directions) |
| Position | Bottom: 350px from bottom edge |
| Animation | Pop-in spring: {mass:1, damping:12, stiffness:200} |
| Timing | Page appears at first word, disappears after last word |

**Visual reference**: All caps, word-by-word yellow highlight, bold pop-in entrance.

**Spring config explained**:
- `damping: 12` — moderate bounce, settles in ~0.4s
- `stiffness: 200` — snappy entrance
- Scale goes from 0 → slight overshoot (~1.05) → 1.0

## Bounce Style

Best for: Entertainment, reactions, challenges, high-energy content.

| Property | Value |
|----------|-------|
| Font | Bangers (Google Fonts, OFL) |
| Font Size | 84px |
| Text Transform | UPPERCASE |
| Words Per Page | 1-2 |
| Combine Window | 600ms |
| Text Color | Rotating (see below) |
| Text Shadow | 4px solid black outline (all 4 directions) |
| Position | Bottom: 350px from bottom edge |
| Animation | Bouncy scale: 70% → ~120% → 100% |
| Spring Config | {mass:1, damping:8, stiffness:180} |

**Color rotation** (per page, cycling):
1. Cyan (#00FFFF)
2. Magenta (#FF00FF)
3. Lime (#00FF00)
4. Yellow (#FFFF00)
5. Orange (#FF6600)
6. Hot Pink (#FF0066)

**Spring config explained**:
- `damping: 8` — very bouncy, overshoots significantly
- Scale: starts at 0.7, springs up to ~1.2, settles at 1.0
- Creates the "explosive word pop" effect

## Clean Style

Best for: Professional, interviews, calm content, podcasts.

| Property | Value |
|----------|-------|
| Font | Inter Bold (700 weight) |
| Font Size | 56px |
| Text Transform | None (preserves original case) |
| Words Per Page | 3-5 |
| Combine Window | 1500ms |
| Text Color | White (#FFFFFF) |
| Active Word | Light gray (#E0E0E0) |
| Text Shadow | 2px 2px 8px rgba(0,0,0,0.6) — soft shadow |
| Position | Bottom: 350px from bottom edge |
| Animation | Fade-in opacity 0→1 over 6 frames (200ms at 30fps) |

**Visual reference**: Minimal, readable, doesn't distract from the speaker. Subtle active-word highlighting through slight color change rather than bold contrast.

## Font Files

All fonts must be placed in `remotion/public/fonts/`:
- `Montserrat-Bold.ttf` — from Google Fonts (OFL license)
- `Bangers-Regular.ttf` — from Google Fonts (OFL license)
- `Inter-Bold.ttf` — from Google Fonts (OFL license)

Download from: https://fonts.google.com/

## Caption Positioning

All styles share the same vertical positioning:
- **Bottom offset**: 350px from bottom edge of 1920px frame
- This places captions above the platform's built-in UI elements (like/comment/share buttons)
- Safe zone for TikTok: 150px from bottom, 64px from sides
- Safe zone for YouTube Shorts: 120px from bottom
- Our 350px offset clears all platform UI with margin

## Integration with Hook Overlay

The hook overlay occupies the top 200px zone (first 3.5s only). Captions appear in the bottom zone. No overlap.

When both are visible (0.3s - 3.5s), the visual hierarchy is:
1. Hook text (top, large, attention-grabbing)
2. Video content (center)
3. Captions (bottom, word-level)
4. Progress bar (very bottom, subtle)
