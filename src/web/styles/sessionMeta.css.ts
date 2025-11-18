import { style } from '@vanilla-extract/css'

import { colors } from './colors.css'

export const metaItem = style({
  marginBottom: '16px'
})

export const multiStepLabel = style({
  fontWeight: 'bold',
  color: colors.white
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const requiredMark = style({
  marginLeft: '6px',
  fontWeight: 'bold',
  color: colors.red
})

export const inputFullWidth = style({
  width: '100%'
})
