import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'
import { zIndex } from '@/styles/zIndex.css'

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const referencesList = style({
  margin: 0,
  padding: 0,
  listStyle: 'none'
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
  marginTop: '10px',
  color: colors.muted,
  fontStyle: 'italic'
})

export const addReferenceContainer = style({
  display: 'flex',
  position: 'relative',
  marginBottom: '15px',
  gap: '10px',
  alignItems: 'center'
})

export const addReferenceInput = style({
  padding: '8px',
  flexGrow: 1
})

export const addReferenceButton = style({
  padding: '8px 12px',
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '4px',
  color: colors.white,
  backgroundColor: colors.cyan,
  cursor: 'pointer',
  transition: 'background-color 0.2s ease'
})

export const suggestionList = style({
  position: 'absolute',
  top: '100%',
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
  color: 'white',
  cursor: 'pointer',
  listStyle: 'none'
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.black
  }
])

export const referenceSummary = style({
  marginLeft: '8px',
  fontSize: '0.85rem',
  color: 'rgba(255,255,255,0.74)'
})
