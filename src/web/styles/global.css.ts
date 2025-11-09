import { globalStyle } from '@vanilla-extract/css'

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
