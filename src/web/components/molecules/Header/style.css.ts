import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

export const header = style({
  display: 'block'
})

export const stickyTop = style({
  position: 'sticky',
  top: 0,
  zIndex: zIndex.low
})
