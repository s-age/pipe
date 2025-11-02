import { style } from '@vanilla-extract/css';

export const turnsColumn = style({
  flex: '1',
  padding: '20px',
  overflowY: 'auto',
  borderRight: '1px solid #eee',
  display: 'flex',
  flexDirection: 'column',
});

export const turnsHeader = style({
  position: 'sticky',
  top: '0',
  backgroundColor: '#f0f2f5',
  padding: '10px 20px',
  borderBottom: '1px solid #dee2e6',
  zIndex: '5',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
});

export const turnsListSection = style({
  flex: '1',
  overflowY: 'auto',
  paddingTop: '10px',
});

export const newInstructionControl = style({
  display: 'flex',
  marginTop: '20px',
  paddingTop: '10px',
  borderTop: '1px solid #eee',
});

export const instructionTextarea = style({
  flex: '1',
  minHeight: '60px',
  marginRight: '10px',
  padding: '10px',
  borderRadius: '4px',
  border: '1px solid #ced4da',
  resize: 'vertical',
});

export const welcomeMessage = style({
  textAlign: 'center',
  marginTop: '50px',
  color: '#6c757d',
});
