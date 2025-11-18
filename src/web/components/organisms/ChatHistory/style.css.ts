import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css.ts'

// ChatHistory styles — use shared color tokens from `colors`.
export const turnsColumn = style({
  display: 'flex',
  flex: '1 1 0',
  minWidth: 0,
  minHeight: 0,
  overflowY: 'auto',
  borderRadius: '10px',
  flexDirection: 'column',
  borderRight: `1px solid ${colors.gray}`
})

export const chatRoot = style({
  display: 'flex',
  flex: '1 1 0',
  minHeight: 0,
  flexDirection: 'column'
})

export const turnsHeader = style({
  display: 'flex',
  position: 'sticky',
  top: 0,
  padding: '8px',
  color: colors.cyan,
  justifyContent: 'space-between',
  alignItems: 'center',
  zIndex: zIndex.low
})

export const turnsListSection = style({
  flex: '1 1 0',
  minHeight: 0,
  overflowY: 'auto',
  padding: '16px',
  color: colors.white
})

export const panel = style({
  display: 'flex',
  flex: '1 1 auto',
  height: '100%',
  overflow: 'hidden',
  padding: '12px',
  borderRadius: '10px',
  color: colors.white,
  background: colors.black,
  boxShadow: '0 6px 20px rgba(0,0,0,0.5)',
  flexDirection: 'column'
})

export const panelBottomSpacing = style({
  marginBottom: '8px'
})

export const newInstructionControl = style({
  position: 'sticky',
  bottom: 0,
  padding: '12px',
  gap: '12px',
  alignItems: 'stretch',
  zIndex: zIndex.low
})

// Ensure the form inside the sticky footer stretches and lays out its children
// horizontally so the textarea can take available width next to the button.
export const footerForm = style({
  display: 'flex',
  flex: '1 1 auto',
  width: '100%',
  gap: '12px',
  alignItems: 'stretch'
})

export const welcomeMessage = style({
  padding: '12px',
  textAlign: 'center',
  color: colors.muted
})

// Provide named accents for components that want to use the palette
export const chatAccents = {
  cyan: colors.cyan,
  cyanAlt: colors.cyanAlt,
  redAccent: colors.red,
  redStrong: colors.red
}

// Button used to delete the current session in the header
export const deleteButton = style({
  padding: '6px 8px',
  border: 'none',
  borderRadius: '4px',
  color: `${colors.white} !important`,
  backgroundColor: `${colors.red} !important`,
  cursor: 'pointer'
})
