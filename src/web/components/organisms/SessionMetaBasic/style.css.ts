import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const multiStepLabel = style({
  fontWeight: 'bold',
  color: colors.white
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const requiredMark = style({
  marginLeft: '6px',
  fontWeight: 'bold',
  color: colors.red
})

export const inputFullWidth = style({
  width: '100%'
})

export const artifactsList = style({
  marginTop: '8px'
})

export const artifactItem = style({
  display: 'flex',
  marginBottom: '4px',
  padding: '4px 8px',
  borderRadius: '4px',
  backgroundColor: colors.offWhiteAlt,
  alignItems: 'center',
  justifyContent: 'space-between'
})

export const artifactPath = style({
  fontSize: '14px',
  flexGrow: 1
})

export const removeArtifactButton = style({
  minWidth: '24px',
  height: '24px',
  marginLeft: '8px'
})
