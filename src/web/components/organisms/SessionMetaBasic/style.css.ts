import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaItem = style({
  marginBottom: '16px'
})

export const multiStepLabel = style({
  color: colors.offWhite,
  fontWeight: 'bold'
})

export const metaItemLabel = style({
  fontWeight: 'bold',
  marginBottom: '4px',
  display: 'block',
  color: colors.offWhite
})

export const inputFullWidth = style({
  width: '100%'
})

export const artifactsList = style({
  marginTop: '8px'
})

export const artifactItem = style({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '4px 8px',
  marginBottom: '4px',
  backgroundColor: '#f0f0f0',
  borderRadius: '4px'
})

export const artifactPath = style({
  fontSize: '14px',
  flexGrow: 1
})

export const removeArtifactButton = style({
  marginLeft: '8px',
  minWidth: '24px',
  height: '24px'
})
