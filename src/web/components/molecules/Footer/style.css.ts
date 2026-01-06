import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

export const footer = style({
  display: 'block'
})

export const stickyBottom = style({
  position: 'sticky',
  bottom: 0,
  zIndex: zIndex.low
})
