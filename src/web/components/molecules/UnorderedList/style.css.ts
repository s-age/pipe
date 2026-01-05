import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const unorderedList = style({
  listStyle: 'none',
  padding: 0,
  margin: 0,
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
    '&.marker-disc': {
      listStyle: 'disc',
      paddingLeft: vars.spacing.l
    },
    '&.marker-circle': {
      listStyle: 'circle',
      paddingLeft: vars.spacing.l
    },
    '&.marker-square': {
      listStyle: 'square',
      paddingLeft: vars.spacing.l
    }
  }
})
