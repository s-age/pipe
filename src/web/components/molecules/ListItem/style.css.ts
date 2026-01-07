import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const listItem = style({
  selectors: {
    '&.padding-s': {
      padding: variables.spacing.s
    },
    '&.padding-m': {
      padding: variables.spacing.m
    },
    '&.padding-l': {
      padding: variables.spacing.l
    }
  }
})
