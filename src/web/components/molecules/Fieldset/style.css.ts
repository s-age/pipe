import { style } from '@vanilla-extract/css'

export const fieldset = style({
  border: 0,
  margin: 0,
  padding: 0,
})

export const hint = style({
  fontSize: 12,
  color: '#666',
  marginTop: 6,
  marginBottom: 6,
})

export const error = style({
  color: 'red',
  fontSize: 12,
  marginTop: 6,
  marginBottom: 6,
  fontWeight: 600,
})
