import { style, globalStyle } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const code = style({
  fontFamily: variables.fontFamily.mono,
  fontSize: variables.fontSize.s,
  padding: `${variables.spacing.xs} ${variables.spacing.s}`
})

export const pre = style({
  fontFamily: variables.fontFamily.mono,
  fontSize: variables.fontSize.s,
  padding: variables.spacing.m,
  overflow: 'auto',
  margin: 0
})

globalStyle(`${pre} code`, {
  backgroundColor: 'transparent',
  padding: 0,
  border: 'none',
  borderRadius: 0
})
