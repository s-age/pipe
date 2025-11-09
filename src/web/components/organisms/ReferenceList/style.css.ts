import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const metaItem = style({
  marginBottom: '15px'
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '5px',
  fontWeight: 'bold',
  color: colors.offWhite
})

export const referencesList = style({
  listStyle: 'none',
  padding: 0,
  margin: 0
})

export const referenceItem = style({
  marginBottom: '8px',
  padding: '8px',
  border: '1px solid #eee',
  borderRadius: '4px',
  backgroundColor: '#f9f9f9'
})

export const referenceControls = style({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  flexWrap: 'wrap'
})

export const referenceLabel = style({
  display: 'flex',
  alignItems: 'center',
  flexGrow: 1,
  marginRight: '10px'
})

export const referencePath = style({
  marginLeft: '5px',
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
  color: '#ccc',
  selectors: {
    '&[data-locked="true"]': {
      color: '#007bff'
    }
  }
})

export const noItemsMessage = style({
  color: colors.grayText,
  fontStyle: 'italic',
  marginTop: '10px'
})
