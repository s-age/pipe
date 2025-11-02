import { style } from '@vanilla-extract/css';

export const pageContainer = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '20px',
  backgroundColor: '#f8f9fa',
  color: '#343a40',
});

export const errorMessageStyle = style({
  color: '#dc3545',
  marginTop: '10px',
  textAlign: 'center',
});
