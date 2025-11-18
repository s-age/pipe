import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const inputFieldStyle = style({
  boxSizing: 'border-box',
  padding: '8px',
  border: `1px solid ${colors.muted}`,
  borderRadius: '4px',
  color: colors.muted,
  background: colors.black,
  selectors: {
    '&:focus': {
      border: `1px solid ${colors.cyan}`,
      boxShadow: `0 0 0 1px ${colors.cyanBorderRGBA}`,
      outline: 'none'
    }
  }
})

export const errorMessageStyle = style({
  marginTop: '-10px',
  marginBottom: '15px',
  fontSize: '0.875em',
  color: colors.red
})
