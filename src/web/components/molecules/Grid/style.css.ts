import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const grid = style({
  display: 'grid',

  selectors: {
    '&.columns-1': {
      gridTemplateColumns: '1fr'
    },
    '&.columns-2': {
      gridTemplateColumns: 'repeat(2, 1fr)'
    },
    '&.columns-3': {
      gridTemplateColumns: 'repeat(3, 1fr)'
    },
    '&.columns-4': {
      gridTemplateColumns: 'repeat(4, 1fr)'
    },
    '&.columns-auto-fit': {
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'
    },
    '&.columns-auto-fill': {
      gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))'
    },
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
