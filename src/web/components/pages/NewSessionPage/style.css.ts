import { style } from '@vanilla-extract/css';

export const pageContainer = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '0',
  backgroundColor: '#373b3e',
  color: '#343a40',
  padding: '16px',
});

export const errorMessageStyle = style({
  color: '#dc3545',
  marginTop: '10px',
  textAlign: 'center',
});
