import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const box = style({
  boxSizing: 'border-box',

  selectors: {
    '&.padding-s': {
      padding: variables.spacing.s
    },
    '&.padding-m': {
      padding: variables.spacing.m
    },
    '&.padding-l': {
      padding: variables.spacing.l
    },
    '&.margin-s': {
      margin: variables.spacing.s
    },
    '&.margin-m': {
      margin: variables.spacing.m
    },
    '&.margin-l': {
      margin: variables.spacing.l
    },
    '&.margin-auto': {
      margin: 'auto'
    },
    '&.border-default': {
      border: `1px solid ${variables.color.border}`
    },
    '&.border-thin': {
      border: `1px solid ${variables.color.border}`
    },
    '&.border-thick': {
      border: `2px solid ${variables.color.border}`
    },
    '&.radius-s': {
      borderRadius: variables.borderRadius.s
    },
    '&.radius-m': {
      borderRadius: variables.borderRadius.m
    },
    '&.radius-l': {
      borderRadius: variables.borderRadius.l
    }
  }
})
