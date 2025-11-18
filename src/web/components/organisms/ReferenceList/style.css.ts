import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const metaItem = style({
  marginBottom: '32px'
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const referencesList = style({
  listStyle: 'none',
  padding: 0,
  margin: 0
})

export const referenceControls = style({
  display: 'flex',
  flexDirection: 'column',
  gap: '8px'
})

export const referenceCheckboxMargin = style({
  marginRight: '5px'
})

export const noItemsMessage = style({
  color: colors.muted,
  fontStyle: 'italic',
  marginTop: '10px'
})

export const addReferenceContainer = style({
  display: 'flex',
  gap: '10px',
  marginBottom: '15px',
  alignItems: 'center',
  position: 'relative'
})

export const addReferenceInput = style({
  flexGrow: 1,
  padding: '8px'
})

export const addReferenceButton = style({
  padding: '8px 12px',
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '4px',
  backgroundColor: colors.cyan,
  color: colors.white,
  cursor: 'pointer',
  transition: 'background-color 0.2s ease'
})

export const suggestionList = style({
  position: 'absolute',
  top: '100%',
  left: '0',
  right: '0',
  marginTop: '5px',
  padding: '0',
  height: '150px',
  overflowY: 'auto',
  backgroundColor: colors.gray,
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '4px',
  zIndex: 10
})

export const suggestionItem = style({
  padding: '4px 8px',
  cursor: 'pointer',
  listStyle: 'none',
  color: 'white'
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.black
  }
])
