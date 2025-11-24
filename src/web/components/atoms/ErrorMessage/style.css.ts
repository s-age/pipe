import { style } from '@vanilla-extract/css'

export const errorMessageStyle = style({
  display: 'flex',
  width: '100%',
  marginTop: '8px',
  fontWeight: 'bold',
  textAlign: 'left',
  color: 'red',
  alignItems: 'center',
  gap: '8px',
  selectors: {
    '&::before': {
      content: '"❗️"',
      display: 'inline-block',
      marginRight: '8px'
    }
  }
})
