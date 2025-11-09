import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const headerContainer = style({
  height: '64px',
  display: 'flex',
  alignItems: 'center',
  padding: '0 20px',
  // smoother horizontal cyan band: softer, more natural transitions
  // start from pure black at edges, pass through dark green bands and cyan center
  background: `linear-gradient(90deg,
    #0A0A0A 0%,
    #1A1A1A 10%,
    #004444 25%,
    #006666 40%,
    #39C4C4 50%,
    #006666 60%,
    #004444 75%,
    #1A1A1A 90%,
    #0A0A0A 100%
  )`,
  boxShadow: `inset 0 -1px 0 0 ${colors.mediumBackground}`,
  color: colors.offWhite
})

export const headerTitle = style({
  fontWeight: 'bold',
  fontSize: '1.1rem'
})

export const searchSquare = style({
  width: '40px',
  height: '40px',
  borderRadius: '8px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'rgba(0,0,0,0.35)',
  color: colors.offWhite,
  marginRight: '12px',
  cursor: 'pointer'
})

export const searchWrapper = style({
  flex: '1',
  display: 'flex',
  justifyContent: 'center',
  position: 'relative'
})

export const searchInput = style({
  width: '36%',
  minWidth: '320px',
  maxWidth: '480px',
  height: '40px',
  borderRadius: '8px',
  border: 'none',
  padding: '8px 44px 8px 44px', // room for magnifier
  background: `${colors.cyan}`,
  color: colors.offWhite,
  fontSize: '1rem',
  outline: 'none',
  boxShadow: '0 6px 18px rgba(0,0,0,0.18)',
  '::placeholder': { color: 'rgba(255,255,255,0.8)' }
})

export const searchIconButton = style({
  position: 'absolute',
  left: '12px',
  top: '50%',
  transform: 'translateY(-50%)',
  width: '20px',
  height: '20px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  border: 'none',
  background: 'transparent',
  color: colors.offWhite,
  zIndex: 2,
  cursor: 'pointer',
  padding: 0
})
