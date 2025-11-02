import { style } from '@vanilla-extract/css';

export const baseButtonStyle = style({
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
