import { style, globalStyle } from '@vanilla-extract/css';

// 各ターンを囲むFlexboxコンテナとして機能
export const turnWrapper = style({
  display: 'flex',
  width: '100%',
  marginBottom: '16px', // 各ターンの下に余白
});

// ユーザーのターンを右寄せにするためのスタイル
export const userTaskAligned = style({
  justifyContent: 'flex-end',
});

// モデルの応答などを左寄せにするためのスタイル
export const otherTurnAligned = style({
  justifyContent: 'flex-start',
});

// 各ターンのコンテンツ部分の共通スタイル
export const turnContentBase = style({
  backgroundColor: '#8c97a4',
  border: '1px solid #222831',
  borderRadius: '8px',
  padding: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  width: '75%', // 各ターンのコンテンツ幅
});

export const turnHeader = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
});

export const turnHeaderInfo = style({
  display: 'flex',
  alignItems: 'center',
});

export const turnIndexStyle = style({
  marginRight: '8px',
  fontWeight: 'bold',
});

export const turnTimestamp = style({
  fontWeight: 'normal',
  marginLeft: '8px',
});

export const turnHeaderControls = style({
  display: 'flex',
  gap: '4px',
});

export const turnContent = style({
  wordWrap: 'break-word',
  whiteSpace: 'pre-wrap',
  color: '#fffeec',
  padding: '0 12px',
});

export const rawMarkdown = style({
  display: 'none',
});

export const renderedMarkdown = style({
  // GitHub Markdown CSSを適用するためのクラス名
  // className="markdown-body"
  padding: '12px',
  marginTop: '8px',
});

globalStyle(`${renderedMarkdown}.markdown-body`, {
  // GitHub Markdown CSSのスタイルをここにコピーするか、
  // 外部CSSとして読み込む場合は不要
});

export const toolResponseContent = style({
  padding: '12px',
  borderRadius: '4px',
  color: '#fffeec',
});

export const statusSuccess = style({
  color: '#00adb5',
  fontWeight: 'bold',
});

export const statusError = style({
  color: '#e12885',
  fontWeight: 'bold',
});

export const editablePre = style({
  padding: '0 12px',
  borderRadius: '4px',
  color: '#fffeec',
  boxSizing: 'border-box',
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
  color: '#fffeec',
});

export const editButtonContainer = style({
  textAlign: 'right',
  marginTop: '12px',
});