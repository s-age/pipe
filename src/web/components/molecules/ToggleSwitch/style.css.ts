import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const toggleSwitch = style({
  display: 'inline-block',
  position: 'relative',
  width: '50px',
  height: '24px',
  cursor: 'pointer'
})

export const toggleInput = style({
  width: 0,
  height: 0,
  opacity: 0
})

export const toggleSlider = style({
  position: 'absolute',
  top: 0,
  right: 0,
  bottom: 0,
  left: 0,
  borderRadius: '24px',
  backgroundColor: colors.muted,
  transition: '0.4s',
  selectors: {
    '&:before': {
      position: 'absolute',
      content: '""',
      height: '18px',
      width: '18px',
      left: '3px',
      bottom: '3px',
      backgroundColor: colors.white,
      borderRadius: '50%',
      transition: '0.4s'
    }
  }
})

export const toggleSliderChecked = style({
  backgroundColor: colors.cyan,
  selectors: {
    '&:before': {
      transform: 'translateX(26px)'
    }
  }
})

export const toggleLabel = style({
  marginLeft: '10px',
  fontSize: '14px',
  color: colors.white
})
