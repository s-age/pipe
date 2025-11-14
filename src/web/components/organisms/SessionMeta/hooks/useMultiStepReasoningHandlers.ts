import { useCallback } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  sessionDetail
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

        await updateMultiStepReasoning(currentSessionId, {
          multi_step_reasoning_enabled: checked
        })

        // No need to update session detail or refresh the session tree.
        // The checkbox state is managed by the form, and multi_step_reasoning_enabled
        // does not affect the session tree structure or display.
      } catch {
        // Toasts are displayed by the action hook. Swallow here to keep UI stable.
      }
    },
    [currentSessionId, sessionDetail, updateMultiStepReasoning]
  )

  return { handleMultiStepReasoningChange }
}
