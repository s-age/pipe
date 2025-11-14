import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const container = style({
  position: 'relative',
  maxWidth: '100%'
})

export const pathDisplayContainer = style({
  display: 'flex',
  flexWrap: 'wrap',
  gap: '5px',
  margin: '8px 0'
})

export const pathTag = style({
  backgroundColor: colors.cyan,
  color: colors.uiBackground,
  padding: '2px 6px',
  borderRadius: '3px',
  fontSize: '12px',
  cursor: 'pointer',
  display: 'inline-flex',
  alignItems: 'center',
  gap: '8px',
  wordBreak: 'break-all',
  ':hover': {
    opacity: 0.8
  }
})

export const pathTagDeleteButton = style({
  background: 'none',
  border: 'none',
  color: 'inherit',
  cursor: 'pointer',
  padding: '0',
  fontSize: '14px',
  lineHeight: '1',
  fontWeight: 'bold'
})

export const searchInput = style({
  width: '100%',
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '4px',
  color: colors.offWhite
})

export const suggestionList = style({
  position: 'absolute',
  top: '45px',
  left: '0',
  right: '0',
  marginTop: '5px',
  padding: '0',
  height: '150px',
  overflowY: 'scroll',
  backgroundColor: colors.mediumBackground,
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '4px',
  zIndex: 10
})

export const suggestionItem = style({
  padding: '4px 8px',
  cursor: 'pointer',
  listStyle: 'none',
  color: colors.offWhite,
  backgroundColor: colors.mediumBackground,
  ':hover': {
    backgroundColor: colors.cyan,
    color: colors.uiBackground
  }
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.uiBackground
  }
])
