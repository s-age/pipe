import { useState, useCallback } from 'react'

import { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionHyperparametersProps = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
}

export const useSessionHyperparameters = ({
  sessionDetail,
  currentSessionId,
  onMetaSave,
}: UseSessionHyperparametersProps): {
  temperature: number
  setTemperature: React.Dispatch<React.SetStateAction<number>>
  handleTemperatureMouseUp: () => void
  topP: number
  setTopP: React.Dispatch<React.SetStateAction<number>>
  handleTopPMouseUp: () => void
  topK: number
  setTopK: React.Dispatch<React.SetStateAction<number>>
  handleTopKMouseUp: () => void
} => {
  const [temperature, setTemperature] = useState(
    sessionDetail?.hyperparameters?.temperature || 0.7,
  )
  const [topP, setTopP] = useState(sessionDetail?.hyperparameters?.top_p || 0.9)
  const [topK, setTopK] = useState(sessionDetail?.hyperparameters?.top_k || 5)

  const handleTemperatureMouseUp = useCallback((): void => {
    if (!currentSessionId || !sessionDetail) return
    onMetaSave(currentSessionId, {
      hyperparameters: {
        ...sessionDetail.hyperparameters,
        temperature: temperature,
      },
    })
  }, [currentSessionId, onMetaSave, temperature, sessionDetail])

  const handleTopPMouseUp = useCallback((): void => {
    if (!currentSessionId || !sessionDetail) return
    onMetaSave(currentSessionId, {
      hyperparameters: {
        ...sessionDetail.hyperparameters,
        top_p: topP,
      },
    })
  }, [currentSessionId, onMetaSave, topP, sessionDetail])

  const handleTopKMouseUp = useCallback((): void => {
    if (!currentSessionId || !sessionDetail) return
    onMetaSave(currentSessionId, {
      hyperparameters: {
        ...sessionDetail.hyperparameters,
        top_k: topK,
      },
    })
  }, [currentSessionId, onMetaSave, topK, sessionDetail])

  return {
    temperature,
    setTemperature,
    handleTemperatureMouseUp,
    topP,
    setTopP,
    handleTopPMouseUp,
    topK,
    setTopK,
    handleTopKMouseUp,
  }
}
