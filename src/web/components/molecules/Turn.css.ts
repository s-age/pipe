import { style, globalStyle } from '@vanilla-extract/css';

export const turnStyle = style({
  backgroundColor: '#fff',
  border: '1px solid #e0e0e0',
  borderRadius: '8px',
  marginBottom: '15px',
  padding: '15px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
});

export const turnHeader = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px',
  paddingBottom: '10px',
  borderBottom: '1px solid #eee',
});

export const turnHeaderInfo = style({
  display: 'flex',
  alignItems: 'center',
});

export const turnIndexStyle = style({
  color: '#007bff',
  marginRight: '10px',
  fontWeight: 'bold',
});

export const turnTimestamp = style({
  fontWeight: 'normal',
  color: '#999',
  marginLeft: '10px',
});

export const turnHeaderControls = style({
  display: 'flex',
  gap: '5px',
});

export const turnContent = style({
  wordWrap: 'break-word',
  whiteSpace: 'pre-wrap',
});

export const rawMarkdown = style({
  display: 'none',
});

export const renderedMarkdown = style({
  // GitHub Markdown CSSを適用するためのクラス名
  // className="markdown-body"
});

globalStyle(`${renderedMarkdown}.markdown-body`, {
  // GitHub Markdown CSSのスタイルをここにコピーするか、
  // 外部CSSとして読み込む場合は不要
});

export const toolResponseContent = style({
  backgroundColor: '#e9ecef',
  padding: '10px',
  borderRadius: '4px',
  border: '1px solid #dee2e6',
});

export const statusSuccess = style({
  color: '#28a745',
  fontWeight: 'bold',
});

export const statusError = style({
  color: '#dc3545',
  fontWeight: 'bold',
});

export const editablePre = style({
  backgroundColor: '#f4f4f4',
  padding: '10px',
  borderRadius: '4px',
  border: '1px solid #ddd',
});

export const editTextArea = style({
  width: '100%',
  minHeight: '120px',
  boxSizing: 'border-box',
  padding: '10px',
  borderRadius: '5px',
  border: '1px solid #ced4da',
  whiteSpace: 'pre-wrap',
  wordWrap: 'break-word',
});

export const editButtonContainer = style({
  textAlign: 'right',
  marginTop: '10px',
});