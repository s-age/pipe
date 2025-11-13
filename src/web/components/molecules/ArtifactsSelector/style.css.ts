import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaItem = style({
  maxWidth: '100%',
  marginBottom: '16px'
})

export const metaItemLabel = style({
  fontWeight: 'bold',
  marginBottom: '4px',
  display: 'block',
  color: colors.offWhite
})

export const artifactsList = style({
  marginTop: '8px',
  display: 'flex',
  flexWrap: 'wrap',
  gap: '4px'
})

export const artifactItem = style({
  backgroundColor: colors.cyan,
  color: colors.uiBackground,
  padding: '2px 6px',
  borderRadius: '3px',
  fontSize: '12px',
  cursor: 'pointer',
  display: 'inline-flex',
  alignItems: 'center',
  gap: '4px',
  ':hover': {
    opacity: 0.8
  }
})

export const artifactPath = style({
  fontSize: '12px',
  wordBreak: 'break-all'
})

export const removeArtifactButton = style({
  background: 'none',
  border: 'none',
  color: 'inherit',
  cursor: 'pointer',
  padding: '0',
  fontSize: '14px',
  lineHeight: '1',
  fontWeight: 'bold'
})

export const debugInfo = style({
  backgroundColor: '#f0f0f0',
  border: '1px solid #ccc',
  padding: '4px',
  marginBottom: '8px',
  fontSize: '12px',
  color: '#333',
  fontFamily: 'monospace',
  borderRadius: '4px'
})
