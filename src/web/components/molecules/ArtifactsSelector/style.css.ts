import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const artifactsList = style({
  display: 'flex',
  marginTop: '8px',
  flexWrap: 'wrap',
  gap: '4px'
})

export const artifactItem = style({
  display: 'inline-flex',
  padding: '2px 6px',
  borderRadius: '3px',
  fontSize: '12px',
  color: colors.black,
  backgroundColor: colors.cyan,
  cursor: 'pointer',
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
  padding: '0',
  border: 'none',
  fontSize: '14px',
  fontWeight: 'bold',
  lineHeight: '1',
  color: 'inherit',
  background: 'none',
  cursor: 'pointer'
})

export const debugInfo = style({
  marginBottom: '8px',
  padding: '4px',
  border: '1px solid #ccc',
  borderRadius: '4px',
  fontFamily: 'monospace',
  fontSize: '12px',
  color: colors.darkGray,
  backgroundColor: colors.offWhiteAlt
})
