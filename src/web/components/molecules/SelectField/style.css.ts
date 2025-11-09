import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const errorMessageStyle = style({
  color: colors.error,
  fontSize: '0.875em',
  marginTop: '-10px',
  marginBottom: '15px'
})
