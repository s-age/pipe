import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const metaColumn = style({
  // Use a fixed width and let height be governed by the parent panel.
  width: '300px',
  height: '100%',
  overflowY: 'auto',
  borderRadius: '10px',
  // provide breathing room on the right so the panel isn't flush to the viewport edge
  margin: '0 12px',
  // Keep horizontal overflow hidden but allow vertical scrolling via overflowY above.
  overflowX: 'hidden'
})

export const sessionMetaSection = style({
  flex: '1',
  display: 'flex',
  flexDirection: 'column',
  boxSizing: 'border-box',
  minHeight: '0',
  overflowY: 'auto'
})

export const sessionMetaView = style({
  flex: '1',
  padding: '20px',
  background: colors.gray,
  borderRadius: '8px',
  marginBottom: '16px',

  selectors: {
    '&:first-child': {
      marginBottom: '24px'
    },
    '&:last-child': {
      borderRadius: '8px 8px 0 0'
    }
  }
})

export const stickySaveMetaButtonContainer = style({
  position: 'sticky',
  bottom: 0,
  zIndex: 1,
  padding: '12px',
  borderTop: `1px solid ${colors.gray}`,
  background: colors.black,
  // Slight separation shadow so the sticky area reads as a control bar
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)'
})

export const metaItem = style({
  marginBottom: '16px'
})

export const metaItemLabel = style({
  fontWeight: 'bold',
  marginBottom: '4px',
  display: 'block',
  color: colors.white
})

export const multiStepLabel = style({
  color: colors.white,
  fontWeight: 'bold'
})

export const inputFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  // Make inputs visually match the panel: black background, gray border.
  background: '#000',
  color: colors.white,
  borderRadius: '4px',
  padding: '8px',

  border: `1px solid ${colors.muted}`,

  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const textareaFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: '#000',
  color: colors.white,
  minHeight: '100px',
  marginTop: '10px',
  borderRadius: '4px',
  padding: '8px',

  border: `1px solid ${colors.muted}`,

  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const checkboxLabel = style({
  display: 'flex',
  alignItems: 'center',
  cursor: 'pointer',
  color: colors.white
})

globalStyle(`${checkboxLabel} input[type="checkbox"]`, {
  marginRight: '4px'
})

export const hyperparametersControl = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px'
})

export const sliderValue = style({
  display: 'inline-block',
  width: '30px',
  textAlign: 'right',
  color: colors.white
})

export const sliderContainer = style({
  flex: 1
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
  alignItems: 'center',
  flexGrow: '1'
})

globalStyle(`${todoCheckboxLabel} input[type="checkbox"]`, {
  marginRight: '8px'
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
  float: 'right',
  marginBottom: '4px',
  backgroundColor: colors.red
})

export const saveMetaButton = style({
  width: '100%',
  height: '56px',
  padding: '12px 16px',
  borderRadius: '8px',
  boxSizing: 'border-box'
})
