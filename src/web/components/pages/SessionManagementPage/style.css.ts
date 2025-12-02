import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css'

export const pageContent = style({
  display: 'flex',
  flex: 1,
  width: '60%',
  minHeight: 0,
  margin: '12px 0',
  flexDirection: 'column',
  alignSelf: 'center'
})

export const scrollableContainer = style({
  display: 'flex',
  flex: 1,
  minHeight: 0,
  maxHeight: 'calc(100vh - 48px)',
  overflowY: 'auto',
  padding: '20px 20px 80px',
  borderRadius: '12px',
  background: colors.gray,
  flexDirection: 'column',
  gap: '12px'
})

export const headerSection = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
})

export const actionsSection = style({
  display: 'flex',
  gap: '12px'
})

export const buttonBar = style({
  display: 'flex',
  position: 'fixed',
  bottom: '12px',
  left: '50%',
  width: '60%',
  maxWidth: '1200px',
  boxSizing: 'border-box',
  padding: '10px',
  borderRadius: '0 0 12px 12px',
  background: colors.gray,
  transform: 'translateX(-50%)',
  borderTop: `2px solid ${colors.black}`,
  zIndex: zIndex.stickyButtonBar,
  gap: '12px',
  justifyContent: 'center',
  alignItems: 'center',
  '@media': {
    'screen and (max-width: 720px)': {
      width: 'calc(100% - 32px)',
      left: '50%',
      transform: 'translateX(-50%)',
      flexDirection: 'column',
      gap: '12px',
      padding: '12px'
    }
  }
})

const PRIMARY_BASIS = '50%'
const SECONDARY_BASIS = '30%'

export const primaryButton = style({
  display: 'flex',
  flex: `0 0 ${PRIMARY_BASIS}`,
  width: PRIMARY_BASIS,
  minWidth: 0,
  height: '56px',
  boxSizing: 'border-box',
  borderRadius: '6px',
  alignItems: 'center',
  justifyContent: 'center',
  selectors: {
    // Ensure disabled visuals are applied when this layout class is used
    '&:disabled, &[data-disabled="true"]': {
      background: colors.muted,
      color: colors.white,
      cursor: 'not-allowed',
      opacity: 0.8
    }
  },
  '@media': {
    'screen and (min-width: 721px)': {
      order: 2
    },
    'screen and (max-width: 720px)': {
      flex: '0 0 auto',
      width: '100%',
      height: '48px'
    }
  }
})

export const secondaryButton = style({
  display: 'flex',
  flex: `0 0 ${SECONDARY_BASIS}`,
  width: SECONDARY_BASIS,
  height: '56px',
  boxSizing: 'border-box',
  borderRadius: '6px',
  color: colors.white,
  background: colors.muted,
  alignItems: 'center',
  justifyContent: 'center',
  '@media': {
    'screen and (min-width: 721px)': {
      order: 1
    },
    'screen and (max-width: 720px)': {
      flex: '0 0 auto',
      width: '100%',
      height: '48px'
    }
  },
  selectors: {
    '&:hover': {
      background: colors.red,
      color: colors.white
    }
  }
})
