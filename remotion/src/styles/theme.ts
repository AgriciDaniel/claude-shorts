/**
 * Color palettes and style constants for each caption preset.
 */

export const HORMOZI_THEME = {
  textColor: "#FFFFFF",
  activeColor: "#FFD700", // Yellow highlight on active word
  shadowColor: "#000000",
  backgroundColor: "transparent",
};

export const MRBEAST_THEME = {
  textColor: "#FFFFFF",
  shadowColor: "#000000",
  backgroundColor: "transparent",
  // Rotating bright colors per page
  rotatingColors: [
    "#00FFFF", // Cyan
    "#FF00FF", // Magenta
    "#00FF00", // Lime
    "#FFFF00", // Yellow
    "#FF6600", // Orange
    "#FF0066", // Hot pink
  ],
};

export const CLEAN_THEME = {
  textColor: "#FFFFFF",
  activeColor: "#E0E0E0", // Subtle lighter white for active word
  shadowColor: "rgba(0, 0, 0, 0.6)",
  backgroundColor: "transparent",
};
