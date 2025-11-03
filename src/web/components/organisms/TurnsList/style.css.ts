import { style } from "@vanilla-extract/css";

import { colors } from "../../../styles/colors.css.ts";

export const turnsColumn = style({
  overflowY: "auto",
  flex: "1",
  display: "flex",
  flexDirection: "column",
  background: colors.mediumBackground,
  borderRight: `1px solid ${colors.mediumBackground}`,
  minWidth: 0,
});

export const turnsHeader = style({
  padding: "16px",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  borderBottom: `1px solid ${colors.mediumBackground}`,
});

export const turnsListSection = style({
  flex: "1",
  overflowY: "auto",
  padding: "16px",
});

export const newInstructionControl = style({
  padding: "16px",
  borderTop: `1px solid ${colors.mediumBackground}`,
  display: "flex",
  gap: "10px",
  alignItems: "flex-end",
});

export const instructionTextarea = style({
  flex: "1",
  minHeight: "60px",
  resize: "vertical",
  padding: "8px",
  borderRadius: "4px",
  border: `1px solid ${colors.darkBlue}`,
  backgroundColor: colors.grayText,
  color: colors.lightText,
});

export const welcomeMessage = style({
  padding: "20px",
  textAlign: "center",
  color: colors.grayText,
});
