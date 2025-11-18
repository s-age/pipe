import { style, keyframes } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css'

export const overlay = style({
  display: 'flex',
  position: 'fixed',
  backgroundColor: 'rgba(0,0,0,0.36)',
  pointerEvents: 'auto',
  inset: 0,
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: zIndex.loading
})

const spin = keyframes({
  '0%': { transform: 'rotate(0deg)' },
  '100%': { transform: 'rotate(360deg)' }
})

export const spinner = style({
  width: 48,
  height: 48,
  borderWidth: 4,
  borderStyle: 'solid',
  borderRadius: '50%',
  borderLeftColor: colors.white,
  borderRightColor: `${colors.white}66`,
  borderTopColor: `${colors.white}66`,
  borderBottomColor: `${colors.white}66`,
  animationName: spin,
  animationDuration: '900ms',
  animationTimingFunction: 'linear',
  animationIterationCount: 'infinite'
})

export const visuallyHidden = style({
  position: 'absolute',
  width: 1,
  height: 1,
  overflow: 'hidden',
  margin: -1,
  padding: 0,
  border: 0,
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap'
})
