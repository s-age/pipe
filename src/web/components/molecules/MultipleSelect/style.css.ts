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

export const searchIconInTrigger = style({
  position: 'absolute',
  top: '50%',
  left: '8px',
  color: colors.white,
  pointerEvents: 'none',
  transform: 'translateY(-50%)'
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
  display: 'flex',
  padding: '8px 12px',
  borderRadius: 4,
  background: 'transparent',
  cursor: 'pointer',
  alignItems: 'center',
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
  display: 'flex',
  width: '100%',
  marginBottom: 8,
  padding: '8px 10px',
  border: `1px solid ${colors.white}`,
  borderRadius: 6,
  color: colors.white,
  background: colors.black,
  alignItems: 'center'
})

export const searchInputField = style({
  flex: 1,
  border: 'none',
  color: 'inherit',
  background: 'transparent',
  outline: 'none',
  '::placeholder': {
    color: colors.white
  }
})

export const selectedTags = style({
  display: 'flex',
  marginBottom: '8px',
  flexWrap: 'wrap',
  gap: '4px'
})

export const tag = style({
  display: 'inline-flex',
  padding: '4px 8px',
  borderRadius: '12px',
  fontSize: '0.875em',
  color: colors.black,
  background: colors.cyan,
  alignItems: 'center'
})

export const tagRemove = style({
  marginLeft: '4px',
  fontWeight: 'bold',
  cursor: 'pointer'
})

export const searchIcon = style({
  display: 'flex',
  width: '20px',
  height: '20px',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '2px',
  color: colors.cyan,
  alignItems: 'center',
  justifyContent: 'center'
})

export const checkbox = style({
  width: '16px',
  height: '16px',
  marginRight: '8px'
})
