import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const flexColumn = style({
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
    },
    '&.align-start': {
      alignItems: 'flex-start'
    },
    '&.align-center': {
      alignItems: 'center'
    },
    '&.align-end': {
      alignItems: 'flex-end'
    },
    '&.align-stretch': {
      alignItems: 'stretch'
    },
    '&.justify-start': {
      justifyContent: 'flex-start'
    },
    '&.justify-center': {
      justifyContent: 'center'
    },
    '&.justify-end': {
      justifyContent: 'flex-end'
    },
    '&.justify-between': {
      justifyContent: 'space-between'
    },
    '&.justify-around': {
      justifyContent: 'space-around'
    },
    '&.wrap': {
      flexWrap: 'wrap'
    }
  }
})
