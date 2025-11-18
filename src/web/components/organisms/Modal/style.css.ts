import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const overlay = style({
  position: 'fixed',
  inset: 0,
  background: 'rgba(0,0,0,0.6)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
  padding: '24px'
})

export const content = style({
  background: colors.black,
  color: colors.white,
  borderRadius: 8,
  minWidth: 320,
  maxWidth: '90%',
  boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
  border: `1px solid ${colors.muted}`,
  padding: '20px'
})
