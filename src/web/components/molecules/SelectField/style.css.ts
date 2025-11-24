import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const errorMessageStyle = style({
  marginTop: '-10px',
  marginBottom: '15px',
  fontSize: '0.875em',
  color: colors.red
})
