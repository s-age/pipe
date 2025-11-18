import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const selectStyle = style({
  width: '100%',
  padding: '8px',
  border: `1px solid ${colors.white}`,
  borderRadius: '4px',
  backgroundColor: colors.black,
  color: colors.white,
  fontSize: '1em',
  cursor: 'pointer',
  ':focus': {
    borderColor: colors.cyan,
    outline: 'none'
  }
})

export const trigger = style({
  display: 'inline-block',
  width: '100%',
  padding: '8px 12px',
  color: colors.white
})

export const panel = style({
  listStyle: 'none',
  padding: 8,
  margin: 0,
  background: colors.gray,
  borderRadius: 6,
  boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
})

export const option = style({
  padding: '8px 12px',
  borderRadius: 4,
  cursor: 'pointer',
  background: 'transparent',
  selectors: {
    '&:not(:last-child)': {
      marginBottom: '4px'
    }
  }
})

export const optionHighlighted = style({
  background: colors.lightBlue,
  color: colors.black
})

export const searchInput = style({
  width: '100%',
  padding: '8px 10px',
  marginBottom: 8,
  borderRadius: 6,
  border: `1px solid ${colors.white}`,
  background: colors.black,
  color: colors.white
})
