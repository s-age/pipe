import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const pageContainer = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '0',
  backgroundColor: colors.gray,
  color: colors.black,
  padding: '16px',
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column'
})

export const pageContent = style({
  flex: 1,
  minHeight: 0,
  display: 'flex',
  flexDirection: 'column',
  width: '60%',
  alignSelf: 'center'
})
