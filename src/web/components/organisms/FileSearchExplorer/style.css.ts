import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'
import { zIndex } from '@/styles/zIndex.css'

export const container = style({
  position: 'relative',
  maxWidth: '100%'
})

export const pathDisplayContainer = style({
  display: 'flex',
  margin: '8px 0',
  flexWrap: 'wrap',
  gap: '5px'
})

export const pathTag = style({
  display: 'inline-flex',
  padding: '2px 6px',
  borderRadius: '3px',
  fontSize: '12px',
  color: colors.black,
  backgroundColor: colors.cyan,
  cursor: 'pointer',
  alignItems: 'center',
  gap: '8px',
  wordBreak: 'break-all',
  ':hover': {
    opacity: 0.8
  }
})

export const pathTagDeleteButton = style({
  padding: '0',
  border: 'none',
  fontSize: '14px',
  fontWeight: 'bold',
  lineHeight: '1',
  color: 'inherit',
  background: 'none',
  cursor: 'pointer'
})

export const searchInput = style({
  width: '100%',
  border: `1px solid ${colors.muted}`,
  borderRadius: '4px',
  color: colors.white
})

export const suggestionList = style({
  position: 'absolute',
  top: '45px',
  right: '0',
  left: '0',
  height: '150px',
  overflowY: 'auto',
  marginTop: '5px',
  padding: '0',
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '4px',
  backgroundColor: colors.gray,
  zIndex: zIndex.dropdown
})

export const suggestionItem = style({
  padding: '4px 8px',
  color: colors.white,
  backgroundColor: colors.gray,
  cursor: 'pointer',
  listStyle: 'none',
  ':hover': {
    backgroundColor: colors.cyan,
    color: colors.black
  }
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.black
  }
])
