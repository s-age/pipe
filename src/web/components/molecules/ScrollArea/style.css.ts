import { style, styleVariants } from '@vanilla-extract/css'

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

export const heightVariants = styleVariants({
  auto: {
    height: 'auto'
  },
  full: {
    height: '100%'
  },
  '320px': {
    height: '320px'
  }
})
