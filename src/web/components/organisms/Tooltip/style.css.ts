import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const tooltipContainer = style({
  position: 'relative',
  display: 'inline-block'
})

export const tooltipText = style({
  visibility: 'hidden',
  display: 'inline-block',
  width: 'fit-content',
  height: 'fit-content',
  backgroundColor: colors.cyan,
  color: colors.black,
  textAlign: 'center',
  borderRadius: '6px',
  padding: '6px 10px',
  whiteSpace: 'nowrap',
  position: 'absolute',
  zIndex: 1,
  bottom: '125%',
  left: '50%',
  opacity: 0,
  transition: 'opacity 0.18s, transform 0.18s'
  // placement classes
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
  right: '125%',
  top: '50%',
  transform: 'translateY(-50%)'
})

export const placementRight = style({
  left: '125%',
  top: '50%',
  transform: 'translateY(-50%)'
})

export const visible = style({
  visibility: 'visible',
  opacity: 1
})
