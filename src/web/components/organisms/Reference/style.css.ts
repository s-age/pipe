import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const referenceItem = style({
  marginBottom: '20px',
  padding: '4px',
  border: `1px solid ${colors.cyanAlt}`,
  borderRadius: '8px',
  color: colors.white,
  backgroundColor: colors.gray,
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  transition: 'box-shadow 0.2s ease'
})

export const referenceLabel = style({
  display: 'flex',
  width: '100%',
  alignItems: 'center'
})

export const referenceActions = style({
  display: 'flex',
  width: '100%',
  padding: '0 8px',
  alignItems: 'center',
  justifyContent: 'space-between'
})

export const referencePath = style({
  marginLeft: '5px',
  fontSize: '12px',
  wordBreak: 'break-all',
  flexGrow: 1,
  selectors: {
    '&[data-disabled="true"]': {
      textDecoration: 'line-through',
      color: colors.muted
    }
  }
})

export const materialIcons = style({
  display: 'inline-block',
  fontFamily: '"Material Icons"',
  fontSize: '24px',
  fontWeight: 'normal',
  lineHeight: 1,
  letterSpacing: 'normal',
  fontStyle: 'normal',
  textTransform: 'none',
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

export const referenceSummary = style({
  marginLeft: '8px',
  fontSize: '0.85rem',
  color: 'rgba(255,255,255,0.74)'
})

export const persistButton = style({
  minWidth: '32px'
})

export const lockIconStyle = style({
  color: colors.muted,
  transition: 'color 0.2s ease',
  selectors: {
    '&[data-locked="true"]': {
      color: colors.cyan
    }
  }
})
