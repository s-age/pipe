import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const selectStyle = style({
  width: '100%',
  padding: '8px',
  border: `1px solid ${colors.white}`,
  borderRadius: '4px',
  fontSize: '1em',
  color: colors.white,
  backgroundColor: colors.black,
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
  margin: 0,
  padding: 8,
  borderRadius: 6,
  background: colors.gray,
  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
  listStyle: 'none'
})

export const option = style({
  padding: '8px 12px',
  borderRadius: 4,
  background: 'transparent',
  cursor: 'pointer',
  selectors: {
    '&:not(:last-child)': {
      marginBottom: '4px'
    }
  }
})

export const optionHighlighted = style({
  color: colors.black,
  background: colors.lightBlue
})

export const searchInput = style({
  width: '100%',
  marginBottom: 8,
  padding: '8px 10px',
  border: `1px solid ${colors.white}`,
  borderRadius: 6,
  color: colors.white,
  background: colors.black
})
