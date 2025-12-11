import { useCallback } from 'react'

import {
  approveCompressor,
  createCompressor,
  denyCompressor
} from '@/lib/api/session/compress'

import type { CompressorFormInputs } from '../schema'

export type UseCompressorActionsProperties = {
  sessionId: string
  setSummary: (summary: string) => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  compressorSessionId: string | null
  setCompressorSessionId: (id: string | null) => void
  onRefresh: () => Promise<void>
}

export type UseCompressorActionsReturn = {
  handleExecute: (data: CompressorFormInputs) => Promise<void>
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
  const handleExecute = useCallback(
    async (data: CompressorFormInputs): Promise<void> => {
      setIsSubmitting(true)
      setError(null)
      try {
        const requestData = {
          sessionId: sessionId,
          policy: data.policy,
          targetLength: data.targetLength ?? 500,
          startTurn: data.startTurn ?? 1,
          endTurn: data.endTurn ?? 0
        }
        const response = await createCompressor(requestData)

        // Store the compressor session ID for approval
        if (response?.sessionId) {
          setCompressorSessionId(response.sessionId)
        }

        // Check if the summary was rejected by verifier
        if (response?.summary && response.summary.startsWith('Rejected:')) {
          // Extract rejection reason from the summary
          setError(response.summary)
          setSummary('')

          return
        }

        // If the server returned a verified summary, use it.
        if (response?.summary) {
          setSummary(response.summary)
        } else if (response?.message) {
          setSummary(response.message)
        } else if (response?.sessionId) {
          // Provide a clearer user-facing message instead of raw session id
          setSummary(
            `Compression started. Verifier session created (id: ${response.sessionId}). The verified summary will appear here when ready.`
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
    },
    [sessionId, setSummary, setError, setIsSubmitting, setCompressorSessionId]
  )

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
