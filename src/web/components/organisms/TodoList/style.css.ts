import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const todoItem = style({
  display: 'flex',
  marginBottom: '10px',
  alignItems: 'center'
})

export const todoCheckboxLabel = style({
  display: 'flex',
  color: colors.white,
  cursor: 'pointer',
  alignItems: 'center',
  flexGrow: '1'
})

export const todoTitle = style({
  display: 'inline',
  marginLeft: '8px'
})

export const noItemsMessage = style({
  color: colors.muted,
  fontStyle: 'italic'
})

export const todoCheckboxMargin = style({
  marginRight: '8px'
})

export const deleteTodosButton = style({
  marginTop: '12px',
  backgroundColor: colors.red,
  opacity: 0.9,
  ':hover': {
    backgroundColor: colors.red,
    opacity: 1.0
  }
})
