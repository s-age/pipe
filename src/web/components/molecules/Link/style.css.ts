import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const link = style({
  textDecoration: 'none',
  cursor: 'pointer',

  selectors: {
    '&.variant-default': {
      color: variables.color.link
    },
    '&.variant-default:hover': {
      textDecoration: 'underline'
    },
    '&.variant-subtle': {
      color: 'inherit'
    },
    '&.variant-subtle:hover': {
      color: variables.color.link
    },
    '&.variant-primary': {
      color: variables.color.primary,
      fontWeight: 500
    },
    '&.variant-primary:hover': {
      textDecoration: 'underline'
    },
    '&.variant-unstyled': {
      // No color styles applied, allows className to override
    }
  }
})
