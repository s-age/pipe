import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'
import { zIndex } from '@/styles/zIndex.css'

export const overlay = style({
  display: 'flex',
  position: 'fixed',
  padding: '24px',
  background: 'rgba(0,0,0,0.6)',
  inset: 0,
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: zIndex.modal
})

export const content = style({
  minWidth: 320,
  maxWidth: '90%',
  padding: '20px',
  border: `1px solid ${colors.muted}`,
  borderRadius: 8,
  color: colors.white,
  background: colors.black,
  boxShadow: '0 10px 30px rgba(0,0,0,0.6)'
})
