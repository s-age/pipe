import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaItem = style({
  marginBottom: '16px'
})

export const multiStepLabel = style({
  color: colors.offWhite,
  fontWeight: 'bold'
})

export const metaItemLabel = style({
  fontWeight: 'bold',
  marginBottom: '4px',
  display: 'block',
  color: colors.offWhite
})

export const inputFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: '#000',
  color: colors.offWhite,
  borderRadius: '4px',
  padding: '8px',
  border: `1px solid ${colors.grayText}`,
  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const textareaFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: '#000',
  color: colors.offWhite,
  minHeight: '100px',
  marginTop: '10px',
  borderRadius: '4px',
  padding: '8px',
  border: `1px solid ${colors.grayText}`,
  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})
