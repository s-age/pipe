import { style } from '@vanilla-extract/css';

export const textareaStyle = style({
  width: 'calc(100% - 22px)',
  padding: '10px',
  marginBottom: '15px',
  border: '1px solid #ced4da',
  borderRadius: '4px',
  fontSize: '1em',
  boxSizing: 'border-box',
  minHeight: '100px',
  resize: 'vertical',
});
