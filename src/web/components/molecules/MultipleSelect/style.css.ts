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

export const searchIconInTrigger = style({
  position: 'absolute',
  left: '8px',
  top: '50%',
  transform: 'translateY(-50%)',
  color: colors.white,
  pointerEvents: 'none'
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
  display: 'flex',
  alignItems: 'center',
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
  display: 'flex',
  alignItems: 'center',
  width: '100%',
  padding: '8px 10px',
  marginBottom: 8,
  borderRadius: 6,
  border: `1px solid ${colors.white}`,
  background: colors.black,
  color: colors.white
})

export const searchInputField = style({
  flex: 1,
  border: 'none',
  background: 'transparent',
  color: 'inherit',
  outline: 'none',
  '::placeholder': {
    color: colors.white
  }
})

export const selectedTags = style({
  display: 'flex',
  flexWrap: 'wrap',
  gap: '4px',
  marginBottom: '8px'
})

export const tag = style({
  display: 'inline-flex',
  alignItems: 'center',
  padding: '4px 8px',
  background: colors.cyan,
  color: colors.black,
  borderRadius: '12px',
  fontSize: '0.875em'
})

export const tagRemove = style({
  marginLeft: '4px',
  cursor: 'pointer',
  fontWeight: 'bold'
})

export const searchIcon = style({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '20px',
  height: '20px',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '2px',
  color: colors.cyan
})

export const checkbox = style({
  marginRight: '8px',
  width: '16px',
  height: '16px'
})
