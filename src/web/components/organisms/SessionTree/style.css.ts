import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css.ts'

export const sessionListColumn = style({
  flex: '0 0 250px',
  // make the sidebar fill the viewport so flex footer can sit at the bottom
  height: '100vh',
  // teal/cyan sidebar
  background: colors.cyanDark,
  display: 'flex',
  flexDirection: 'column',
  borderRight: `1px solid rgba(0,0,0,0.08)`,
})

export const sessionListContainer = style({
  listStyle: 'none',
  padding: '6px 8px',
  margin: '0',
  flexGrow: '1',
  overflowY: 'auto',
  // allow the container to shrink within a flex column so overflow works
  minHeight: 0,
  // Make room for the fixed footer so the last list item is not hidden.
  paddingBottom: '88px',
})

export const sessionListItem = style({
  marginBottom: '6px',
})

export const sessionLink = style({
  display: 'block',
  padding: '6px 8px',
  borderRadius: '6px',
  textDecoration: 'none',
  color: colors.offWhite,
  fontWeight: 500,
  fontSize: '0.95rem',
  ':hover': {
    backgroundColor: colors.cyanAlt,
  },
})

export const sessionLinkActive = style({
  backgroundColor: colors.cyan,
  color: colors.offWhite,
  fontWeight: 700,
  boxShadow: 'inset 4px 0 0 rgba(255,255,255,0.06)',
})

export const sessionIdStyle = style({
  fontSize: '0.75em',
  color: colors.offWhite,
  marginLeft: '6px',
})

export const stickyNewChatButtonContainer = style({
  // Fixed overlay footer: always visible at the bottom of the viewport.
  position: 'fixed',
  left: 0,
  bottom: 0,
  width: '250px',
  zIndex: 1000,
  padding: '8px',
  borderTop: `1px solid rgba(0,0,0,0.06)`,
  background: colors.cyanDark,
})

export const newChatButton = style({
  width: '56px',
  height: '56px',
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  margin: '6px auto',
  border: `2px solid rgba(255,255,255,0.12)`,
  background: 'rgba(0,0,0,0.32)',
  color: colors.offWhite,
  boxShadow: `0 8px 20px rgba(0,0,0,0.22)`,
  cursor: 'pointer',
  ':hover': {
    boxShadow: `0 12px 30px rgba(0,0,0,0.26)`,
    transform: 'translateY(-1px)',
  },
})
