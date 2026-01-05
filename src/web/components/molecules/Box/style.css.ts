import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const box = style({
  boxSizing: 'border-box',

  selectors: {
    '&.padding-s': {
      padding: vars.spacing.s
    },
    '&.padding-m': {
      padding: vars.spacing.m
    },
    '&.padding-l': {
      padding: vars.spacing.l
    },
    '&.margin-s': {
      margin: vars.spacing.s
    },
    '&.margin-m': {
      margin: vars.spacing.m
    },
    '&.margin-l': {
      margin: vars.spacing.l
    },
    '&.margin-auto': {
      margin: 'auto'
    },
    '&.border-default': {
      border: `1px solid ${vars.color.border}`
    },
    '&.border-thin': {
      border: `1px solid ${vars.color.border}`
    },
    '&.border-thick': {
      border: `2px solid ${vars.color.border}`
    },
    '&.radius-s': {
      borderRadius: vars.borderRadius.s
    },
    '&.radius-m': {
      borderRadius: vars.borderRadius.m
    },
    '&.radius-l': {
      borderRadius: vars.borderRadius.l
    }
  }
})
