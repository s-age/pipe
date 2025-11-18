import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const accordionRoot = style({
  width: '100%'
})

export const header = style({
  display: 'flex',
  cursor: 'pointer',
  alignItems: 'center',
  justifyContent: 'space-between'
})

export const headerLeft = style({
  display: 'flex',
  alignItems: 'center',
  gap: '8px'
})

export const title = style({
  fontWeight: 600,
  color: colors.white
})

export const summary = style({
  fontSize: '0.85rem',
  color: 'rgba(255,255,255,0.74)'
})

export const chevron = style({
  fontSize: '28px',
  lineHeight: 1,
  color: colors.muted,
  transition: 'transform 160ms ease, color 160ms ease'
})

export const chevronOpen = style({
  transform: 'rotate(90deg)'
})

export const content = style({
  marginTop: '8px'
})
