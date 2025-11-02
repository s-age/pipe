import { style, globalStyle } from '@vanilla-extract/css';

export const sessionListColumn = style({
  flex: '0 0 250px',
  padding: '20px',
  borderRight: '1px solid #393e46',
  overflowY: 'auto',
  backgroundColor: '#222831',
});

export const sessionListContainer = style({
  listStyle: 'none',
  padding: '0',
});

export const sessionListItem = style({
  marginBottom: '4px',
});

export const sessionLink = style({
  display: 'block',
  padding: '8px 12px',
  borderRadius: '4px',
  textDecoration: 'none',
  color: '#eeeeee',
  ':hover': {
    backgroundColor: '#393e46',
  },
});

export const sessionLinkActive = style({
  backgroundColor: '#00adb5',
  color: '#222831',
});

export const sessionIdStyle = style({
  fontSize: '0.8em',
  color: '#eeeeee',
  marginLeft: '8px',
});

export const newChatButton = style({
  width: '100%',
  marginBottom: '16px',
});

globalStyle(`${sessionLinkActive} ${sessionIdStyle}`, {
  color: 'rgba(34,40,49,0.8)',
});