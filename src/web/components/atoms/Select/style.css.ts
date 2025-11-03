import { style } from "@vanilla-extract/css";

import { colors } from "../../../styles/colors.css.ts";

export const selectStyle = style({
  width: "100%",
  padding: "8px",
  border: `1px solid ${colors.lightText}`,
  borderRadius: "4px",
  backgroundColor: colors.darkBackground,
  color: colors.lightText,
  fontSize: "1em",
  cursor: "pointer",
  ":focus": {
    borderColor: colors.accent,
    outline: "none",
  },
});
