import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

// 各ターンを囲むFlexboxコンテナとして機能
export const turnWrapper = style({
  display: 'flex',
  width: '100%',
  marginBottom: '8px'
})

// ユーザーのターンを右寄せにするためのスタイル
export const userTaskAligned = style({
  justifyContent: 'flex-end'
})

// モデルの応答などを左寄せにするためのスタイル
export const otherTurnAligned = style({
  justifyContent: 'flex-start'
})

// 各ターンのコンテンツ部分の共通スタイル
export const turnContentBase = style({
  border: `1px solid ${colors.accent}`,
  borderRadius: '8px',
  padding: '8px',
  // Slightly stronger, soft shadow for better elevation. Added transition and
  // hover lift so turns feel interactive without being flashy.
  boxShadow: '0 6px 18px rgba(2,6,23,0.12)',
  transition: 'transform 120ms ease, box-shadow 120ms ease',
  ':hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 12px 30px rgba(2,6,23,0.18)'
  },
  width: '75%', // 各ターンのコンテンツ幅
  // Allow flex children to shrink and allow internal text to wrap
  minWidth: 0
})

export const turnHeader = style({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
})

export const turnHeaderInfo = style({
  display: 'flex',
  alignItems: 'center'
})

export const turnIndexStyle = style({
  marginRight: '8px',
  fontWeight: 'bold'
})

export const turnTimestamp = style({
  fontWeight: 'normal',
  marginLeft: '8px'
})

export const turnHeaderControls = style({
  display: 'flex',
  gap: '4px'
})

export const turnContent = style({
  // Ensure long words / URLs wrap and pre-formatted text keeps newlines
  wordWrap: 'break-word',
  overflowWrap: 'anywhere',
  wordBreak: 'break-word',
  whiteSpace: 'pre-wrap',
  color: colors.offWhite,
  padding: '0 12px'
})

export const rawMarkdown = style({
  display: 'none'
})

export const renderedMarkdown = style({
  // GitHub Markdown CSSを適用するためのクラス名
  // className="markdown-body"
  padding: '12px',
  marginTop: '8px'
})

globalStyle(`${renderedMarkdown}.markdown-body`, {
  // GitHub Markdown CSSのスタイルをここにコピーするか、
  // 外部CSSとして読み込む場合は不要
})

export const toolResponseContent = style({
  padding: '12px',
  borderRadius: '4px',
  color: colors.offWhite
})

export const statusSuccess = style({
  color: colors.accent,
  fontWeight: 'bold'
})

export const statusError = style({
  color: colors.error,
  fontWeight: 'bold'
})

export const editablePre = style({
  padding: '0 12px',
  borderRadius: '4px',
  color: colors.offWhite,
  boxSizing: 'border-box',
  // Allow preformatted text to wrap within the container instead of overflowing.
  // Keep newlines but allow long words/URLs and CJK text to break.
  whiteSpace: 'pre-wrap',
  overflowWrap: 'anywhere',
  wordWrap: 'break-word',
  wordBreak: 'break-word',
  // Helpful for East Asian text line breaking
  lineBreak: 'anywhere'
})

export const editTextArea = style({
  width: '100%',
  minHeight: '120px',
  boxSizing: 'border-box',
  padding: '12px',
  borderRadius: '4px',
  border: `1px solid ${colors.accent}`,
  whiteSpace: 'pre-wrap',
  wordWrap: 'break-word',
  backgroundColor: colors.darkBackground,
  color: colors.offWhite
})

export const editButtonContainer = style({
  textAlign: 'right',
  marginTop: '12px'
})

export const materialIcons = style({
  fontFamily: 'Material Icons',
  fontSize: '16px',
  verticalAlign: 'middle'
})

export const forkButtonIcon = style({
  background: colors.purpleAccent,
  borderRadius: '4px',
  padding: '4px'
})

export const deleteButtonIcon = style({
  background: colors.error,
  borderRadius: '4px',
  padding: '4px'
})

export const copyButtonIcon = style({
  background: colors.lightBlue,
  borderRadius: '4px',
  padding: '4px',
  color: colors.darkBackground
})

export const editButtonIcon = style({
  background: colors.mediumBlue,
  borderRadius: '4px',
  padding: '4px',
  color: colors.mediumBackground
})
