import { style } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

export const appContainer = style({
  display: 'flex',
  height: '100vh',
  overflow: 'hidden',
})

export const columnStyle = style({
  flex: '1',
  padding: '20px',
  overflowY: 'auto',
  borderRight: `1px solid ${colors.offWhite}`,
  selectors: {
    '&:last-child': {
      borderRight: 'none',
    },
  },
})
