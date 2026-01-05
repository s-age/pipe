import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const listItem = style({
  selectors: {
    '&.padding-s': {
      padding: vars.spacing.s
    },
    '&.padding-m': {
      padding: vars.spacing.m
    },
    '&.padding-l': {
      padding: vars.spacing.l
    }
  }
})
