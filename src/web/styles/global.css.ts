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
  color: colors.muted,
  borderRadius: '4px',
  padding: '8px',
  border: `1px solid ${colors.muted}`
})

globalStyle('input:focus, textarea:focus, select:focus', {
  border: `1px solid ${colors.cyan}`,
  boxShadow: '0 0 6px #00ffff, inset 0 0 6px #00ffff33',
  outline: 'none'
})
