import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const formContainer = style({
  maxWidth: '100%',
  width: '100%',
  margin: 0,
  boxSizing: 'border-box',
  padding: '20px',
  display: 'flex',
  flexDirection: 'column',
  flex: 1,
  minHeight: 0
})

export const wrapper = style({
  display: 'flex',
  flexDirection: 'column',
  flex: 1,
  minHeight: 0
})

export const fieldsetContainer = style({
  padding: '16px 0',
  borderRadius: '4px',
  marginBottom: '16px'
})

export const legendStyle = style({
  padding: '0 4px',
  color: colors.cyan
})

export const hyperparametersGrid = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px'
})

export const scrollable = style({
  overflowY: 'auto',
  flex: 1,
  minHeight: 0,
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  boxSizing: 'border-box',
  // Ensure the scrollable region is constrained to the viewport so
  // inner scrolling works even if some parent doesn't provide a fixed height.
  maxHeight: 'calc(100vh - 48px)',
  // Reserve space at the bottom so a sticky button bar doesn't cover content
  paddingBottom: '84px'
})

export const headingSticky = style({
  position: 'sticky',
  top: 0,
  zIndex: 2,
  background: colors.gray,
  paddingBottom: '8px',
  marginBottom: 0,
  borderBottom: `1px solid ${colors.gray}`
})

export const buttonBar = style({
  position: 'fixed',
  bottom: '0',
  left: '50%',
  transform: 'translateX(-50%)',
  zIndex: 999,
  display: 'flex',
  gap: '12px',
  justifyContent: 'center',
  alignItems: 'center',
  padding: '10px',
  width: '60%',
  maxWidth: '1200px',
  boxSizing: 'border-box',
  background: colors.gray,
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
  flex: `0 0 ${PRIMARY_BASIS}`,
  boxSizing: 'border-box',
  minWidth: 0,
  width: PRIMARY_BASIS,
  height: '56px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  // make the primary button visually prominent
  borderRadius: '6px',
  selectors: {
    // Ensure disabled visuals are applied when this layout class is used
    '&:disabled, &[data-disabled="true"]': {
      background: colors.muted,
      color: colors.white,
      cursor: 'not-allowed',
      opacity: 0.8
    }
  },
  // Desktop: ensure Create sits on the right (after Cancel)
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
  flex: `0 0 ${SECONDARY_BASIS}`,
  boxSizing: 'border-box',
  width: SECONDARY_BASIS,
  height: '56px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: '6px',
  // Desktop: ensure Cancel sits on the left (before Create)
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

export const errorMessageStyle = style({
  color: colors.red,
  marginTop: '12px'
})
