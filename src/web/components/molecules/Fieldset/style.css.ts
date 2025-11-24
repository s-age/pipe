import { style } from '@vanilla-extract/css'

export const fieldset = style({
  margin: 0,
  padding: 0,
  border: 0
})

export const hint = style({
  marginTop: 6,
  marginBottom: 6,
  fontSize: 12,
  color: '#666'
})

export const error = style({
  marginTop: 6,
  marginBottom: 6,
  fontSize: 12,
  fontWeight: 600,
  color: 'red'
})
