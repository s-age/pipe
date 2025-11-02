import { style } from '@vanilla-extract/css';
import { colors } from '../../../styles/colors.css.ts';

export const sessionListColumn = style({
  flex: '0 0 250px',
  overflowY: 'auto',
  borderRight: `1px solid ${colors.mediumBackground}`,
  backgroundColor: colors.darkBackground,
  display: 'flex',
  flexDirection: 'column',
});

export const sessionListContainer = style({
  listStyle: 'none',
  padding: '16px',
  margin: '0',
  flexGrow: '1',
});

export const sessionListItem = style({
  marginBottom: '8px',
});

export const sessionLink = style({
  display: 'block',
  padding: '8px',
  borderRadius: '4px',
  textDecoration: 'none',
  color: colors.lightText,
  ':hover': {
    backgroundColor: colors.mediumBackground,
  },
});

export const sessionLinkActive = style({
  backgroundColor: colors.accent,
  color: colors.darkBackground,
  fontWeight: 'bold',
  ':hover': {
    backgroundColor: colors.accentHover,
  },
});

export const sessionIdStyle = style({
  fontSize: '0.8em',
  color: colors.lightText,
  marginLeft: '8px',
});

export const stickyNewChatButtonContainer = style({
  position: 'sticky',
  bottom: 0,
  zIndex: 1,
  padding: '12px',
  borderTop: `1px solid ${colors.mediumBackground}`,
  background: 'inherit'
});