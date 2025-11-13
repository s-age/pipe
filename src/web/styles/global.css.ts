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
  minWidth: '1280px'
})

globalStyle('input, textarea', {
  boxSizing: 'border-box',
  background: colors.uiBackground,
  color: colors.grayText,
  borderRadius: '4px',
  padding: '8px',
  border: `1px solid ${colors.grayText}`
})

globalStyle('input:focus, textarea:focus', {
  border: `1px solid ${colors.cyan}`,
  boxShadow: `0 0 0 1px ${colors.cyanBorderRGBA}`,
  outline: 'none'
})
