import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const legendStyle = style({
  // Make section legend a bit larger than form labels for clearer hierarchy
  fontSize: 16,
  fontWeight: 600,
  margin: 0,
  padding: 0,
  color: colors.offWhite
})

export const visuallyHidden = style({
  position: 'absolute',
  width: 1,
  height: 1,
  padding: 0,
  margin: -1,
  overflow: 'hidden',
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap',
  border: 0
})
