import { useCallback } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
  onRefresh: () => Promise<void>
  setSessionDetail?: (data: SessionDetail | null) => void
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  sessionDetail,
  onRefresh,
  setSessionDetail
}: UseMultiStepReasoningHandlersProperties): {
  handleMultiStepReasoningChange: (
    event: React.ChangeEvent<HTMLInputElement>
  ) => Promise<void>
} => {
  const { updateMultiStepReasoning } = useMultiStepReasoningActions()

  const handleMultiStepReasoningChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      if (!currentSessionId || !sessionDetail) return

      try {
        // Read checked synchronously to avoid relying on the synthetic event
        // after an await (React may pool events).
        const checked = event.target.checked

        const result = await updateMultiStepReasoning(currentSessionId, {
          multi_step_reasoning_enabled: checked
        })

        // Update local session detail immediately from the API response so the UI
        // reflects the change without waiting for a full sessions refresh.
        if (result?.session && typeof setSessionDetail === 'function') {
          setSessionDetail(result.session)
        }

        // Also refresh the session list if needed (keeps the session tree canonical).
        await onRefresh()
      } catch {
        // Toasts are displayed by the action hook. Swallow here to keep UI stable.
      }
    },
    [
      currentSessionId,
      sessionDetail,
      onRefresh,
      updateMultiStepReasoning,
      setSessionDetail
    ]
  )

  return { handleMultiStepReasoningChange }
}
