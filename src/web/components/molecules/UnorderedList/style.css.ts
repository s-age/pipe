import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const unorderedList = style({
  listStyle: 'none',
  padding: 0,
  margin: 0,
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
    },
    '&.marker-disc': {
      listStyle: 'disc',
      paddingLeft: variables.spacing.l
    },
    '&.marker-circle': {
      listStyle: 'circle',
      paddingLeft: variables.spacing.l
    },
    '&.marker-square': {
      listStyle: 'square',
      paddingLeft: variables.spacing.l
    }
  }
})
