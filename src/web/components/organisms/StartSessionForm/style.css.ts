import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css'

export const formContainer = style({
  display: 'flex',
  flex: 1,
  width: '100%',
  maxWidth: '100%',
  height: '100%',
  minHeight: 0,
  boxSizing: 'border-box',
  margin: 0,
  padding: '20px',
  flexDirection: 'column'
})

export const wrapper = style({
  display: 'flex',
  flex: 1,
  minHeight: 0,
  flexDirection: 'column'
})

export const fieldsetContainer = style({
  marginBottom: '16px',
  padding: '16px 0',
  borderRadius: '4px'
})

export const legendStyle = style({
  padding: '0 4px',
  color: colors.cyan
})

export const metaItemLabel = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.white
})

export const requiredMark = style({
  marginLeft: '6px',
  fontWeight: 'bold',
  color: colors.red
})

export const hyperparametersGrid = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px'
})

export const scrollable = style({
  display: 'flex',
  flex: 1,
  minHeight: 0,
  maxHeight: 'calc(100vh - 48px)',
  boxSizing: 'border-box',
  overflowY: 'auto',
  paddingBottom: '84px',
  flexDirection: 'column',
  gap: '12px'
})

export const headingSticky = style({
  position: 'sticky',
  top: 0,
  marginBottom: 0,
  paddingBottom: '8px',
  background: colors.gray,
  zIndex: zIndex.low,
  borderBottom: `1px solid ${colors.gray}`
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

export const errorMessageStyle = style({
  marginTop: '12px',
  color: colors.red
})
