import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const h1Style = style({
  color: colors.accent,
  borderBottom: `1px solid ${colors.mediumBackground}`,
  paddingBottom: '12px',
  marginBottom: '20px'
})

export const h2Style = style({
  color: colors.accent
})
