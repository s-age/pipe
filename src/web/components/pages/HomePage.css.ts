import { style } from '@vanilla-extract/css';

export const appContainer = style({
  display: 'flex',
  height: '100vh',
  overflow: 'hidden',
});

export const columnStyle = style({
  flex: '1',
  padding: '20px',
  overflowY: 'auto',
  borderRight: '1px solid #eee',
  selectors: {
    '&:last-child': {
      borderRight: 'none',
    },
  },
});
