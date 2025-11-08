import type React from 'react'

import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionMetaLogicProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
  temperature: number
  topP: number
  topK: number
}

export const useSessionMetaLogic = ({
  sessionDetail,
  currentSessionId,
  onMetaSave,
  temperature,
  topP,
  topK,
}: UseSessionMetaLogicProperties): {
  handleSaveMeta: () => void
  handleMultiStepReasoningChange: (event: React.ChangeEvent<HTMLInputElement>) => void
} => {
  const handleSaveMeta = (): void => {
    if (!currentSessionId || !sessionDetail) return
    const meta: EditSessionMetaRequest = {
      multi_step_reasoning_enabled: sessionDetail.multi_step_reasoning_enabled,
      hyperparameters: {
        temperature: temperature,
        top_p: topP,
        top_k: topK,
      },
    }
    onMetaSave(currentSessionId, meta)
  }

  const handleMultiStepReasoningChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ): void => {
    if (!currentSessionId || !sessionDetail) return
    onMetaSave(currentSessionId, {
      multi_step_reasoning_enabled: event.target.checked,
    })
  }

  return {
    handleSaveMeta,
    handleMultiStepReasoningChange,
  }
}
