import { style } from '@vanilla-extract/css';

export const bodyStyle = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '20px',
  backgroundColor: '#fffeec',
  color: '#373b3e',
});

export const containerStyle = style({
  maxWidth: '800px',
  margin: 'auto',
  backgroundColor: '#fffeec',
  padding: '28px',
  borderRadius: '8px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
});

export const h1Style = style({
  color: '#137a7f',
  borderBottom: '1px solid #bec8d1',
  paddingBottom: '12px',
  marginBottom: '20px',
});

export const labelStyle = style({
  display: 'block',
  marginBottom: '4px',
  fontWeight: 'bold',
  color: '#bec8d1',
});

export const inputFieldStyle = style({
  width: 'calc(100% - 24px)',
  padding: '12px',
  marginBottom: '16px',
  border: '1px solid #bec8d1',
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
});

export const textareaFieldStyle = style({
  minHeight: '100px',
  resize: 'vertical',
});

export const actionButton = style({
  backgroundColor: '#137a7f',
  color: 'white',
  border: 'none',
  padding: '12px 20px',
  fontSize: '1em',
  borderRadius: '4px',
  cursor: 'pointer',
  transition: 'background-color 0.2s',
  ':hover': {
    backgroundColor: '#86cecb',
  },
});

export const cancelButton = style({
  backgroundColor: '#bec8d1',
  marginLeft: '12px',
  ':hover': {
    backgroundColor: '#86cecb',
  },
});

export const errorMessage = style({
  color: '#e12885',
  marginTop: '12px',
});

export const fieldsetStyle = style({
  border: '1px solid #bec8d1',
  padding: '16px',
  borderRadius: '4px',
  marginBottom: '16px',
});

export const legendStyle = style({
  padding: '0 4px',
});

export const gridContainer = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px',
});
