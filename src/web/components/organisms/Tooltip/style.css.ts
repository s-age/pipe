import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css'

export const tooltipContainer = style({
  display: 'flex',
  position: 'relative',
  justifyContent: 'center'
})

export const tooltipText = style({
  display: 'inline-block',
  position: 'absolute',
  bottom: '125%',
  left: '50%',
  width: 'fit-content',
  height: 'fit-content',
  padding: '6px 10px',
  borderRadius: '6px',
  fontSize: '0.875rem',
  textAlign: 'center',
  color: colors.black,
  backgroundColor: colors.cyan,
  opacity: 0,
  transition: 'opacity 0.18s, transform 0.18s',
  visibility: 'hidden',
  whiteSpace: 'nowrap',
  zIndex: zIndex.base
})

export const placementTop = style({
  bottom: '125%',
  left: '50%',
  transform: 'translateX(-50%)'
})

export const placementBottom = style({
  top: '125%',
  left: '50%',
  transform: 'translateX(-50%)'
})

export const placementLeft = style({
  top: '50%',
  right: '125%',
  transform: 'translateY(-50%)'
})

export const placementRight = style({
  top: '50%',
  left: '125%',
  transform: 'translateY(-50%)'
})

export const visible = style({
  opacity: 1,
  visibility: 'visible'
})
