import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const instructionWrapper = style({
  position: 'relative',
  width: '100%'
})

export const instructionTextarea = style({
  width: '100%',
  minHeight: '80px',
  padding: '12px 64px 12px 12px',
  borderRadius: '8px',
  fontFamily: 'inherit',
  fontSize: '14px',
  lineHeight: '1.5',
  color: colors.white,
  background: colors.black,
  resize: 'vertical',
  ':focus': {
    outline: 'none',
    borderColor: colors.cyan,
    boxShadow: '0 0 6px #00ffff, inset 0 0 6px #00ffff33'
  },
  ':disabled': {
    cursor: 'not-allowed'
  }
})

export const overlaySendButton = style({
  position: 'absolute',
  top: '50%',
  right: '8px',
  minWidth: 'auto',
  marginRight: '8px',
  padding: '12px 12px 8px',
  boxShadow: '0 0 8px #00ffff',
  transform: 'translateY(-50%)',
  ':disabled': {
    cursor: 'not-allowed',
    background: colors.muted
  },
  ':hover': {
    background: colors.cyan,
    boxShadow:
      '0 0 6px #00ffff, 0 0 12px #00ffff, 0 0 18px #00ffff, 0 0 24px #00ffff77, 0 12px 30px rgba(0,0,0,0.26), inset 0 0 10px #00ffff33'
  },
  ':focus': {
    background: colors.cyan,
    boxShadow:
      '0 0 6px #00ffff, 0 0 12px #00ffff, 0 0 18px #00ffff, 0 0 24px #00ffff77, 0 12px 30px rgba(0,0,0,0.26), inset 0 0 10px #00ffff33'
  }
})
