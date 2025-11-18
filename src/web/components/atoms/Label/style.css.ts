import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const labelStyle = style({
  display: 'block',
  marginBottom: '5px',
  fontWeight: 'bold',
  color: colors.white,
  // slightly smaller than section legends to keep hierarchy
  fontSize: '14px'
})
