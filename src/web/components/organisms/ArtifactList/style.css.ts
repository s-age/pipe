import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const artifactsList = style({
  listStyle: 'none',
  padding: 0,
  margin: 0
})

export const noItemsMessage = style({
  fontSize: '14px',
  color: colors.muted,
  padding: '8px 0',
  fontStyle: 'italic'
})
