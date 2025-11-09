import { style, keyframes } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const overlay = style({
  position: 'fixed',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(0,0,0,0.36)',
  zIndex: 2000,
  pointerEvents: 'auto'
})

const spin = keyframes({
  '0%': { transform: 'rotate(0deg)' },
  '100%': { transform: 'rotate(360deg)' }
})

export const spinner = style({
  width: 48,
  height: 48,
  borderRadius: '50%',
  borderStyle: 'solid',
  borderWidth: 4,
  borderLeftColor: colors.offWhite,
  borderRightColor: `${colors.offWhite}66`,
  borderTopColor: `${colors.offWhite}66`,
  borderBottomColor: `${colors.offWhite}66`,
  animationName: spin,
  animationDuration: '900ms',
  animationTimingFunction: 'linear',
  animationIterationCount: 'infinite'
})

export const visuallyHidden = style({
  position: 'absolute',
  width: 1,
  height: 1,
  padding: 0,
  margin: -1,
  overflow: 'hidden',
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap',
  border: 0
})
