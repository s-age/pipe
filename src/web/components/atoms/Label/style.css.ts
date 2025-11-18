import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const labelStyle = style({
  display: 'block',
  marginBottom: '5px',
  fontSize: '14px',
  fontWeight: 'bold',
  color: colors.white
})
