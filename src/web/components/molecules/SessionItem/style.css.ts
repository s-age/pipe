import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const sessionItem = style({
  color: colors.white,
  borderBottom: `1px solid ${colors.darkGray}`,
  selectors: {
    '&:hover': {
      background: colors.darkGray
    }
  }
})

export const label = style({
  flex: 1,
  cursor: 'pointer'
})

export const checkbox = style({
  marginRight: '12px',
  flexShrink: 0
})

export const gridContent = style({
  flex: 1
})

export const subject = style({
  overflow: 'hidden',
  fontWeight: '500',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap'
})

export const shortHash = style({
  fontSize: '0.9em',
  color: colors.lightGray,
  whiteSpace: 'nowrap'
})

export const createdAt = style({
  fontSize: '0.9em',
  color: colors.lightGray,
  whiteSpace: 'nowrap'
})
