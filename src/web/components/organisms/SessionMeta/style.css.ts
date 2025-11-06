import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaColumn = style({
  flex: '0 0 300px',
  overflowY: 'auto',
  background: colors.darkBackground,
})

export const sessionMetaSection = style({
  flex: '1',
  display: 'flex',
  flexDirection: 'column',
  boxSizing: 'border-box',
  minHeight: '0',
  padding: '20px',
})

export const sessionMetaView = style({
  flex: '1',
  overflowY: 'auto',
  paddingBottom: '70px', // Adjust based on the height of the sticky button container
})

export const stickySaveMetaButtonContainer = style({
  position: 'sticky',
  bottom: 0,
  zIndex: 1,
  padding: '12px',
  borderTop: `1px solid ${colors.mediumBackground}`,
  background: 'inherit',
})

export const metaItem = style({
  marginBottom: '16px',
})

export const metaItemLabel = style({
  fontWeight: 'bold',
  marginBottom: '4px',
  display: 'block',
  color: colors.offWhite,
})

export const inputFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: colors.grayText,
  borderRadius: '4px',
  padding: '8px',

  ':focus': {
    border: `1px solid ${colors.darkBlue}`,
  },
})

export const textareaFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: colors.grayText,
  minHeight: '100px',
  marginTop: '10px',

  ':focus': {
    border: `1px solid ${colors.darkBlue}`,
  },
})

export const checkboxLabel = style({
  display: 'flex',
  alignItems: 'center',
  cursor: 'pointer',
  color: colors.offWhite,
})

globalStyle(`${checkboxLabel} input[type="checkbox"]`, {
  marginRight: '4px',
})

export const hyperparametersControl = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px',
})

export const sliderValue = style({
  display: 'inline-block',
  width: '30px',
  textAlign: 'right',
  color: colors.offWhite,
})

export const todosList = style({
  listStyle: 'none',
  paddingLeft: '0',
})

export const todoItem = style({
  marginBottom: '10px',
  display: 'flex',
  alignItems: 'center',
})

export const todoCheckboxLabel = style({
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  flexGrow: '1',
})

globalStyle(`${todoCheckboxLabel} input[type="checkbox"]`, {
  marginRight: '8px',
})

export const todoTitle = style({
  display: 'inline',
  marginLeft: '8px',
})

export const noItemsMessage = style({
  color: colors.grayText,
  fontStyle: 'italic',
})

export const todoCheckboxMargin = style({
  marginRight: '8px',
})

export const deleteTodosButton = style({
  float: 'right',
  marginBottom: '4px',
  backgroundColor: colors.error,
})

export const saveMetaButton = style({
  width: '100%',
})
