import { style } from '@vanilla-extract/css';

export const turnsColumn = style({
  flex: '1',
  overflowY: 'auto',
  borderRight: '1px solid #393e46',
  display: 'flex',
  flexDirection: 'column',
  background: '#373b3e',
});

export const turnsHeader = style({
  position: 'sticky',
  top: '0',
  padding: '0 8px',
  borderBottom: '1px solid #3c858a',
  zIndex: '5',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
});

export const turnsListSection = style({
  flex: '1',
  margin: '16px',
  overflowY: 'auto',
  paddingTop: '10px',
});

export const newInstructionControl = style({
  display: 'flex',
  padding: '12px',
  borderTop: '1px solid #393e46',
});

export const instructionTextarea = style({
  flex: '1',
  minHeight: '60px',
  margin: '0 12px 0 0',
  padding: '10px',
  background: '#8c97a4',
  borderRadius: '4px',
  border: '1px solid #373b3e',
  resize: 'vertical',

  ":focus": {
    border: '1px solid #137a7f',
  }
});

export const welcomeMessage = style({
  textAlign: 'center',
  marginTop: '50px',
  color: '#6c757d',
});
