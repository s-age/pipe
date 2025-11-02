import { style, globalStyle } from '@vanilla-extract/css';

export const turnStyle = style({
  backgroundColor: '#393e46',
  border: '1px solid #222831',
  borderRadius: '8px',
  marginBottom: '16px',
  padding: '16px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
});

export const turnHeader = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '8px',
  paddingBottom: '8px',
  borderBottom: '1px solid #222831',
});

export const turnHeaderInfo = style({
  display: 'flex',
  alignItems: 'center',
});

export const turnIndexStyle = style({
  color: '#00adb5',
  marginRight: '8px',
  fontWeight: 'bold',
});

export const turnTimestamp = style({
  fontWeight: 'normal',
  color: '#eeeeee',
  marginLeft: '8px',
});

export const turnHeaderControls = style({
  display: 'flex',
  gap: '4px',
});

export const turnContent = style({
  wordWrap: 'break-word',
  whiteSpace: 'pre-wrap',
  color: '#eeeeee',
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
  backgroundColor: '#222831',
  padding: '12px',
  borderRadius: '4px',
  border: '1px solid #00adb5',
  color: '#eeeeee',
});

export const statusSuccess = style({
  color: '#00adb5',
  fontWeight: 'bold',
});

export const statusError = style({
  color: '#ff69b4',
  fontWeight: 'bold',
});

export const editablePre = style({
  backgroundColor: '#222831',
  padding: '12px',
  borderRadius: '4px',
  border: '1px solid #00adb5',
  color: '#eeeeee',
});

export const editTextArea = style({
  width: '100%',
  minHeight: '120px',
  boxSizing: 'border-box',
  padding: '12px',
  borderRadius: '4px',
  border: '1px solid #00adb5',
  whiteSpace: 'pre-wrap',
  wordWrap: 'break-word',
  backgroundColor: '#222831',
  color: '#eeeeee',
});

export const editButtonContainer = style({
  textAlign: 'right',
  marginTop: '12px',
});