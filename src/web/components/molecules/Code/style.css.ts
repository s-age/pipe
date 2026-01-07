import { style } from '@vanilla-extract/css'

import { variables } from '@/styles/theme.css'

export const code = style({
  fontFamily: variables.fontFamily.mono,
  fontSize: variables.fontSize.s,
  backgroundColor: variables.color.backgroundCode,
  padding: `${variables.spacing.xs} ${variables.spacing.s}`,
  borderRadius: variables.borderRadius.s,
  border: `1px solid ${variables.color.border}`
})

export const pre = style({
  fontFamily: variables.fontFamily.mono,
  fontSize: variables.fontSize.s,
  backgroundColor: variables.color.backgroundCode,
  padding: variables.spacing.m,
  borderRadius: variables.borderRadius.m,
  border: `1px solid ${variables.color.border}`,
  overflow: 'auto',
  margin: 0,

  selectors: {
    '& code': {
      backgroundColor: 'transparent',
      padding: 0,
      border: 'none',
      borderRadius: 0
    }
  }
})
