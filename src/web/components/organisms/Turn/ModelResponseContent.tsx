import { marked } from 'marked'
import type { JSX } from 'react'

import { turnContent, rawMarkdown, renderedMarkdown } from './style.css'

type ModelResponseContentProperties = {
  content: string
  isCompressed?: boolean
  isStreaming?: boolean
}

export const ModelResponseContent = ({
  content,
  isCompressed = false,
  isStreaming = false
}: ModelResponseContentProperties): JSX.Element => (
  <div className={turnContent}>
    {isCompressed && (
      <p>
        <strong>
          <em>-- History Compressed --</em>
        </strong>
      </p>
    )}
    <div className={rawMarkdown}>{content}</div>
    {!isStreaming && (
      <div
        className={`${renderedMarkdown} markdown-body`}
        dangerouslySetInnerHTML={{ __html: marked.parse(content.trim()) }}
      />
    )}
  </div>
)
