import { style } from '@vanilla-extract/css'

export const metaItem = style({
  marginBottom: '16px'
})

export const hyperparametersControl = style({
  display: 'flex',
  alignItems: 'center',
  marginBottom: '10px',
  gap: '16px'
})

export const labelContainer = style({
  // Keep label column fixed so labels align vertically.
  flex: '0 0 180px',
  textAlign: 'left'
})

export const sliderContainer = style({
  // Allow slider to expand to fill remaining space.
  flex: 1,
  minWidth: '220px'
})
