import { style } from '@vanilla-extract/css'

export const container = style({
  display: 'flex',
  width: '320px',
  gap: '12px'
})

export const left = style({
  display: 'flex',
  flex: '0 0 300px',
  flexDirection: 'column',
  gap: '8px'
})

export const right = style({
  display: 'flex',
  flex: '1 1 auto',
  flexDirection: 'column',
  gap: '8px'
})

export const header = style({
  fontSize: '14px',
  fontWeight: 600
})

export const field = style({
  display: 'flex',
  flexDirection: 'column',
  gap: '6px'
})

export const label = style({
  fontSize: '12px',
  color: '#374151'
})

export const input = style({
  padding: '8px 10px',
  border: '1px solid #e5e7eb',
  borderRadius: '6px',
  fontSize: '13px'
})
