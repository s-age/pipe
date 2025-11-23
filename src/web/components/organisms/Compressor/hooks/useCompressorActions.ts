import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import {
  approveCompressor,
  createCompressor,
  denyCompressor
} from '@/lib/api/session/compress'

type UseCompressorActionsProperties = {
  sessionId: string
  setSummary: (summary: string) => void
  setStage: (stage: 'form' | 'approval') => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
}

export type UseCompressorActionsReturn = {
  handleExecute: () => Promise<void>
  handleApprove: () => Promise<void>
  handleDeny: () => Promise<void>
}

export const useCompressorActions = ({
  sessionId,
  setSummary,
  setStage,
  setError,
  setIsSubmitting
}: UseCompressorActionsProperties): UseCompressorActionsReturn => {
  const form = useOptionalFormContext()

  const handleExecute = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    setError(null)
    try {
      const formValues = form?.getValues()
      if (!formValues) {
        throw new Error('Form values not available')
      }
      const requestData = {
        session_id: sessionId,
        policy: formValues.policy,
        target_length: formValues.targetLength ?? 500,
        start_turn: formValues.startTurn - 1,
        end_turn: formValues.endTurn - 1
      }
      const response = await createCompressor(requestData)
      // TODO: Get summary from response or another API
      setSummary(`Compression session created: ${response.session_id}`)
      setStage('approval')
    } catch (error_: unknown) {
      setError(String(error_))
    } finally {
      setIsSubmitting(false)
    }
  }, [form, sessionId, setSummary, setStage, setError, setIsSubmitting])

  const handleApprove = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    try {
      await approveCompressor(sessionId)
      setStage('form')
      setSummary('')
    } catch (error_: unknown) {
      setError(String(error_))
    } finally {
      setIsSubmitting(false)
    }
  }, [sessionId, setIsSubmitting, setStage, setSummary, setError])

  const handleDeny = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    try {
      await denyCompressor(sessionId)
      setStage('form')
      setSummary('')
    } catch (error_: unknown) {
      setError(String(error_))
    } finally {
      setIsSubmitting(false)
    }
  }, [sessionId, setIsSubmitting, setStage, setSummary, setError])

  return {
    handleExecute,
    handleApprove,
    handleDeny
  }
}
