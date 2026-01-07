import { style, globalStyle } from '@vanilla-extract/css'

import { colors } from '../../../styles/colors.css'

// 各ターンを囲むFlexboxコンテナとして機能
export const turnWrapper = style({
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
  width: '75%',
  minWidth: 0,
  border: `1px solid ${colors.cyan}`,
  boxShadow: '0 0 6px #00ffff, inset 0 0 6px #00ffff33',
  transition: 'transform 120ms ease, box-shadow 120ms ease'
})

export const turnHeader = style({
  // Flex コンポーネントで justify="between" と align="center" を指定
})

export const turnHeaderInfo = style({
  // Flex コンポーネントで align="center" を指定
})

export const turnIndexStyle = style({
  marginRight: '8px'
  // fontWeight は Text コンポーネントの weight="bold" で指定
})

export const turnTimestamp = style({
  marginLeft: '8px',
  fontWeight: 'normal'
})

export const turnHeaderControls = style({
  // Flex コンポーネントで gap="s" を指定
})

export const turnContent = style({
  padding: '0 12px',
  color: colors.white,
  wordWrap: 'break-word',
  overflowWrap: 'anywhere',
  wordBreak: 'break-word',
  whiteSpace: 'pre-wrap'
})

export const rawMarkdown = style({
  display: 'none'
})

export const renderedMarkdown = style({
  marginTop: '8px',
  padding: '12px'
})

globalStyle(`${renderedMarkdown}.markdown-body`, {
  // GitHub Markdown CSSのスタイルをここにコピーするか、
  // 外部CSSとして読み込む場合は不要
})

export const toolResponseContent = style({
  padding: '12px',
  borderRadius: '4px',
  color: colors.white
})

export const statusSuccess = style({
  fontWeight: 'bold',
  color: colors.cyan
})

export const statusError = style({
  fontWeight: 'bold',
  color: colors.red
})

export const editablePre = style({
  boxSizing: 'border-box',
  padding: '0 12px',
  borderRadius: '4px',
  lineHeight: '1.8em',
  color: colors.white,
  whiteSpace: 'pre-wrap',
  overflowWrap: 'anywhere',
  wordWrap: 'break-word',
  wordBreak: 'break-word',
  lineBreak: 'anywhere'
})

export const editTextArea = style({
  width: '100%',
  minHeight: '120px',
  boxSizing: 'border-box',
  padding: '12px',
  border: `1px solid ${colors.cyan}`,
  borderRadius: '4px',
  color: colors.white,
  backgroundColor: colors.black,
  whiteSpace: 'pre-wrap',
  wordWrap: 'break-word'
})

export const editButtonContainer = style({
  marginTop: '12px',
  textAlign: 'right'
})

export const materialIcons = style({
  fontFamily: 'Material Icons',
  fontSize: '16px',
  verticalAlign: 'middle'
})

export const forkButtonIcon = style({
  padding: '4px',
  borderRadius: '4px',
  background: colors.cyanAlt
})

export const deleteButtonIcon = style({
  padding: '4px',
  borderRadius: '4px',
  background: colors.red
})

export const copyButtonIcon = style({
  padding: '4px',
  borderRadius: '4px',
  color: colors.black,
  background: colors.lightBlue
})

export const editButtonIcon = style({
  padding: '4px',
  borderRadius: '4px',
  color: colors.gray,
  background: colors.mediumBlue
})
