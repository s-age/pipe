import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const link = style({
  textDecoration: 'none',
  cursor: 'pointer',

  selectors: {
    '&.variant-default': {
      color: vars.color.link
    },
    '&.variant-default:hover': {
      textDecoration: 'underline'
    },
    '&.variant-subtle': {
      color: 'inherit'
    },
    '&.variant-subtle:hover': {
      color: vars.color.link
    },
    '&.variant-primary': {
      color: vars.color.primary,
      fontWeight: 500
    },
    '&.variant-primary:hover': {
      textDecoration: 'underline'
    }
  }
})
