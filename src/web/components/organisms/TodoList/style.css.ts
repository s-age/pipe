import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaItem = style({
  marginBottom: '16px'
})

export const todosList = style({
  listStyle: 'none',
  paddingLeft: '0'
})

export const todoItem = style({
  marginBottom: '10px',
  display: 'flex',
  alignItems: 'center'
})

export const todoCheckboxLabel = style({
  cursor: 'pointer',
  display: 'flex',
  color: colors.offWhite,
  alignItems: 'center',
  flexGrow: '1'
})

export const todoTitle = style({
  display: 'inline',
  marginLeft: '8px'
})

export const noItemsMessage = style({
  color: colors.grayText,
  fontStyle: 'italic'
})

export const todoCheckboxMargin = style({
  marginRight: '8px'
})

export const deleteTodosButton = style({
  float: 'right',
  marginBottom: '4px',
  backgroundColor: colors.error
})
