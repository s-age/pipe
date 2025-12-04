import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const sessionItem = style({
  display: 'flex',
  padding: '8px 12px',
  color: colors.white,
  alignItems: 'center',
  borderBottom: `1px solid ${colors.darkGray}`,
  selectors: {
    '&:hover': {
      background: colors.darkGray
    }
  }
})

export const label = style({
  display: 'flex',
  flex: 1,
  cursor: 'pointer',
  alignItems: 'center'
})

export const checkbox = style({
  marginRight: '12px',
  flexShrink: 0
})

export const content = style({
  display: 'grid',
  flex: 1,
  gridTemplateColumns: '1fr 100px 180px',
  gap: '12px'
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
