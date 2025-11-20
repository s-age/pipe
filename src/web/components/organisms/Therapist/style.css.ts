import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css.ts'

export const container = style({
  width: '300px',
  height: '100%',
  boxSizing: 'border-box',
  overflowX: 'hidden',
  overflowY: 'auto',
  margin: '0 12px',
  borderRadius: '10px'
})

export const body = style({
  display: 'flex',
  minHeight: 0,
  padding: '16px',
  background: colors.pureBlack,
  flexDirection: 'column',
  gap: '8px'
})

export const title = style({
  margin: 0,
  fontSize: 14,
  fontWeight: 600,
  color: colors.white
})

export const muted = style({
  fontSize: 13,
  color: colors.muted
})
