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
  padding: '12px',
  color: colors.offWhite,
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '8px',
  backgroundColor: colors.mediumBackground,
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  transition: 'box-shadow 0.2s ease'
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
  margin: '0 12px 12px 0'
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
