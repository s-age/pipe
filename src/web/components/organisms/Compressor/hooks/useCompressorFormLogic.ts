import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'

import { useCompressorActions } from './useCompressorActions'
import type { CompressorFormInputs } from '../schema'

type UseCompressorFormLogicProperties = {
  compressorSessionId: string | null
  sessionId: string
  onRefresh: () => Promise<void>
  setCompressorSessionId: (id: string | null) => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  setSummary: (summary: string) => void
}

export const useCompressorFormLogic = ({
  sessionId,
  setCompressorSessionId,
  setError,
  setIsSubmitting,
  setSummary
}: UseCompressorFormLogicProperties): { onExecuteClick: () => void } => {
  const formContext = useOptionalFormContext()
  const actions = useCompressorActions()

  const onExecuteClick = useCallback((): void => {
    const values = formContext?.getValues() as CompressorFormInputs | undefined
    if (!values) return

    setIsSubmitting(true)
    setError(null)

    const requestData = {
      sessionId: sessionId,
      policy: values.policy,
      targetLength: values.targetLength ?? 500,
      startTurn: values.startTurn ?? 1,
      endTurn: values.endTurn ?? 0
    }

    void actions.executeCompression(requestData).then((response) => {
      if (response?.sessionId) {
        setCompressorSessionId(response.sessionId)
      }

      if (response?.summary && response.summary.startsWith('Rejected:')) {
        setError(response.summary)
        setSummary('')
      } else if (response?.summary) {
        setSummary(response.summary)
      } else if (response?.message) {
        setSummary(response.message)
      } else if (response?.sessionId) {
        setSummary(
          `Compression started. Verifier session created (id: ${response.sessionId}). The verified summary will appear here when ready.`
        )
      } else {
        setSummary(
          'Compression started. The verified summary will appear here when ready.'
        )
      }

      setIsSubmitting(false)
    })
  }, [
    formContext,
    actions,
    sessionId,
    setSummary,
    setError,
    setIsSubmitting,
    setCompressorSessionId
  ])

  return { onExecuteClick }
}
