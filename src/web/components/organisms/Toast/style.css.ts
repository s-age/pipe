import { style, globalStyle, keyframes } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  position: 'fixed',
  zIndex: 1000,
  display: 'flex',
  flexDirection: 'column',
  gap: 8,
  pointerEvents: 'none',
  alignItems: 'flex-end',
  padding: 12
})

// Positioning helpers via data-pos attribute
globalStyle('[data-pos="top-left"]', {
  top: 12,
  left: 12,
  right: 'auto',
  bottom: 'auto',
  alignItems: 'flex-start',
  flexDirection: 'column-reverse'
})

globalStyle('[data-pos="top-center"]', {
  top: 12,
  left: '50%',
  transform: 'translateX(-50%)',
  bottom: 'auto',
  alignItems: 'center',
  flexDirection: 'column-reverse'
})

globalStyle('[data-pos="top-right"]', {
  top: 12,
  right: 12,
  left: 'auto',
  bottom: 'auto',
  alignItems: 'flex-end',
  flexDirection: 'column-reverse'
})

globalStyle('[data-pos="bottom-left"]', {
  bottom: 12,
  left: 12,
  top: 'auto',
  alignItems: 'flex-start',
  flexDirection: 'column'
})

globalStyle('[data-pos="bottom-center"]', {
  bottom: 12,
  left: '50%',
  transform: 'translateX(-50%)',
  top: 'auto',
  alignItems: 'center',
  flexDirection: 'column'
})

globalStyle('[data-pos="bottom-right"]', {
  bottom: 12,
  right: 12,
  top: 'auto',
  alignItems: 'flex-end',
  flexDirection: 'column'
})

export const toast = style({
  pointerEvents: 'auto',
  background: colors.offWhite,
  boxShadow: '0 10px 30px rgba(0,0,0,0.12)',
  borderRadius: 8,
  padding: '10px 12px',
  minWidth: 240,
  maxWidth: 360,
  borderLeft: '4px solid transparent',
  transition: 'transform 200ms ease, opacity 200ms ease'
})

const fadeIn = keyframes({
  '0%': { opacity: 1, transform: 'translateY(-6px) scale(0.98)' },
  '100%': { opacity: 1, transform: 'translateY(0) scale(1)' }
})

const fadeOut = keyframes({
  '0%': { opacity: 1, transform: 'translateY(0) scale(1)' },
  '100%': { opacity: 0, transform: 'translateY(-6px) scale(0.98)' }
})

export const enter = style({
  animationName: fadeIn,
  animationDuration: '200ms',
  animationTimingFunction: 'ease',
  animationFillMode: 'forwards'
})

export const exit = style({
  animationName: fadeOut,
  animationDuration: '180ms',
  animationTimingFunction: 'ease',
  animationFillMode: 'forwards'
})

export const row = style({
  display: 'flex',
  gap: 8,
  alignItems: 'flex-start'
})

export const icon = style({
  width: 28,
  height: 28,
  borderRadius: 14,
  display: 'inline-grid',
  placeItems: 'center',
  background: `${colors.accent}33`,
  color: colors.accent,
  fontSize: 14
})

export const content = style({
  flex: 1
})

export const title = style({
  fontWeight: 600,
  fontSize: 13
})

export const description = style({
  fontSize: 13,
  color: 'var(--muted, #555)',
  marginTop: 2
})

export const close = style({
  background: 'transparent',
  border: 0,
  padding: 6,
  marginLeft: 8,
  cursor: 'pointer'
})

export const statusSuccess = style({
  borderLeftColor: colors.accent,
  backgroundColor: colors.offWhite,
  color: colors.darkBackground
})

export const statusFailure = style({
  borderLeftColor: colors.error,
  backgroundColor: colors.offWhite,
  color: colors.darkBackground
})

export const statusWarning = style({
  borderLeftColor: colors.warning,
  backgroundColor: colors.offWhite,
  color: colors.darkBackground
})
