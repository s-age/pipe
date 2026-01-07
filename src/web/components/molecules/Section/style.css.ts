import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const section = style({
  display: 'block'
})

export const paddingS = style({
  padding: variables.spacing.s
})

export const paddingM = style({
  padding: variables.spacing.m
})

export const paddingL = style({
  padding: variables.spacing.l
})
