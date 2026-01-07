import { createTheme } from '@vanilla-extract/css'

import { colors } from './colors.css'

export const [themeClass, variables] = createTheme({
  color: {
    // Base colors
    background: colors.darkGray,
    backgroundAlt: colors.black,
    backgroundCode: colors.pureBlack,
    text: colors.white,
    textMuted: colors.muted,
    border: colors.muted,

    // Interactive colors
    primary: colors.cyan,
    primaryHover: colors.cyanHover,
    link: colors.cyan,

    // Status colors
    error: colors.red,
    warning: colors.orange,
    success: colors.green
  },

  spacing: {
    xs: '4px',
    s: '8px',
    m: '16px',
    l: '24px',
    xl: '32px'
  },

  fontSize: {
    xs: '12px',
    s: '14px',
    m: '16px',
    l: '20px',
    xl: '24px'
  },

  borderRadius: {
    s: '4px',
    m: '8px',
    l: '12px'
  },

  fontFamily: {
    sans: 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial',
    mono: 'ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, "DejaVu Sans Mono", monospace'
  }
})
