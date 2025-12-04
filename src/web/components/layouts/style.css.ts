import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const appContainer = style({
  display: 'flex',
  height: '100vh',
  overflow: 'hidden',
  padding: '0',
  background: colors.pureBlack,
  flexDirection: 'column'
})
