import { globalStyle } from '@vanilla-extract/css'
import './global.css'

// Minimal reset/global base to ensure predictable layout and flexible containers
globalStyle('*, *::before, *::after', {
  boxSizing: 'border-box'
})

globalStyle('html, body, #root', {
  height: '100%',
  margin: 0,
  padding: 0
})

globalStyle('body', {
  margin: 0,
  padding: 0,
  lineHeight: 1.4,
  WebkitFontSmoothing: 'antialiased',
  MozOsxFontSmoothing: 'grayscale',
  background: 'inherit', // respect app backgrounds set elsewhere
  color: 'inherit'
})

// Make images and media behave
globalStyle('img, picture, video, canvas, svg', {
  display: 'block',
  maxWidth: '100%'
})

// Remove default list styles where appropriate
globalStyle('ul[role="list"], ol[role="list"], ul, ol', {
  listStyle: 'none',
  padding: 0,
  margin: 0
})

// Allow using flexbox children to shrink below content size
globalStyle('#root > *', {
  minHeight: 0
})

// Reset form elements to inherit font
globalStyle('input, button, textarea, select', {
  font: 'inherit'
})

// Remove default focus outlines in favour of accessible focus styles set locally
globalStyle('a, button', {
  textDecoration: 'none'
})

// Remove default margins from headings and paragraphs for layout control
globalStyle('h1, h2, h3, h4, h5, h6', {
  margin: 0,
  padding: 0
})

globalStyle('p', {
  margin: 0
})

// Remove default focus border/outline from form controls but preserve
// an accessible focus indicator using :focus-visible where supported.
globalStyle('input, textarea, select, button', {
  outline: 'none',
  boxShadow: 'none'
})

globalStyle('input:focus, textarea:focus, select:focus, button:focus', {
  outline: 'none',
  boxShadow: 'none',
  borderColor: 'transparent'
})

// Provide a subtle focus-visible style for keyboard users.
globalStyle(':focus-visible', {
  outline: '2px solid rgba(0,200,200,0.9)',
  outlineOffset: '2px'
})
