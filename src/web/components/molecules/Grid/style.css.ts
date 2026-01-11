import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

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
      gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 150px), 1fr))'
    },
    '&.columns-auto-fill': {
      gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 150px), 1fr))'
    },
    '&.columns-custom': {
      gridTemplateColumns: 'var(--grid-template-columns)'
    },
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
