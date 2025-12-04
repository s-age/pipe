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
  position: 'sticky',
  top: 0,
  padding: '12px',
  fontWeight: 'bold',
  color: colors.white,
  background: colors.black,
  alignItems: 'center',
  borderBottom: `1px solid ${colors.darkGray}`
})

export const headerLabel = style({
  display: 'flex',
  flex: 1,
  cursor: 'pointer',
  alignItems: 'center'
})

export const headerCheckbox = style({
  marginRight: '12px',
  flexShrink: 0
})

export const headerContent = style({
  display: 'grid',
  flex: 1,
  gridTemplateColumns: '1fr 100px 180px',
  gap: '12px'
})

export const headerSubject = style({
  fontWeight: '500'
})

export const headerShortHash = style({
  fontSize: '0.9em',
  color: colors.lightGray,
  whiteSpace: 'nowrap'
})

export const headerUpdatedAt = style({
  fontSize: '0.9em',
  color: colors.lightGray,
  whiteSpace: 'nowrap'
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
