import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const metaItem = style({
  marginBottom: '15px',
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '5px',
  fontWeight: 'bold',
  color: colors.cyan,
})

export const inputFullWidth = style({
  width: '100%',
  padding: '8px',
  border: '1px solid #ccc',
  borderRadius: '4px',
})

export const textareaFullWidth = style({
  width: '100%',
  padding: '8px',
  border: '1px solid #ccc',
  borderRadius: '4px',
  minHeight: '80px',
  resize: 'vertical',
})
