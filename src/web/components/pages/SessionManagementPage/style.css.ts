import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const appContainer = style({
  display: 'flex',
  width: '100%',
  overflow: 'hidden',
  padding: '0',
  background: colors.pureBlack,
  flexDirection: 'column'
})

export const mainContent = style({
  display: 'grid',
  padding: '12px',
  gridTemplateColumns: '1fr',
  gap: '0',
  justifyItems: 'center'
})

export const centerColumn = style({
  display: 'flex',
  width: '60%',
  margin: '0 auto',
  padding: '0 12px',
  background: colors.gray,
  flexDirection: 'column'
})

export const sessionManagementContainer = style({
  display: 'flex',
  width: '60%',
  padding: '12px',
  flexDirection: 'column',
  gap: '12px'
})

export const headerSection = style({
  display: 'flex',
  padding: '12px 0',
  justifyContent: 'space-between',
  alignItems: 'center'
})

export const title = style({
  margin: 0,
  fontSize: '24px',
  fontWeight: 'bold',
  color: colors.white
})

export const actionsSection = style({
  display: 'flex',
  gap: '12px'
})
