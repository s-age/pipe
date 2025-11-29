import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css.ts'

export const headerContainer = style({
  display: 'flex',
  height: '64px',
  padding: '0',
  color: colors.white,
  background: colors.headerGradation,
  boxShadow: `inset 0 -1px 0 0 ${colors.gray}`,
  alignItems: 'center'
})

export const headerTitle = style({
  fontSize: '1.1rem',
  fontWeight: 'bold'
})

export const brand = style({
  display: 'flex',
  marginRight: '12px',
  alignItems: 'center',
  gap: '10px'
})

export const brandLogo = style({
  height: '32px',
  margin: '0 20px',
  borderRadius: '6px',
  objectFit: 'cover'
})

export const brandText = style({
  fontSize: '1.1rem',
  fontWeight: '700',
  textTransform: 'lowercase'
})

export const searchSquare = style({
  display: 'flex',
  width: '40px',
  height: '40px',
  marginLeft: '-12px',
  borderRadius: '8px',
  color: colors.white,
  background: colors.cyanDark,
  cursor: 'pointer',
  alignItems: 'center',
  justifyContent: 'center'
})

export const searchWrapper = style({
  display: 'flex',
  position: 'relative',
  flex: '1',
  justifyContent: 'center'
})

export const searchInput = style({
  width: '36%',
  minWidth: '320px',
  maxWidth: '480px',
  height: '40px',
  padding: '8px 44px 8px 44px',
  border: 'none',
  borderRadius: '8px',
  fontSize: '1rem',
  color: colors.white,
  background: `${colors.cyan}`,
  boxShadow: '0 6px 18px rgba(0,0,0,0.18)',
  zIndex: zIndex.low,
  '::placeholder': { color: 'rgba(255,255,255,0.8)' }
})

export const searchIconButton = style({
  display: 'flex',
  position: 'absolute',
  top: '50%',
  left: '12px',
  width: '20px',
  height: '20px',
  padding: 0,
  border: 'none',
  color: colors.white,
  background: 'transparent',
  cursor: 'pointer',
  transform: 'translateY(-50%)',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 2
})

export const searchResults = style({
  position: 'absolute',
  top: 'calc(100% + 8px)',
  left: '50%',
  width: '36%',
  minWidth: '320px',
  maxWidth: '480px',
  overflow: 'hidden',
  padding: '6px 0',
  borderRadius: '8px',
  color: colors.white,
  background: colors.black,
  boxShadow: '0 6px 18px rgba(0,0,0,0.24)',
  transform: 'translateX(-50%)',
  zIndex: zIndex.headerSearch
})

export const searchResultItem = style({
  padding: '10px 14px',
  color: colors.white,
  background: 'transparent',
  cursor: 'pointer',
  borderBottom: '1px solid rgba(255,255,255,0.03)',
  selectors: {
    '&:hover': {
      background: 'rgba(255,255,255,0.06)',
      color: colors.white
    },
    '&:last-child': {
      borderBottom: 'none'
    }
  }
})

export const searchNoResults = style({
  padding: '8px 12px',
  color: 'rgba(255,255,255,0.7)'
})

export const searchModalOverlay = style({
  display: 'flex',
  position: 'fixed',
  background: 'rgba(0,0,0,0.5)',
  inset: 0,
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: zIndex.header
})

export const searchModalContent = style({
  width: '80%',
  maxWidth: '720px',
  height: '70vh',
  overflow: 'auto',
  padding: '0',
  borderRadius: '10px',
  color: colors.white,
  background: colors.gray,
  boxShadow: '0 12px 36px rgba(0,0,0,0.6)'
})

export const searchModalHeader = style({
  display: 'flex',
  marginBottom: '8px',
  padding: '12px',
  borderBottom: `1px solid ${colors.white}`
})

export const searchModalHeaderText = style({
  flex: 1,
  fontSize: '1.2rem',
  fontWeight: 'bold',
  textAlign: 'center',
  color: colors.cyan,
  alignItems: 'center'
})

export const searchModalClose = style({
  border: 'none',
  fontSize: '1rem',
  color: colors.white,
  background: 'transparent',
  cursor: 'pointer'
})
