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
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  compressorSessionId: string | null
  setCompressorSessionId: (id: string | null) => void
  onRefresh: () => Promise<void>
}

export type UseCompressorActionsReturn = {
  handleExecute: () => Promise<void>
  handleApprove: () => Promise<void>
  handleDeny: () => Promise<void>
}

export const useCompressorActions = ({
  sessionId,
  setSummary,
  setError,
  setIsSubmitting,
  compressorSessionId,
  setCompressorSessionId,
  onRefresh
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
        start_turn: formValues.startTurn,
        end_turn: formValues.endTurn
      }
      const response = await createCompressor(requestData)
      // Log full response for debugging (helps diagnose missing summary)
      console.log('createCompressor response:', response)

      // Store the compressor session ID for approval
      if (response?.session_id) {
        setCompressorSessionId(response.session_id)
      }

      // If the server returned a verified summary, use it.
      if (response?.summary) {
        setSummary(response.summary)
      } else if (response?.message) {
        setSummary(response.message)
      } else if (response?.session_id) {
        // Provide a clearer user-facing message instead of raw session id
        setSummary(
          `Compression started. Verifier session created (id: ${response.session_id}). The verified summary will appear here when ready.`
        )
      } else {
        setSummary(
          'Compression started. The verified summary will appear here when ready.'
        )
      }
    } catch (error_: unknown) {
      setError(String(error_))
    } finally {
      setIsSubmitting(false)
    }
  }, [form, sessionId, setSummary, setError, setIsSubmitting, setCompressorSessionId])

  const handleApprove = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    try {
      if (!compressorSessionId) {
        throw new Error('Compressor session ID not available')
      }
      await approveCompressor(compressorSessionId)
      setSummary('')
      setCompressorSessionId(null)
      if (onRefresh) {
        await onRefresh()
      }
    } catch (error_: unknown) {
      setError(String(error_))
    } finally {
      setIsSubmitting(false)
    }
  }, [
    compressorSessionId,
    setIsSubmitting,
    setSummary,
    setError,
    setCompressorSessionId,
    onRefresh
  ])

  const handleDeny = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    try {
      if (!compressorSessionId) {
        throw new Error('Compressor session ID not available')
      }
      await denyCompressor(compressorSessionId)
      setSummary('')
      setCompressorSessionId(null)
    } catch (error_: unknown) {
      setError(String(error_))
    } finally {
      setIsSubmitting(false)
    }
  }, [
    compressorSessionId,
    setIsSubmitting,
    setSummary,
    setError,
    setCompressorSessionId
  ])

  return {
    handleExecute,
    handleApprove,
    handleDeny
  }
}
