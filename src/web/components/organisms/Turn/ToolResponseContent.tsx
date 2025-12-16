import type { JSX } from 'react'

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
    <div className={toolResponseContent}>
      <strong>Status: </strong>
      <span className={statusClass}>{response.status}</span>
      {response.message !== undefined && response.message !== null && (
        <pre>{JSON.stringify(response.message, null, 2)}</pre>
      )}
    </div>
  )
}
