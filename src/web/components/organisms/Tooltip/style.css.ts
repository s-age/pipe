import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css'

export const tooltipContainer = style({
  display: 'flex',
  position: 'relative',
  justifyContent: 'center',

  selectors: {
    '&.right': {
      justifyContent: 'right'
    }
  }
})

export const tooltipText = style({
  display: 'inline-block',
  position: 'absolute',
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
  transform: 'translate(-50%, -100%)'
})

export const placementBottom = style({
  transform: 'translateX(-50%)'
})

export const placementLeft = style({
  transform: 'translateY(-50%)'
})

export const placementRight = style({
  transform: 'translateY(-50%)'
})

export const visible = style({
  opacity: 1,
  visibility: 'visible'
})
