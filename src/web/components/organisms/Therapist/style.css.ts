import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css.ts'

export const wrapper = style({
  height: '100%',
  boxSizing: 'border-box',
  margin: '0 12px',
  borderRadius: '10px',
  background: colors.darkGray
})

export const container = style({
  display: 'flex',
  position: 'relative',
  height: '100%',
  boxSizing: 'border-box',
  margin: '0',
  flexDirection: 'column'
})

export const body = style({
  display: 'flex',
  flex: '1',
  minHeight: 0,
  // Make the body a flex column but let the inner `results` area handle
  // scrolling so its height stays consistent while header/footer remain visible.
  padding: '0 0 0 16px',
  // Add bottom padding to ensure content doesn't get hidden behind the
  // sticky footer/button container when the content is very long.
  paddingBottom: '56px',
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
  marginTop: '16px',
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
  flex: '1 1 auto',
  minHeight: 0,
  overflowY: 'auto',
  margin: '0',
  paddingRight: '8px'
})

export const list = style({
  marginTop: '8px',
  marginBottom: '16px'
})

export const buttonContainer = style({
  position: 'sticky',
  bottom: 0,
  padding: '12px',
  borderRadius: '0 0 8px 8px',
  background: colors.darkGray,
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
  borderTop: `2px solid ${colors.black}`,
  zIndex: 55
})

export const reloadButton = style({
  display: 'inline-flex',
  // placed inside the header (no absolute positioning needed)
  width: '40px',
  height: '40px',
  padding: 0,
  border: 'none',
  borderRadius: '8px',
  color: colors.cyan,
  background: 'transparent',
  cursor: 'pointer',
  transition: 'transform 140ms ease, background 120ms ease',
  alignItems: 'center',
  justifyContent: 'center',
  selectors: {
    '&:hover, &:focus-visible': {
      transform: 'scale(1.15)',
      background: 'rgba(0,255,255,0.04)'
    }
  }
})

export const header = style({
  position: 'sticky',
  top: 0,
  height: '56px',
  boxSizing: 'border-box',
  padding: '12px 16px',
  borderBottom: `2px solid ${colors.black}`,
  zIndex: 60
})
export const resultItemHeading = style({
  marginTop: '8px',

  selectors: {
    '&:first-child': {
      marginBottom: '8px'
    }
  }
})

export const checkboxLabel = style({
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
  cursor: 'pointer'
})
