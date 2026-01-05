import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const article = style({
  display: 'block'
})

export const paddingS = style({
  padding: vars.spacing.s
})

export const paddingM = style({
  padding: vars.spacing.m
})

export const paddingL = style({
  padding: vars.spacing.l
})
