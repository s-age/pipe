import { style } from '@vanilla-extract/css'

export const rightColumn = style({
  display: 'flex',
  width: '320px',
  height: '100%',
  paddingBottom: '12px',
  flexDirection: 'column',
  gap: '12px'
})

export const header = style({
  fontSize: '14px',
  fontWeight: 600
})

export const metaBody = style({
  display: 'flex',
  flex: '1',
  minHeight: 0,
  flexDirection: 'column'
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
