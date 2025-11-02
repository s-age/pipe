import { style, globalStyle } from '@vanilla-extract/css';

export const metaColumn = style({
  flex: '0 0 300px',
  overflowY: 'auto',
  background: '#222831',
});

export const sessionMetaSection = style({
  flex: '1',
  display: 'flex',
  flexDirection: 'column',
  boxSizing: 'border-box',
  minHeight: '0',
  padding: '20px',
});

export const sessionMetaView = style({
  flex: '1',
  overflowY: 'auto',
  paddingBottom: '70px', // Adjust based on the height of the sticky button container
});

export const stickySaveMetaButtonContainer = style({
  position: 'sticky',
  bottom: 0,
  zIndex: 1,
  padding: '12px',
  borderTop: '1px solid #393e46',
  background: 'inherit'
});

export const metaItem = style({
  marginBottom: '15px',
});

export const metaItemLabel = style({
  fontWeight: 'bold',
  marginBottom: '5px',
  display: 'block',
  color: '#fffeec'
});

export const inputFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: '#8c97a4',
  borderRadius: '4px',
  padding: '8px',

  ":focus": {
    border: '1px solid #137a7f',
  }
});

export const textareaFullWidth = style({
  width: '100%',
  boxSizing: 'border-box',
  background: '#8c97a4',
  minHeight: '100px',
  marginTop: '10px',

  ":focus": {
    border: '1px solid #137a7f',
  }
});

export const checkboxLabel = style({
  display: 'flex',
  alignItems: 'center',
  cursor: 'pointer',
  color: '#fffeec',
});

globalStyle(`${checkboxLabel} input[type="checkbox"]`, {
  marginRight: '5px',
});

export const hyperparametersControl = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px',
});

export const sliderValue = style({
  display: 'inline-block',
  width: '30px',
  textAlign: 'right',
  color: '#fffeec',
});

export const todosList = style({
  listStyle: 'none',
  paddingLeft: '0',
});

export const todoItem = style({
  marginBottom: '10px',
  display: 'flex',
  alignItems: 'center',
});

export const todoCheckboxLabel = style({
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  flexGrow: '1',
});

globalStyle(`${todoCheckboxLabel} input[type="checkbox"]`, {
  marginRight: '8px',
});

export const todoTitle = style({
  display: 'inline',
  marginLeft: '8px',
});

export const noItemsMessage = style({
  color: '#6c757d',
  fontStyle: 'italic',
});

export const referencesList = style({
  listStyle: 'none',
  paddingLeft: '0',
});

export const referenceItem = style({
  marginBottom: '10px',
});

export const referenceControls = style({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
});

export const referenceLabel = style({
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  flexGrow: '1',
});

globalStyle(`${referenceLabel} input[type="checkbox"]`, {
  marginRight: '8px',
});

export const referencePath = style({
  wordBreak: 'break-all',
});

export const referencePersistToggle = style({
  background: 'none',
  border: 'none',
  padding: '0',
  cursor: 'pointer',
  marginRight: '5px',
  display: 'flex',
  alignItems: 'center',
});

export const materialIcons = style({
  fontSize: '16px',
  verticalAlign: 'middle',
});

export const ttlControls = style({
  display: 'flex',
  alignItems: 'center',
  marginLeft: '10px',
});

export const ttlButton = style({
  background: '#e9ecef',
  border: '1px solid #ced4da',
  borderRadius: '4px',
  padding: '2px 8px',
  cursor: 'pointer',
  ':hover': {
    backgroundColor: '#dee2e6',
  },
});

export const ttlValue = style({
  padding: '0 8px',
  fontWeight: 'bold',
});

export const referenceCheckboxMargin = style({
  marginRight: '8px',
});

export const deleteTodosButton = style({
  float: 'right',
  marginBottom: '5px',
  backgroundColor: '#dc3545',
});

export const saveMetaButton = style({
  width: '100%',
});
