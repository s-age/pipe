import { style } from '@vanilla-extract/css';

export const bodyStyle = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '20px',
  backgroundColor: '#f8f9fa',
  color: '#343a40',
});

export const containerStyle = style({
  maxWidth: '800px',
  margin: 'auto',
  backgroundColor: '#ffffff',
  padding: '30px',
  borderRadius: '8px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
});

export const h1Style = style({
  color: '#007bff',
  borderBottom: '1px solid #dee2e6',
  paddingBottom: '10px',
  marginBottom: '20px',
});

export const labelStyle = style({
  display: 'block',
  marginBottom: '5px',
  fontWeight: 'bold',
  color: '#495057',
});

export const inputFieldStyle = style({
  width: 'calc(100% - 22px)',
  padding: '10px',
  marginBottom: '15px',
  border: '1px solid #ced4da',
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
});

export const textareaFieldStyle = style({
  minHeight: '100px',
  resize: 'vertical',
});

export const actionButton = style({
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  padding: '10px 20px',
  fontSize: '1em',
  borderRadius: '4px',
  cursor: 'pointer',
  transition: 'background-color 0.2s',
  ':hover': {
    backgroundColor: '#0056b3',
  },
});

export const cancelButton = style({
  backgroundColor: '#6c757d',
  marginLeft: '10px',
  ':hover': {
    backgroundColor: '#5a6268',
  },
});

export const errorMessage = style({
  color: '#dc3545',
  marginTop: '10px',
});

export const fieldsetStyle = style({
  border: '1px solid #dee2e6',
  padding: '15px',
  borderRadius: '4px',
  marginBottom: '15px',
});

export const legendStyle = style({
  padding: '0 5px',
});

export const gridContainer = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '15px',
});
