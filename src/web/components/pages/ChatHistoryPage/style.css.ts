import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const appContainer = style({
  display: 'flex',
  height: '100vh',
  overflow: 'hidden',
  padding: '0',
  background: colors.pureBlack,
  flexDirection: 'column'
})

export const mainContent = style({
  display: 'flex',
  flex: '1',
  overflow: 'hidden',
  gap: '0'
})

export const leftColumn = style({
  flex: '0 0 320px',
  overflowY: 'auto',
  padding: '0'
})

export const centerColumn = style({
  display: 'flex',
  flex: '1 1 0',
  overflowY: 'auto',
  padding: '0 12px',
  background: colors.gray,
  flexDirection: 'column'
})

export const rightColumn = style({
  width: '320px',
  boxSizing: 'content-box',
  overflowY: 'auto',
  flexDirection: 'column',
  alignItems: 'stretch',
  scrollbarWidth: 'none',
  scrollbarColor: `${colors.darkGray} transparent`,
  selectors: {
    '&::-webkit-scrollbar': {
      width: '0'
    },
    '&::-webkit-scrollbar-track': {
      background: 'transparent'
    },
    '&::-webkit-scrollbar-thumb': {
      backgroundColor: colors.darkGray,
      borderRadius: '4px'
    }
  }
})

export const panel = style({
  display: 'flex',
  flex: '1 1 auto',
  height: '100%',
  overflow: 'hidden',
  padding: '12px',
  borderRadius: '10px',
  color: colors.white,
  background: colors.black,
  boxShadow: '0 6px 20px rgba(0,0,0,0.5)',
  flexDirection: 'column'
})

export const panelBottomSpacing = style({
  marginBottom: '8px'
})

export const errorMessage = style({
  color: 'red'
})
