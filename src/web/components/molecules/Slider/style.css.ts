import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const container = style({
  position: 'relative',
  width: '100%',
  height: 48
})

export const label = style({
  position: 'absolute',
  top: '0',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  fontSize: '12px',
  color: colors.white,
  pointerEvents: 'none',
  zIndex: 1
})

export const valueLabel = style({
  fontVariantNumeric: 'tabular-nums'
})

export const trackWrap = style({
  position: 'relative',
  width: '100%',
  height: 48
})

export const svg = style({
  width: '100%',
  height: 48,
  display: 'block'
})

export const track = style({
  fill: 'var(--track-bg, #e6e6e6)'
})

export const fill = style({
  fill: `var(--accent, ${colors.cyan})`
})
export const thumbCircle = style({
  fill: 'white',
  stroke: `var(--accent, ${colors.cyan})`,
  strokeWidth: 2,
  filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.12))'
})

export const hiddenRange = style({
  position: 'absolute',
  inset: 0,
  width: '100%',
  height: '100%',
  opacity: 0,
  margin: 0,
  // keep it focusable
  ':focus': {
    outline: 'none'
  }
})
