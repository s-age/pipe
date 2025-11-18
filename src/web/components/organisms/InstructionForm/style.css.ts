import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const instructionWrapper = style({
  position: 'relative',
  width: '100%'
})

export const instructionTextarea = style({
  width: '100%',
  minHeight: '80px',
  padding: '12px 48px 12px 12px',
  fontSize: '14px',
  color: colors.white,
  lineHeight: '1.5',
  borderRadius: '8px',
  background: colors.black,
  resize: 'vertical',
  fontFamily: 'inherit',
  ':focus': {
    outline: 'none',
    borderColor: colors.cyan,
    boxShadow: `0 0 0 2px ${colors.cyan}33`
  },
  ':disabled': {
    cursor: 'not-allowed'
  }
})

export const overlaySendButton = style({
  position: 'absolute',
  right: '8px',
  top: '50%',
  transform: 'translateY(-50%)',
  padding: '12px 12px 8px',
  marginRight: '8px',
  minWidth: 'auto',
  ':disabled': {
    cursor: 'not-allowed',
    backgroundColor: colors.muted
  }
})
