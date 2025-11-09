import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const metaItem = style({
  marginBottom: '15px',
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '5px',
  fontWeight: 'bold',
  color: colors.offWhite,
})

export const inputFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  // Match SessionMeta inputs: black background, gray border, cyan focus ring
  background: '#000',
  color: colors.offWhite,
  padding: '8px',
  border: `1px solid ${colors.grayText}`,
  borderRadius: '4px',

  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`,
  },
})

export const textareaFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: '#000',
  color: colors.offWhite,
  padding: '8px',
  border: `1px solid ${colors.grayText}`,
  borderRadius: '4px',
  minHeight: '80px',
  resize: 'vertical',

  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`,
  },
})
