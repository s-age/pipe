import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'
import { zIndex } from '@/styles/zIndex.css'

export const tabsContainer = style({
  zIndex: zIndex.tabs
})

export const tabHeader = style({
  display: 'flex',
  width: '100%',
  overflow: 'hidden',
  borderRadius: 0,
  background: colors.darkGray,
  gap: 0
})

export const tabButton = style({
  flex: 1,
  minWidth: 0,
  padding: '6px 10px',
  border: 'none',
  borderRadius: 0,
  fontSize: '14px',
  textAlign: 'center',
  color: colors.muted,
  background: colors.darkGray,
  cursor: 'pointer',
  selectors: {
    '&:not(:last-child)': {
      borderRight: `1px solid ${colors.gray}`
    },
    '&:hover': {
      opacity: 0.5
    }
  }
})

export const tabButtonActive = style({
  flex: 1,
  minWidth: 0,
  padding: '6px 10px',
  border: 'none',
  borderRadius: 0,
  fontSize: '14px',
  textAlign: 'center',
  color: colors.white,
  background: colors.cyan,
  cursor: 'pointer',
  selectors: {
    '&:not(:last-child)': {
      borderRight: `1px solid ${colors.cyan}`
    }
  }
})

export const tabPanel = style({
  display: 'block'
})
