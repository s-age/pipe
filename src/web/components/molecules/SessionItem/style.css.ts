import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const sessionItem = style({
  display: 'flex',
  padding: '8px 12px',
  color: colors.white,
  alignItems: 'center',
  borderBottom: `1px solid ${colors.darkGray}`,
  justifyContent: 'space-between',
  selectors: {
    '&:hover': {
      background: colors.darkGray
    }
  }
})

export const checkbox = style({
  marginRight: '12px'
})

export const sessionName = style({
  flex: 1,
  fontWeight: '500'
})

export const createdAt = style({
  fontSize: '0.9em',
  color: colors.lightGray,
  flexShrink: 0
})
