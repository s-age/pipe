import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const container = style({
  display: 'inline-flex',
  flexDirection: 'column',
  gap: '6px',
  width: '100%',
})

export const label = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  fontSize: '12px',
  color: 'var(--text-muted, #666)',
})

export const valueLabel = style({
  fontVariantNumeric: 'tabular-nums',
})

export const trackWrap = style({
  position: 'relative',
  width: '100%',
  height: 36,
})

export const svg = style({
  width: '100%',
  height: 36,
  display: 'block',
})

export const track = style({
  fill: 'var(--track-bg, #e6e6e6)',
})

export const fill = style({
  fill: `var(--accent, ${colors.cyan})`,
})
export const thumbCircle = style({
  fill: 'white',
  stroke: `var(--accent, ${colors.cyan})`,
  strokeWidth: 2,
  filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.12))',
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
    outline: 'none',
  },
})
