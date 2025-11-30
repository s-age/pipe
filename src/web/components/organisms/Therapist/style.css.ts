import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css.ts'

export const container = style({
  display: 'flex',
  height: '100%',
  boxSizing: 'border-box',
  margin: '0 12px',
  borderRadius: '10px',
  background: colors.darkGray,
  flexDirection: 'column'
})

export const body = style({
  display: 'flex',
  flex: '1',
  minHeight: 0,
  overflowY: 'auto',
  padding: '16px',
  color: colors.white,
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

export const description = style({
  margin: 0,
  fontSize: 12,
  color: colors.muted
})

export const button = style({
  width: '100%',
  height: '56px',
  boxSizing: 'border-box',
  padding: '12px 16px',
  borderRadius: '8px',
  color: colors.white,
  background: 'rgba(0,0,0,0.32)',
  boxShadow: '0 0 8px #00ffff, inset 0 0 10px #00ffff33',
  ':hover': {
    transform: 'translateY(-1px)',
    boxShadow:
      '0 0 6px #00ffff, 0 0 12px #00ffff, 0 0 18px #00ffff, 0 0 24px #00ffff77, 0 12px 30px rgba(0,0,0,0.26), inset 0 0 10px #00ffff33'
  },
  ':disabled': {
    boxShadow: 'none'
  }
})

export const results = style({
  marginTop: '16px'
})

export const list = style({
  marginTop: '8px',
  marginBottom: '16px'
})

export const buttonContainer = style({
  padding: '12px',
  borderRadius: '0 0 8px 8px',
  background: colors.darkGray,
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
  borderTop: `2px solid ${colors.black}`
})

export const resultItemHeading = style({
  marginTop: '8px',

  selectors: {
    '&:first-child': {
      marginBottom: '8px'
    }
  }
})
