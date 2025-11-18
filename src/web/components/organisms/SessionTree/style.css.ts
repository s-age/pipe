import { style } from '@vanilla-extract/css'

import { zIndex } from '@/styles/zIndex.css'

import { colors } from '../../../styles/colors.css.ts'

export const sessionListColumn = style({
  display: 'flex',
  flex: '0 0 250px',
  height: '100vh',
  background: colors.cyanDark,
  flexDirection: 'column',
  borderRight: `1px solid rgba(0,0,0,0.08)`
})

export const sessionListContainer = style({
  minHeight: 0,
  overflowY: 'auto',
  margin: '0',
  padding: '12px 12px',
  paddingBottom: '88px',
  listStyle: 'none',
  flexGrow: '1'
})

export const sessionListItem = style({
  marginBottom: '6px'
})

// Depth-based indentation classes (16px per level). Create up to 10 levels.
export const depth0 = style({ marginLeft: '0px' })
export const depth1 = style({ marginLeft: '16px' })
export const depth2 = style({ marginLeft: '32px' })
export const depth3 = style({ marginLeft: '48px' })
export const depth4 = style({ marginLeft: '64px' })
export const depth5 = style({ marginLeft: '80px' })
export const depth6 = style({ marginLeft: '96px' })
export const depth7 = style({ marginLeft: '112px' })
export const depth8 = style({ marginLeft: '128px' })
export const depth9 = style({ marginLeft: '144px' })
export const depth10 = style({ marginLeft: '160px' })

export const nestedList = style({
  margin: 0,
  paddingLeft: 0,
  listStyle: 'none'
})

export const sessionLink = style({
  display: 'block',
  padding: '8px 12px',
  borderRadius: '6px',
  fontSize: '0.95rem',
  fontWeight: 500,
  color: colors.white,
  textDecoration: 'none',
  ':hover': {
    backgroundColor: colors.cyanAlt
  }
})

export const sessionLinkActive = style({
  fontWeight: 700,
  color: colors.white,
  backgroundColor: colors.cyan,
  boxShadow: 'inset 4px 0 0 rgba(255,255,255,0.06)'
})

export const sessionIdStyle = style({
  marginLeft: '8px',
  fontSize: '0.75em',
  color: colors.white
})

export const stickyNewChatButtonContainer = style({
  position: 'sticky',
  bottom: 0,
  left: 0,
  width: '100%',
  padding: '12px',
  background: colors.cyanDark,
  zIndex: zIndex.sessionTree,
  borderTop: `1px solid rgba(0,0,0,0.06)`
})

export const newChatButton = style({
  display: 'flex',
  width: '100%',
  height: '56px',
  margin: '8px 0',
  border: `2px solid rgba(255,255,255,0.12)`,
  borderRadius: '8px',
  color: colors.white,
  background: 'rgba(0,0,0,0.32)',
  boxShadow: `0 8px 20px rgba(0,0,0,0.22)`,
  cursor: 'pointer',
  alignItems: 'center',
  justifyContent: 'center',
  ':hover': {
    boxShadow: `0 12px 30px rgba(0,0,0,0.26)`,
    transform: 'translateY(-1px)'
  }
})
