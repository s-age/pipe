import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'inline-flex',
  color: colors.white,
  cursor: 'pointer',
  alignItems: 'center',
  gap: '8px'
})
export const control = style({
  display: 'inline-flex',
  width: '18px',
  height: '18px',
  border: `1px solid ${colors.white}`,
  borderRadius: '50%',
  background: 'transparent',
  transition: 'all 0.12s ease',
  alignItems: 'center',
  justifyContent: 'center'
})

export const svg = style({
  display: 'block',
  width: '12px',
  height: '12px'
})

export const labelText = style({
  userSelect: 'none'
})

export const hiddenInput = style({
  position: 'absolute',
  width: '1px',
  height: '1px',
  overflow: 'hidden',
  margin: '-1px',
  padding: 0,
  border: 0,
  clip: 'rect(0 0 0 0)',
  whiteSpace: 'nowrap'
})

globalStyle(`.${container} input:checked + .${control}`, {
  borderColor: colors.cyan,
  backgroundColor: colors.cyan
})

globalStyle(`.${container} input:checked + .${control} svg circle`, {
  fill: colors.cyan
})

globalStyle(`.${container} input:focus + .${control}`, {
  boxShadow: `0 0 0 3px ${colors.cyan}33`
})
