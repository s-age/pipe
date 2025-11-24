import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const wrapper = style({
  marginBottom: '16px'
})

export const label = style({
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
