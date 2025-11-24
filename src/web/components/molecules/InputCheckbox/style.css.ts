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
  borderRadius: '4px',
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

export const check = style({
  opacity: 0,
  transition: 'opacity 0.12s ease, transform 0.12s ease',
  transform: 'scale(0.8)',
  fill: 'none',
  stroke: 'white',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round'
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

// Target the sibling `.control` when the input (hiddenInput) is checked/focused.
globalStyle(`.${container} input:checked + .${control}`, {
  backgroundColor: colors.cyan,
  borderColor: colors.cyan
})

globalStyle(`.${container} input:checked + .${control} svg path`, {
  opacity: 1,
  transform: 'scale(1)'
})

globalStyle(`.${container} input:focus + .${control}`, {
  boxShadow: `0 0 0 3px ${colors.cyan}33`
})
