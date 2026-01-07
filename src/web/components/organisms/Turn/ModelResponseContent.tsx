import { clsx } from 'clsx'
import { marked } from 'marked'
import type { JSX } from 'react'

import { Emphasis } from '@/components/atoms/Emphasis'
import { Strong } from '@/components/atoms/Strong'
import { Box } from '@/components/molecules/Box'
import { Paragraph } from '@/components/molecules/Paragraph'

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
  <Box className={turnContent}>
    {isCompressed && (
      <Paragraph>
        <Strong>
          <Emphasis>-- History Compressed --</Emphasis>
        </Strong>
      </Paragraph>
    )}
    <Box className={rawMarkdown}>{content}</Box>
    {!isStreaming && (
      <Box
        className={clsx(renderedMarkdown, 'markdown-body')}
        dangerouslySetInnerHTML={{ __html: marked.parse(content.trim()) }}
      />
    )}
  </Box>
)
