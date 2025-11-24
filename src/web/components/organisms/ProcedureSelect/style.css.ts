import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'
import { zIndex } from '@/styles/zIndex.css'

export const container = style({
  position: 'relative',
  maxWidth: '100%'
})

export const input = style({
  width: '100%',
  padding: '8px',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '4px',
  fontSize: '14px',
  color: 'white',
  backgroundColor: colors.black,
  ':focus': {
    outline: 'none',
    borderColor: colors.cyan,
    boxShadow: `0 0 0 2px ${colors.cyan}40`
  }
})

export const suggestionList = style({
  position: 'absolute',
  top: '100%',
  right: '0',
  left: '0',
  height: '150px',
  overflowY: 'auto',
  marginTop: '2px',
  padding: '0',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '4px',
  backgroundColor: colors.black,
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  zIndex: zIndex.dropdown
})

export const suggestionItem = style({
  padding: '8px 12px',
  color: 'white',
  backgroundColor: colors.black,
  cursor: 'pointer',
  listStyle: 'none',
  borderBottom: `1px solid ${colors.darkGray}`,
  ':hover': {
    backgroundColor: colors.darkGray
  },
  ':last-child': {
    borderBottom: 'none'
  }
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.black
  }
])

export const selectedProcedureContainer = style({
  display: 'flex',
  marginTop: '8px',
  flexWrap: 'wrap',
  gap: '4px'
})

export const selectedProcedureTag = style({
  padding: '2px 6px',
  borderRadius: '3px',
  fontSize: '12px',
  color: colors.black,
  backgroundColor: colors.cyan,
  cursor: 'pointer',
  ':hover': {
    opacity: 0.8
  }
})
