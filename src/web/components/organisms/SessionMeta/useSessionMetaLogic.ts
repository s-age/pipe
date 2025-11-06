import React from 'react'

import { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionMetaLogicProps = {
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
}: UseSessionMetaLogicProps): {
  handleSaveMeta: () => void
  handleMultiStepReasoningChange: (e: React.ChangeEvent<HTMLInputElement>) => void
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
    e: React.ChangeEvent<HTMLInputElement>,
  ): void => {
    if (!currentSessionId || !sessionDetail) return
    onMetaSave(currentSessionId, {
      multi_step_reasoning_enabled: e.target.checked,
    })
  }

  return {
    handleSaveMeta,
    handleMultiStepReasoningChange,
  }
}
