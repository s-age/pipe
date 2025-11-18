import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'inline-flex',
  alignItems: 'stretch',
  width: '360px',
  maxWidth: '56%',
  height: '40px',
  borderRadius: '8px',
  overflow: 'hidden',
  boxShadow: '0 6px 18px rgba(0,0,0,0.18)'
})

export const input = style({
  flex: '1 1 auto',
  border: 'none',
  padding: '8px 12px',
  fontSize: '1rem',
  background: colors.cyanDark,
  color: colors.white,
  outline: 'none',
  '::placeholder': { color: 'rgba(255,255,255,0.8)' }
})

export const button = style({
  flex: '0 0 44px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'rgba(0,0,0,0.35)',
  color: colors.white,
  border: 'none',
  cursor: 'pointer',
  padding: 0
})
