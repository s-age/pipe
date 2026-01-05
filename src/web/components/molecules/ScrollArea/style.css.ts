import { style } from '@vanilla-extract/css'

export const scrollArea = style({
  flex: 1,
  minHeight: 0,

  selectors: {
    '&.direction-vertical': {
      overflowY: 'auto',
      overflowX: 'hidden'
    },
    '&.direction-horizontal': {
      overflowX: 'auto',
      overflowY: 'hidden'
    },
    '&.direction-both': {
      overflow: 'auto'
    }
  }
})
