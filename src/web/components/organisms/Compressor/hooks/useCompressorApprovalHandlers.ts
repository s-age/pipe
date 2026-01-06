import { useCallback } from 'react'

import { useCompressorActions } from './useCompressorActions'

type UseCompressorApprovalHandlersProperties = {
  compressorSessionId: string | null
  onRefresh: () => Promise<void>
  setCompressorSessionId: (id: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  setSummary: (summary: string) => void
}

export const useCompressorApprovalHandlers = ({
  compressorSessionId,
  onRefresh,
  setCompressorSessionId,
  setIsSubmitting,
  setSummary
}: UseCompressorApprovalHandlersProperties): {
  handleApprove: () => Promise<void>
} => {
  const actions = useCompressorActions()

  const handleApprove = useCallback(async (): Promise<void> => {
    if (!compressorSessionId) return

    setIsSubmitting(true)
    await actions.approveCompression(compressorSessionId)
    await onRefresh()
    setSummary('')
    setCompressorSessionId(null)
    setIsSubmitting(false)
  }, [
    actions,
    compressorSessionId,
    onRefresh,
    setSummary,
    setCompressorSessionId,
    setIsSubmitting
  ])

  return { handleApprove }
}
