import { style } from '@vanilla-extract/css'

export const errorMessageStyle = style({
  color: 'red',
  fontWeight: 'bold',
  textAlign: 'left',
  marginTop: '8px',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  // make it visually compact so it doesn't span too widely
  width: '100%',
  selectors: {
    '&::before': {
      content: '"❗️"',
      display: 'inline-block',
      marginRight: '8px'
    }
  }
})
