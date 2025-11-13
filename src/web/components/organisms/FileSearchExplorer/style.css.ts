import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const container = style({
  padding: '5px',
  position: 'relative',
  maxWidth: '100%'
})

export const pathDisplayContainer = style({
  display: 'flex',
  flexWrap: 'wrap',
  gap: '5px',
  marginBottom: '10px'
})

export const pathTag = style({
  padding: '4px 8px',
  border: '1px solid #ccc',
  borderRadius: '4px',
  backgroundColor: colors.uiBackground,
  color: 'white',
  wordBreak: 'break-all'
})

export const pathTagDeleteButton = style({
  marginLeft: '5px',
  border: 'none',
  background: 'none',
  cursor: 'pointer',
  fontWeight: 'bold',
  color: '#888'
})

export const searchInput = style({
  width: '100%',
  padding: '8px'
})

export const suggestionList = style({
  position: 'absolute',
  top: '100%',
  left: '0',
  right: '0',
  marginTop: '5px',
  padding: '0',
  height: '150px',
  overflowY: 'scroll',
  backgroundColor: colors.uiBackground,
  zIndex: 10
})

export const suggestionItem = style({
  padding: '4px 8px',
  cursor: 'pointer',
  listStyle: 'none',
  color: 'white',
  backgroundColor: colors.uiBackground
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.uiBackground
  }
])
