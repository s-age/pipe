import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const sessionList = style({
  display: 'flex',
  height: '100%',
  overflowY: 'auto',
  flexDirection: 'column'
})

export const header = style({
  display: 'flex',
  padding: '12px',
  fontWeight: 'bold',
  color: colors.white,
  background: colors.black,
  justifyContent: 'space-between',
  alignItems: 'center',
  borderBottom: `1px solid ${colors.darkGray}`
})

export const headerCheckbox = style({
  marginRight: '12px'
})

export const headerName = style({
  flex: 1,
  fontWeight: '500'
})

export const headerCreatedAt = style({
  fontSize: '0.9em',
  color: colors.lightGray,
  flexShrink: 0
})

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

export const checkbox = style({
  marginRight: '12px'
})

export const sessionName = style({
  flex: 1,
  fontWeight: '500'
})

export const createdAt = style({
  fontSize: '0.9em',
  color: colors.lightGray
})

export const sessionNode = style({
  // For tree nodes
})

export const sessionChildren = style({
  marginLeft: '20px'
})
