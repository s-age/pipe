import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const paragraph = style({
  margin: 0,
  display: 'block',

  selectors: {
    '&.size-xs': {
      fontSize: vars.fontSize.xs
    },
    '&.size-s': {
      fontSize: vars.fontSize.s
    },
    '&.size-m': {
      fontSize: vars.fontSize.m
    },
    '&.size-l': {
      fontSize: vars.fontSize.l
    },
    '&.size-xl': {
      fontSize: vars.fontSize.xl
    },
    '&.weight-normal': {
      fontWeight: 400
    },
    '&.weight-medium': {
      fontWeight: 500
    },
    '&.weight-semibold': {
      fontWeight: 600
    },
    '&.weight-bold': {
      fontWeight: 700
    },
    '&.variant-muted': {
      color: vars.color.textMuted
    },
    '&.variant-error': {
      color: vars.color.error
    },
    '&.variant-success': {
      color: vars.color.success
    },
    '&.align-left': {
      textAlign: 'left'
    },
    '&.align-center': {
      textAlign: 'center'
    },
    '&.align-right': {
      textAlign: 'right'
    },
    '&.align-justify': {
      textAlign: 'justify'
    }
  }
})
