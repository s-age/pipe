export const colors = {
  // Neutral / Black scale
  // Base app background / core text colors.
  black: '#121212',
  pureBlack: '#0a0a1a',
  white: '#FFFFFF',

  // Greys and muted tones
  gray: '#2C2C2C',
  darkGray: '#333333',
  lightGray: '#eeeeee',
  offWhiteAlt: '#f0f0f0',
  muted: '#8c97a4',
  mutedFallback: '#555555',

  // Cyan / Teal (primary accent palette)
  // Use these for interactive accents and branding color usage.
  cyan: '#39C4C4',
  cyanAlt: '#86cecb',
  cyanDark: '#0D474E',
  cyanBorderRGBA: 'rgba(57,196,196,0.5)',
  cyanHover: '#2e9b9b',

  // Blues (helper / secondary accents)
  lightBlue: '#c3e5e7',
  mediumBlue: '#86cecb',

  // Greens
  green: '#0b4d37',

  // Action colors
  red: '#bf1e33',
  orange: '#f59e0b',

  // Header gradient token
  // NOTE: This is a CSS gradient string used for the header background.
  // Keep as a string so it can be assigned directly to `background`.
  headerGradation: `linear-gradient(90deg,
    #0A0A0A 0%,
    #1A1A1A 10%,
    #004444 25%,
    #006666 40%,
    #39C4C4 50%,
    #006666 60%,
    #004444 75%,
    #1A1A1A 90%,
    #0A0A0A 100%
  )`
}
