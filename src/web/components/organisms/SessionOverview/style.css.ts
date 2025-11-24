import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const sessionListItem = style({
  marginBottom: '6px'
})

export const sessionLink = style({
  display: 'block',
  padding: '8px 12px',
  borderRadius: '6px',
  fontSize: '0.95rem',
  fontWeight: 500,
  color: colors.white,
  textDecoration: 'none',
  selectors: {
    '&:hover': {
      backgroundColor: colors.cyanAlt
    }
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
