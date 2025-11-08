import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const appContainer = style({
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  overflow: 'hidden',
  // page background: use app dark background so edges aren't white
  // make the outermost background pure black so panels sit on black
  background: '#000000',
  padding: '0',
})

export const mainContent = style({
  display: 'flex',
  flex: '1',
  overflow: 'hidden',
  gap: '0',
})

export const leftColumn = style({
  flex: '0 0 320px',
  padding: '0',
  overflowY: 'auto',
})

export const centerColumn = style({
  flex: '1 1 0',
  padding: '12px',
  overflowY: 'auto',
  display: 'flex',
  flexDirection: 'column',
})

export const rightColumn = style({
  flex: '0 0 300px',
  padding: '18px',
  overflowY: 'auto',
  marginRight: '16px',
  display: 'flex',
  flexDirection: 'column',
  boxSizing: 'content-box',
  // ensure right panel fills available height
  alignItems: 'stretch',
})

export const panel = style({
  // panels should be slightly lighter than the page background
  background: colors.darkBackground,
  borderRadius: '10px',
  padding: '12px',
  // slightly softer shadow so the page edge doesn't read as white
  boxShadow: '0 6px 20px rgba(0,0,0,0.5)',
  color: colors.offWhite,
  height: '100%',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  flex: '1 1 auto',
})
