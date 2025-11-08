import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'inline-flex',
  alignItems: 'center',
  gap: '8px',
  cursor: 'pointer',
})
export const control = style({
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '18px',
  height: '18px',
  border: `1px solid ${colors.lightText}`,
  borderRadius: '50%',
  background: 'transparent',
  transition: 'all 0.12s ease',
})

export const svg = style({
  width: '12px',
  height: '12px',
  display: 'block',
})

export const labelText = style({
  userSelect: 'none',
})

export const hiddenInput = style({
  position: 'absolute',
  width: '1px',
  height: '1px',
  padding: 0,
  margin: '-1px',
  overflow: 'hidden',
  clip: 'rect(0 0 0 0)',
  whiteSpace: 'nowrap',
  border: 0,
})

globalStyle(`.${container} input:checked + .${control}`, {
  borderColor: colors.accent,
  backgroundColor: colors.accent,
})

globalStyle(`.${container} input:checked + .${control} svg circle`, {
  fill: colors.accent,
})

globalStyle(`.${container} input:focus + .${control}`, {
  boxShadow: `0 0 0 3px ${colors.accent}33`,
})
