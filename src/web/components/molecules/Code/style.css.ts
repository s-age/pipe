import { style } from '@vanilla-extract/css'

import { vars } from '@/styles/theme.css'

export const code = style({
  fontFamily: vars.fontFamily.mono,
  fontSize: vars.fontSize.s,
  backgroundColor: vars.color.backgroundCode,
  padding: `${vars.spacing.xs} ${vars.spacing.s}`,
  borderRadius: vars.borderRadius.s,
  border: `1px solid ${vars.color.border}`
})

export const pre = style({
  fontFamily: vars.fontFamily.mono,
  fontSize: vars.fontSize.s,
  backgroundColor: vars.color.backgroundCode,
  padding: vars.spacing.m,
  borderRadius: vars.borderRadius.m,
  border: `1px solid ${vars.color.border}`,
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
