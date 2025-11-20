import { style } from '@vanilla-extract/css'

import { colors } from '../../styles/colors.css.ts'
import { zIndex } from '../../styles/zIndex.css.ts'

export const container = style({
  width: '300px',
  height: '100%',
  overflowX: 'hidden',
  overflowY: 'auto',
  margin: '0 12px',
  borderRadius: '10px'
})

export const tabHeader = style({
  display: 'flex',
  marginBottom: '12px',
  gap: '8px'
})

export const tabButton = style({
  padding: '6px 10px',
  border: 'none',
  borderRadius: 6,
  color: colors.muted,
  background: 'transparent',
  cursor: 'pointer'
})

export const tabButtonActive = style({
  padding: '6px 10px',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '6px',
  color: colors.white,
  background: colors.pureBlack,
  cursor: 'pointer'
})

export const tabBody = style({
  display: 'flex',
  flex: '1',
  minHeight: '0',
  boxSizing: 'border-box',
  overflowY: 'auto',
  flexDirection: 'column'
})

export const sectionTitle = style({
  margin: '0 0 4px 0',
  fontSize: 14,
  fontWeight: 600,
  color: colors.white
})

export const muted = style({
  fontSize: 13,
  color: colors.muted
})

export const form = style({
  display: 'flex',
  flex: '1',
  marginBottom: '0',
  padding: '20px',
  borderRadius: '8px',
  background: colors.gray,
  flexDirection: 'column',
  gap: '10px'
})

export const field = style({
  display: 'flex',
  flexDirection: 'column'
})

export const fieldsetContainer = style({
  borderRadius: '4px'
})

export const label = style({
  fontSize: 12,
  color: colors.white
})
export const input = style({
  width: '100%',
  boxSizing: 'border-box',
  padding: '8px',
  border: `1px solid ${colors.muted}`,
  borderRadius: '4px',
  fontSize: 13,
  color: colors.white,
  background: colors.pureBlack,
  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const textarea = style({
  width: '100%',
  boxSizing: 'border-box',
  padding: '8px',
  border: `1px solid ${colors.muted}`,
  borderRadius: '4px',
  fontSize: 13,
  color: colors.white,
  background: colors.pureBlack,
  resize: 'vertical',
  ':focus': {
    outline: 'none',
    border: `1px solid ${colors.cyan}`,
    boxShadow: `0 0 0 3px ${colors.cyanBorderRGBA}`
  }
})

export const buttonRow = style({
  display: 'flex',
  marginTop: '6px',
  gap: '8px'
})

export const primary = style({
  padding: '8px 12px',
  border: 'none',
  borderRadius: '8px',
  color: colors.white,
  background: colors.cyan,
  cursor: 'pointer'
})

export const secondary = style({
  padding: '8px 12px',
  border: `1px solid ${colors.gray}`,
  borderRadius: '8px',
  color: colors.white,
  background: 'transparent',
  cursor: 'pointer'
})

export const previewBox = style({
  marginTop: '12px',
  padding: '10px',
  border: `1px solid ${colors.gray}`,
  borderRadius: '6px',
  color: colors.white,
  background: colors.pureBlack
})

export const previewTitle = style({
  marginBottom: '6px',
  fontSize: 13,
  fontWeight: 600,
  color: colors.white
})

export const pre = style({
  fontFamily:
    'ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace',
  fontSize: 12,
  color: colors.white,
  whiteSpace: 'pre-wrap'
})

export const buttonContainer = style({
  bottom: 0,
  marginTop: '-12px',
  padding: '12px',
  borderRadius: '0 0 10px 10px',
  background: colors.darkGray,
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
  zIndex: zIndex.base,
  borderTop: `2px solid ${colors.black}`
})

export const executeButton = style({
  width: '100%',
  height: '56px',
  boxSizing: 'border-box',
  padding: '12px 16px',
  borderRadius: '0 0 8px 8px'
})
