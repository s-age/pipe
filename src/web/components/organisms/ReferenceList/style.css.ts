import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const metaItem = style({
  marginBottom: '15px'
})

export const metaItemLabel = style({
  display: 'block',
  marginRight: '4px',
  fontWeight: 'bold',
  color: colors.offWhite
})

export const referencesList = style({
  listStyle: 'none',
  padding: 0,
  margin: 0
})

export const referenceItem = style({
  marginBottom: '20px',
  padding: '4px',
  color: colors.offWhite,
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '8px',
  backgroundColor: colors.mediumBackground,
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  transition: 'box-shadow 0.2s ease'
})

export const referenceControls = style({
  display: 'flex',
  flexDirection: 'column',
  gap: '8px'
})

export const referenceLabel = style({
  display: 'flex',
  alignItems: 'center',
  width: '100%'
})

export const referenceActions = style({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  width: '100%',
  padding: '0 8px'
})

export const referencePath = style({
  marginLeft: '5px',
  fontSize: '12px',
  wordBreak: 'break-all',
  flexGrow: 1,
  selectors: {
    '&[data-disabled="true"]': {
      textDecoration: 'line-through',
      color: colors.grayText
    }
  }
})

export const materialIcons = style({
  fontFamily: '"Material Icons"',
  fontWeight: 'normal',
  fontStyle: 'normal',
  fontSize: '24px',
  lineHeight: 1,
  letterSpacing: 'normal',
  textTransform: 'none',
  display: 'inline-block',
  whiteSpace: 'nowrap',
  wordWrap: 'normal',
  direction: 'ltr',
  WebkitFontSmoothing: 'antialiased',
  textRendering: 'optimizeLegibility',
  MozOsxFontSmoothing: 'grayscale',
  fontFeatureSettings: 'liga'
})

export const ttlControls = style({
  display: 'flex',
  alignItems: 'center',
  gap: '5px'
})

export const ttlValue = style({
  minWidth: '20px',
  textAlign: 'center'
})

export const referenceCheckboxMargin = style({
  marginRight: '5px'
})

export const persistButton = style({
  minWidth: '32px'
})

export const lockIconStyle = style({
  color: colors.grayText,
  transition: 'color 0.2s ease',
  selectors: {
    '&[data-locked="true"]': {
      color: colors.cyan
    }
  }
})

export const noItemsMessage = style({
  color: colors.grayText,
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
  color: colors.offWhite,
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
  color: 'white'
})

export const selectedSuggestionItem = style([
  suggestionItem,
  {
    backgroundColor: colors.cyan,
    color: colors.uiBackground
  }
])
