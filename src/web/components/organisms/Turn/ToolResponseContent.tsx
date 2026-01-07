import type { JSX } from 'react'

import { Strong } from '@/components/atoms/Strong'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Code } from '@/components/molecules/Code'

import { toolResponseContent, statusSuccess, statusError } from './style.css'

type ToolResponseContentProperties = {
  response: {
    status: string
    message?: unknown
  }
}

export const ToolResponseContent = ({
  response
}: ToolResponseContentProperties): JSX.Element => {
  const statusClass =
    typeof response.status === 'string' &&
    response.status.toLowerCase().startsWith('succe')
      ? statusSuccess
      : statusError

  return (
    <Box className={toolResponseContent}>
      <Strong>Status: </Strong>
      <Text className={statusClass}>{response.status}</Text>
      {response.message !== undefined && response.message !== null && (
        <Code block={true}>{JSON.stringify(response.message, null, 2)}</Code>
      )}
    </Box>
  )
}
