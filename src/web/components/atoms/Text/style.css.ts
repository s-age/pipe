import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const text = style({
  margin: 0,

  selectors: {
    '&.size-xs': {
      fontSize: variables.fontSize.xs
    },
    '&.size-s': {
      fontSize: variables.fontSize.s
    },
    '&.size-m': {
      fontSize: variables.fontSize.m
    },
    '&.size-l': {
      fontSize: variables.fontSize.l
    },
    '&.size-xl': {
      fontSize: variables.fontSize.xl
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
      color: variables.color.textMuted
    },
    '&.variant-error': {
      color: variables.color.error
    },
    '&.variant-success': {
      color: variables.color.success
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
    },
    '&.truncate': {
      display: 'inline-block',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }
})
