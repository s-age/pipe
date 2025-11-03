import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const inputStyle = style({
  width: 'calc(100% - 22px)',
  padding: '10px',
  marginBottom: '15px',
  border: `1px solid ${colors.lightText}`,
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
})
