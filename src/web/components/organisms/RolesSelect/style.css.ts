import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const container = style({
  position: 'relative',
  maxWidth: '100%'
})

export const input = style({
  width: '100%',
  padding: '8px',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '4px',
  backgroundColor: colors.black,
  color: 'white',
  fontSize: '14px',
  ':focus': {
    outline: 'none',
    borderColor: colors.cyan,
    boxShadow: `0 0 0 2px ${colors.cyan}40`
  }
})

export const suggestionList = style({
  position: 'absolute',
  top: '100%',
  left: '0',
  right: '0',
  marginTop: '2px',
  padding: '0',
  height: '150px',
  overflowY: 'auto',
  backgroundColor: colors.black,
  border: `1px solid ${colors.cyan}`,
  borderRadius: '4px',
  zIndex: 10,
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
})

export const suggestionItem = style({
  padding: '8px 12px',
  cursor: 'pointer',
  listStyle: 'none',
  color: 'white',
  backgroundColor: colors.black,
  borderBottom: '1px solid #333',
  ':hover': {
    backgroundColor: '#333'
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

export const selectedRolesContainer = style({
  marginTop: '8px',
  display: 'flex',
  flexWrap: 'wrap',
  gap: '4px'
})

export const selectedRoleTag = style({
  backgroundColor: colors.cyan,
  color: colors.black,
  padding: '2px 6px',
  borderRadius: '3px',
  fontSize: '12px',
  cursor: 'pointer',
  ':hover': {
    opacity: 0.8
  }
})
