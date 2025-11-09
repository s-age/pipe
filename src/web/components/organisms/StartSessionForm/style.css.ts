import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const formContainer = style({
  maxWidth: '800px',
  margin: 'auto',
  padding: '20px'
})

export const fieldsetContainer = style({
  border: `1px solid ${colors.lightBlue}`,
  padding: '16px',
  borderRadius: '4px',
  marginBottom: '16px'
})

export const legendStyle = style({
  padding: '0 4px',
  color: colors.accent
})

export const hyperparametersGrid = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px'
})

export const errorMessageStyle = style({
  color: colors.error,
  marginTop: '12px'
})
