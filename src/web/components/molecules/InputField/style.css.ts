import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const inputFieldStyle = style({
  boxSizing: 'border-box',
  background: colors.uiBackground,
  color: colors.grayText,
  borderRadius: '4px',
  padding: '8px',
  border: `1px solid ${colors.grayText}`,

  selectors: {
    '&:focus': {
      border: `1px solid ${colors.cyan}`,
      boxShadow: `0 0 0 1px ${colors.cyanBorderRGBA}`,
      outline: 'none'
    }
  }
})

export const errorMessageStyle = style({
  color: colors.error,
  fontSize: '0.875em',
  marginTop: '-10px',
  marginBottom: '15px'
})
