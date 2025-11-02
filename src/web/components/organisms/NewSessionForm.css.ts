import { style } from '@vanilla-extract/css';

export const formContainer = style({
  maxWidth: '800px',
  margin: 'auto',
  backgroundColor: '#ffffff',
  padding: '30px',
  borderRadius: '8px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
});

export const fieldsetContainer = style({
  border: '1px solid #dee2e6',
  padding: '15px',
  borderRadius: '4px',
  marginBottom: '15px',
});

export const legendStyle = style({
  padding: '0 5px',
});

export const hyperparametersGrid = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '15px',
});

export const errorMessageStyle = style({
  color: '#dc3545',
  marginTop: '10px',
});
