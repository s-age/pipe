import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const textareaStyle = style({
  width: '100%',
  padding: '10px',
  marginBottom: '15px',
  border: `1px solid ${colors.lightText}`,
  background: colors.grayText,
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
  minHeight: '100px',
  resize: 'vertical'
})
