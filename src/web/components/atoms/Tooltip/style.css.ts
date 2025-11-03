import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const tooltipContainer = style({
  position: 'relative',
  display: 'inline-block',
})

export const tooltipText = style({
  visibility: 'hidden',
  width: '120px',
  backgroundColor: colors.darkBackground,
  color: colors.offWhite,
  textAlign: 'center',
  borderRadius: '6px',
  padding: '5px 0',
  position: 'absolute',
  zIndex: 1,
  bottom: '125%',
  left: '50%',
  marginLeft: '-60px',
  opacity: 0,
  transition: 'opacity 0.3s',

  selectors: {
    [`${tooltipContainer}:hover &`]: {
      visibility: 'visible',
      opacity: 1,
    },
  },
})
