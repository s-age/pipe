import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const selectStyle = style({
  width: '100%',
  padding: '8px',
  border: `1px solid ${colors.lightText}`,
  borderRadius: '4px',
  backgroundColor: colors.darkBackground,
  color: colors.lightText,
  fontSize: '1em',
  cursor: 'pointer',
  ':focus': {
    borderColor: colors.accent,
    outline: 'none'
  }
})

export const trigger = style({
  display: 'inline-block',
  width: '100%',
  padding: '8px 12px',
  color: colors.lightText
})

export const searchIconInTrigger = style({
  position: 'absolute',
  left: '8px',
  top: '50%',
  transform: 'translateY(-50%)',
  color: colors.lightText,
  pointerEvents: 'none'
})

export const panel = style({
  listStyle: 'none',
  padding: 8,
  margin: 0,
  background: colors.mediumBackground,
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
  color: colors.darkBackground
})

export const searchInput = style({
  display: 'flex',
  alignItems: 'center',
  width: '100%',
  padding: '8px 10px',
  marginBottom: 8,
  borderRadius: 6,
  border: `1px solid ${colors.lightText}`,
  background: colors.darkBackground,
  color: colors.lightText
})

export const searchInputField = style({
  flex: 1,
  border: 'none',
  background: 'transparent',
  color: 'inherit',
  outline: 'none',
  '::placeholder': {
    color: colors.lightText
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
  background: colors.accent,
  color: colors.darkBackground,
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
  border: `1px solid ${colors.accent}`,
  borderRadius: '2px',
  color: colors.accent
})

export const checkbox = style({
  marginRight: '8px',
  width: '16px',
  height: '16px'
})
