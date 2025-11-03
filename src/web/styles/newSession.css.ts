import { style } from '@vanilla-extract/css'

const colors = {
  darkBackground: '#2b2b2b',
  mediumBackground: '#373b3e',
  lightText: '#bec8d1',
  offWhite: '#fffeec',
  lightBlue: '#c3e5e7',
  mediumBlue: '#86cecb',
  darkBlue: '#137a7f',
  error: '#e12885',
  grayText: '#8c97a4',
  accent: '#4aa6ac',
  accentHover: '#3c858a',
  purpleAccent: '#96297b',
}

export const bodyStyle = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '20px',
  backgroundColor: colors.darkBackground,
  color: colors.lightText,
})

export const containerStyle = style({
  maxWidth: '800px',
  margin: 'auto',
  backgroundColor: colors.mediumBackground,
  padding: '28px',
  borderRadius: '8px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
})

export const h1Style = style({
  color: colors.accent,
  borderBottom: `1px solid ${colors.mediumBackground}`,
  paddingBottom: '12px',
  marginBottom: '20px',
})

export const labelStyle = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: colors.accent,
})

export const inputFieldStyle = style({
  width: 'calc(100% - 24px)',
  padding: '12px',
  marginBottom: '16px',
  border: `1px solid ${colors.accent}`,
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
  backgroundColor: colors.darkBackground,
  color: colors.lightText,
})

export const textareaFieldStyle = style({
  minHeight: '100px',
  resize: 'vertical',
})

export const errorMessage = style({
  color: colors.error,
  marginTop: '12px',
})

export const fieldsetStyle = style({
  border: `1px solid ${colors.mediumBackground}`,
  padding: '16px',
  borderRadius: '4px',
  marginBottom: '16px',
})

export const legendStyle = style({
  padding: '0 4px',
  color: colors.accent,
})

export const gridContainer = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px',
})
