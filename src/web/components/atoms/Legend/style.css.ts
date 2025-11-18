import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const legendStyle = style({
  margin: 0,
  padding: 0,
  fontSize: 16,
  fontWeight: 600,
  color: colors.white
})

export const visuallyHidden = style({
  position: 'absolute',
  width: 1,
  height: 1,
  overflow: 'hidden',
  margin: -1,
  padding: 0,
  border: 0,
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap'
})
