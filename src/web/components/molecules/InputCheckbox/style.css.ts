import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'inline-flex',
  alignItems: 'center',
  gap: '8px',
  cursor: 'pointer'
})
export const control = style({
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '18px',
  height: '18px',
  border: `1px solid ${colors.white}`,
  borderRadius: '4px',
  background: 'transparent',
  transition: 'all 0.12s ease'
})

export const svg = style({
  width: '12px',
  height: '12px',
  display: 'block'
})

export const check = style({
  fill: 'none',
  stroke: 'white',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  opacity: 0,
  transform: 'scale(0.8)',
  transition: 'opacity 0.12s ease, transform 0.12s ease'
})

export const labelText = style({
  userSelect: 'none'
})

export const hiddenInput = style({
  // visually hidden but accessible
  position: 'absolute',
  width: '1px',
  height: '1px',
  padding: 0,
  margin: '-1px',
  overflow: 'hidden',
  clip: 'rect(0 0 0 0)',
  whiteSpace: 'nowrap',
  border: 0
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
