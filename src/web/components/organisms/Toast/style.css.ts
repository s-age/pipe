import { style, globalStyle, keyframes } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'flex',
  position: 'fixed',
  padding: 12,
  pointerEvents: 'none',
  zIndex: zIndex.toast,
  flexDirection: 'column',
  gap: 8,
  alignItems: 'flex-end'
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
  minWidth: 240,
  maxWidth: 360,
  padding: '10px 12px',
  borderRadius: 8,
  background: colors.white,
  boxShadow: '0 10px 30px rgba(0,0,0,0.12)',
  pointerEvents: 'auto',
  transition: 'transform 200ms ease, opacity 200ms ease',
  borderLeft: '4px solid transparent'
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
  display: 'inline-grid',
  width: 28,
  height: 28,
  borderRadius: 14,
  fontSize: 14,
  color: colors.cyan,
  background: `${colors.cyan}33`,
  placeItems: 'center'
})

export const content = style({
  flex: 1
})

export const title = style({
  fontSize: 13,
  fontWeight: 600
})

export const description = style({
  marginTop: 2,
  fontSize: 13,
  color: colors.muted
})

export const close = style({
  marginLeft: 8,
  padding: 6,
  border: 0,
  background: 'transparent',
  cursor: 'pointer'
})

export const statusSuccess = style({
  color: colors.black,
  backgroundColor: colors.white,
  borderLeftColor: colors.cyan
})

export const statusFailure = style({
  color: colors.black,
  backgroundColor: colors.white,
  borderLeftColor: colors.red
})

export const statusWarning = style({
  color: colors.black,
  backgroundColor: colors.white,
  borderLeftColor: colors.orange
})
