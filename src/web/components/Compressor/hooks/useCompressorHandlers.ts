import { useCallback, useState } from 'react'

import type { CompressorFormInputs } from '../schema'

type UseCompressorHandlersProperties = {
  sessionId: string
}

type UseCompressorHandlersReturn = {
  defaultValues: CompressorFormInputs
  onSubmit: (data: CompressorFormInputs) => Promise<void>
  isSubmitting: boolean
  execResult: string | null
}

export const useCompressorHandlers = ({
  sessionId
}: UseCompressorHandlersProperties): UseCompressorHandlersReturn => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [execResult, setExecResult] = useState<string | null>(null)

  const defaultValues: CompressorFormInputs = {
    policy: 'Keep key findings and preserve meaning. Use concise, objective language.',
    targetLength: 1000,
    startTurn: undefined,
    endTurn: undefined
  }

  const onSubmit = useCallback(
    async (data: CompressorFormInputs): Promise<void> => {
      setIsSubmitting(true)
      try {
        const payload = {
          session: sessionId || undefined,
          instruction: `Compress to approximately ${data.targetLength || '[unspecified]'} characters. Policy: ${data.policy}`,
          target_length: data.targetLength || undefined,
          start_turn: data.startTurn || undefined,
          end_turn: data.endTurn || undefined
        }

        const response = await fetch('/api/compress', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          const text = await response.text()
          setExecResult(`Error ${response.status}: ${text}`)

          return
        }

        const result: unknown = await response.json()
        setExecResult(JSON.stringify(result, null, 2))
      } catch (error: unknown) {
        setExecResult(`Error: ${String(error)}`)
      } finally {
        setIsSubmitting(false)
      }
    },
    [sessionId]
  )

  return {
    defaultValues,
    onSubmit,
    isSubmitting,
    execResult
  }
}
