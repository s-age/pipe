import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const orderedList = style({
  padding: 0,
  margin: 0,
  paddingLeft: variables.spacing.l,
  display: 'flex',
  flexDirection: 'column',

  selectors: {
    '&.gap-s': {
      gap: variables.spacing.s
    },
    '&.gap-m': {
      gap: variables.spacing.m
    },
    '&.gap-l': {
      gap: variables.spacing.l
    },
    '&.gap-xl': {
      gap: variables.spacing.xl
    }
  }
})
