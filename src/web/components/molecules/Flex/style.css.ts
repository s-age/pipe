import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const flex = style({
  display: 'flex',
  flexDirection: 'row',

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
    '&.align-baseline': {
      alignItems: 'baseline'
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
