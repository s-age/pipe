import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const container = style({
  display: 'flex',
  minWidth: '300px',
  padding: '16px',
  flexDirection: 'column',
  gap: '16px'
})

export const header = style({
  display: 'flex',
  alignItems: 'center',
  gap: '12px'
})

export const icon = style({
  fontSize: '24px',
  color: colors.cyan
})

export const title = style({
  margin: 0,
  fontSize: '1.2em',
  color: colors.white
})

export const message = style({
  fontSize: '0.9em',
  lineHeight: '1.5',
  color: colors.muted
})

export const actions = style({
  display: 'flex',
  marginTop: '16px',
  justifyContent: 'flex-end',
  gap: '8px'
})
