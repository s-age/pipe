import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

export const pageContent = style({
  display: 'flex',
  flex: 1,
  width: '60%',
  minHeight: 0,
  margin: '12px 0',
  borderRadius: '10px',
  backgroundColor: colors.gray,
  flexDirection: 'column',
  alignSelf: 'center'
})
