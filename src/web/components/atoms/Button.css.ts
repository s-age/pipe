import { style } from '@vanilla-extract/css';

export const baseButtonStyle = style({
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
