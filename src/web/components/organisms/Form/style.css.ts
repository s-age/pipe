import { style } from '@vanilla-extract/css'

import { colors } from '@/styles/colors.css'

// Ensure forms can stretch to fill their container so child controls with
// flex-based layouts (footer, lists) can size correctly.
export const formStyle = style({
  width: '100%',
  height: '100%',
  minHeight: 0
})

export const formErrorStyle = style({
  marginBottom: '1rem',
  color: colors.red
})
