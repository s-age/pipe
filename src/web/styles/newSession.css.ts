import { style } from '@vanilla-extract/css';

export const bodyStyle = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '20px',
  backgroundColor: '#222831',
  color: '#eeeeee',
});

export const containerStyle = style({
  maxWidth: '800px',
  margin: 'auto',
  backgroundColor: '#393e46',
  padding: '28px',
  borderRadius: '8px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
});

export const h1Style = style({
  color: '#00adb5',
  borderBottom: '1px solid #393e46',
  paddingBottom: '12px',
  marginBottom: '20px',
});

export const labelStyle = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: '#00adb5',
});

export const inputFieldStyle = style({
  width: 'calc(100% - 24px)',
  padding: '12px',
  marginBottom: '16px',
  border: '1px solid #00adb5',
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
  backgroundColor: '#222831',
  color: '#eeeeee',
});

export const textareaFieldStyle = style({
  minHeight: '100px',
  resize: 'vertical',
});

export const actionButton = style({
  backgroundColor: '#00adb5',
  color: '#222831',
  border: 'none',
  padding: '12px 20px',
  fontSize: '1em',
  borderRadius: '4px',
  cursor: 'pointer',
  transition: 'background-color 0.2s',
  ':hover': {
    backgroundColor: '#008c92',
  },
});

export const cancelButton = style({
  backgroundColor: '#393e46',
  color: '#eeeeee',
  marginLeft: '12px',
  ':hover': {
    backgroundColor: '#00adb5',
  },
});

export const errorMessage = style({
  color: '#ff69b4',
  marginTop: '12px',
});

export const fieldsetStyle = style({
  border: '1px solid #393e46',
  padding: '16px',
  borderRadius: '4px',
  marginBottom: '16px',
});

export const legendStyle = style({
  padding: '0 4px',
  color: '#00adb5',
});

export const gridContainer = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px',
});
