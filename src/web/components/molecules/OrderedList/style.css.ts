import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const orderedList = style({
  padding: 0,
  margin: 0,
  paddingLeft: vars.spacing.l,
  display: 'flex',
  flexDirection: 'column',

  selectors: {
    '&.gap-s': {
      gap: vars.spacing.s
    },
    '&.gap-m': {
      gap: vars.spacing.m
    },
    '&.gap-l': {
      gap: vars.spacing.l
    },
    '&.gap-xl': {
      gap: vars.spacing.xl
    }
  }
})
