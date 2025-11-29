import { globalStyle } from '@vanilla-extract/css'

import './reset.css'
import { colors } from './colors.css.ts'

// Global app styles (font stack and other app-wide defaults)
// To load the Inter font, add one of the following to your app:
// 1) Add this <link> to your HTML <head> (quick):
//    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
// 2) Self-host or include via your bundler.

globalStyle('html, body, #root', {
  fontFamily:
    'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial',
  // Prevent the app from shrinking below 1280px wide. Layouts can still
  // horizontally scroll if the viewport is smaller than this.
  background: colors.darkGray,
  minWidth: '1280px',
  height: '100%',
  contain: 'paint'
})

globalStyle('input, textarea, select', {
  boxSizing: 'border-box',
  background: colors.black,
  color: colors.white,
  borderRadius: '4px',
  padding: '8px',
  border: `1px solid ${colors.muted}`
})

globalStyle('input:focus, textarea:focus, select:focus', {
  border: `1px solid ${colors.cyan}`,
  boxShadow: '0 0 6px #00ffff, inset 0 0 6px #00ffff33',
  outline: 'none'
})

globalStyle('input:-webkit-autofill', {
  boxShadow: `0 0 0px 1000px ${colors.black} inset`,
  WebkitBoxShadow: `0 0 0px 1000px ${colors.black} inset`,
  WebkitTextFillColor: colors.white,
  color: colors.white
})

globalStyle('.markdown-body', {
  marginTop: '0',
  padding: '0'
})

globalStyle('.markdown-body h3', {
  marginTop: '0',
  marginBottom: '0',
  marginBlockStart: '0',
  marginBlockEnd: '0',
  padding: '0',
  lineHeight: '0.8em'
})

globalStyle('.markdown-body h3, .markdown-body p', {
  marginTop: '0',
  marginBottom: '0',
  marginBlockStart: '0',
  marginBlockEnd: '0',
  padding: '0',
  lineHeight: '1.5em'
})

globalStyle('.markdown-body ol, .markdown-body ol ol, .markdown-body ol ul', {
  marginTop: '0',
  marginBottom: '0',
  marginLeft: '24px',
  marginBlockStart: '0',
  marginBlockEnd: '0',
  padding: '0',
  lineHeight: '0',
  listStyleType: 'decimal'
})

globalStyle('.markdown-body ul, .markdown-body ul ul, .markdown-body ul ol', {
  marginTop: '0',
  marginBottom: '0',
  marginLeft: '24px',
  marginBlockStart: '0',
  marginBlockEnd: '0',
  padding: '0',
  lineHeight: '0',
  listStyleType: 'disc'
})

globalStyle('.markdown-body li, .markdown-body li + li', {
  marginTop: '0',
  marginBottom: '0',
  marginBlockStart: '0',
  marginBlockEnd: '0',
  padding: '0',
  lineHeight: '1.8em'
})
