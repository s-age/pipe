import { style, globalStyle } from '@vanilla-extract/css';

export const sessionListColumn = style({
  flex: '0 0 250px',
  padding: '20px',
  borderRight: '1px solid #eee',
  overflowY: 'auto',
  backgroundColor: '#f8f9fa',
});

export const sessionListContainer = style({
  listStyle: 'none',
  padding: '0',
});

export const sessionListItem = style({
  marginBottom: '5px',
});

export const sessionLink = style({
  display: 'block',
  padding: '8px 10px',
  borderRadius: '4px',
  textDecoration: 'none',
  color: '#343a40',
  ':hover': {
    backgroundColor: '#e9ecef',
  },
});

export const sessionLinkActive = style({
  backgroundColor: '#007bff',
  color: 'white',
});

export const sessionIdStyle = style({
  fontSize: '0.8em',
  color: '#6c757d',
  marginLeft: '10px',
});

export const newChatButton = style({
  width: '100%',
  marginBottom: '15px',
});

globalStyle(`${sessionLinkActive} ${sessionIdStyle}`, {
  color: 'rgba(255,255,255,0.8)',
});