import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const pageContainer = style({
  display: 'flex',
  minHeight: '100vh',
  margin: '0',
  padding: '16px',
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  color: colors.black,
  backgroundColor: colors.gray,
  flexDirection: 'column'
})

export const pageContent = style({
  display: 'flex',
  flex: 1,
  width: '60%',
  minHeight: 0,
  flexDirection: 'column',
  alignSelf: 'center'
})
