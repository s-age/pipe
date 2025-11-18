import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const loadingSpinnerStyle = style({
  display: 'flex',
  height: '100vh',
  fontSize: '24px',
  fontWeight: 'bold',
  color: colors.darkGray,
  justifyContent: 'center',
  alignItems: 'center'
})
