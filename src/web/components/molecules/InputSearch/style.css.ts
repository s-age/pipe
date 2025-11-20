import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'inline-flex',
  width: '360px',
  maxWidth: '56%',
  height: '40px',
  overflow: 'hidden',
  borderRadius: '8px',
  boxShadow: '0 6px 18px rgba(0,0,0,0.18)',
  alignItems: 'stretch'
})

export const input = style({
  flex: '1 1 auto',
  padding: '8px 12px',
  border: 'none',
  fontSize: '1rem',
  color: colors.white,
  background: colors.cyanDark,
  outline: 'none',
  '::placeholder': { color: 'rgba(255,255,255,0.8)' }
})

export const button = style({
  display: 'flex',
  flex: '0 0 44px',
  marginLeft: '-24px',
  padding: 0,
  border: 'none',
  color: colors.white,
  background: colors.darkGray,
  cursor: 'pointer',
  alignItems: 'center',
  justifyContent: 'center',

  selectors: {
    '&:hover': {
      background: colors.gray
    }
  }
})
