import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

// ChatHistory styles — use shared color tokens from `colors`.
export const turnsColumn = style({
  overflowY: 'auto',
  // Make center column smaller than left by setting flex ratio 1 (left is 2)
  flex: '1 1 0',
  display: 'flex',
  flexDirection: 'column',
  borderRight: `1px solid ${colors.mediumBackground}`,
  borderRadius: '10px',
  minWidth: 0,
  minHeight: 0
})

export const chatRoot = style({
  display: 'flex',
  flexDirection: 'column',
  flex: '1 1 0',
  minHeight: 0
})

export const turnsHeader = style({
  padding: '8px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  color: colors.accent,
  position: 'sticky',
  top: 0,
  zIndex: 2
})

export const turnsListSection = style({
  flex: '1 1 0',
  overflowY: 'auto',
  padding: '16px',
  color: colors.offWhite,
  minHeight: 0
})

export const panel = style({
  // panels should be slightly lighter than the page background
  background: colors.darkBackground,
  borderRadius: '10px',
  padding: '12px',
  // slightly softer shadow so the page edge doesn't read as white
  boxShadow: '0 6px 20px rgba(0,0,0,0.5)',
  color: colors.offWhite,
  height: '100%',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  flex: '1 1 auto'
})

export const panelBottomSpacing = style({
  marginBottom: '8px'
})

export const newInstructionControl = style({
  padding: '12px',
  gap: '12px',
  alignItems: 'stretch',
  position: 'sticky',
  bottom: 0,
  zIndex: 2
})

// Ensure the form inside the sticky footer stretches and lays out its children
// horizontally so the textarea can take available width next to the button.
export const footerForm = style({
  display: 'flex',
  flex: '1 1 auto',
  gap: '12px',
  alignItems: 'stretch',
  width: '100%'
})

export const welcomeMessage = style({
  padding: '12px',
  textAlign: 'center',
  color: colors.grayText
})

// Provide named accents for components that want to use the palette
export const chatAccents = {
  cyan: colors.cyan,
  cyanAlt: colors.cyanAlt,
  redAccent: colors.error,
  redStrong: colors.error
}
