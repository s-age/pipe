import { style, globalStyle } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css.ts'

export const metaColumn = style({
  height: '100%',
  boxSizing: 'content-box',
  overflowX: 'hidden',
  overflowY: 'auto',
  margin: '0 12px',
  borderRadius: '10px'
})

export const sessionMetaSection = style({
  display: 'flex',
  flex: '1',
  minHeight: '0',
  boxSizing: 'border-box',
  overflowY: 'auto',
  flexDirection: 'column'
})

export const sessionMetaView = style({
  flex: '1',
  marginBottom: '16px',
  padding: '20px',
  borderRadius: '8px',
  background: colors.gray,
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
  bottom: '16px',
  padding: '12px',
  borderRadius: '0 0 8px 8px',
  background: colors.darkGray,
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
  zIndex: zIndex.base,
  borderTop: `2px solid ${colors.black}`
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const multiStepLabel = style({
  fontWeight: 'bold',
  color: colors.white
})

export const inputFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  padding: '8px',
  border: `1px solid ${colors.muted}`,
  borderRadius: '4px',
  color: colors.white,
  background: colors.pureBlack,
  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const textareaFullWidth = style({
  width: '100%',
  minHeight: '100px',
  boxSizing: 'border-box',
  marginTop: '10px',
  padding: '8px',
  border: `1px solid ${colors.muted}`,
  borderRadius: '4px',
  color: colors.white,
  background: colors.pureBlack,
  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const checkboxLabel = style({
  display: 'flex',
  color: colors.white,
  cursor: 'pointer',
  alignItems: 'center'
})

globalStyle(`${checkboxLabel} input[type="checkbox"]`, {
  marginRight: '4px'
})

export const hyperparametersControl = style({
  display: 'flex',
  marginBottom: '10px',
  justifyContent: 'space-between',
  alignItems: 'center'
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
  paddingLeft: '0',
  listStyle: 'none'
})

export const todoItem = style({
  display: 'flex',
  marginBottom: '10px',
  alignItems: 'center'
})

export const todoCheckboxLabel = style({
  display: 'flex',
  cursor: 'pointer',
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
  boxSizing: 'border-box',
  padding: '12px 16px',
  borderRadius: '8px',
  color: colors.white,
  background: 'rgba(0,0,0,0.32)',
  boxShadow: '0 0 8px #00ffff, inset 0 0 10px #00ffff33',
  ':hover': {
    transform: 'translateY(-1px)',
    boxShadow:
      '0 0 6px #00ffff, 0 0 12px #00ffff, 0 0 18px #00ffff, 0 0 24px #00ffff77, 0 12px 30px rgba(0,0,0,0.26), inset 0 0 10px #00ffff33'
  },
  ':disabled': {
    boxShadow: 'none'
  }
})
