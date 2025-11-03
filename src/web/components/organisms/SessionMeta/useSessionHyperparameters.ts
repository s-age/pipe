import { useState, useCallback } from 'react'

import { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { SessionData } from '@/lib/api/session/getSession'

type UseSessionHyperparametersProps = {
  sessionData: SessionData | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
}

export const useSessionHyperparameters = ({
  sessionData,
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
    sessionData?.hyperparameters?.temperature || 0.7,
  )
  const [topP, setTopP] = useState(sessionData?.hyperparameters?.top_p || 0.9)
  const [topK, setTopK] = useState(sessionData?.hyperparameters?.top_k || 5)

  const handleTemperatureMouseUp = useCallback((): void => {
    if (!currentSessionId || !sessionData) return
    onMetaSave(currentSessionId, {
      hyperparameters: {
        ...sessionData.hyperparameters,
        temperature: temperature,
      },
    })
  }, [currentSessionId, onMetaSave, temperature, sessionData])

  const handleTopPMouseUp = useCallback((): void => {
    if (!currentSessionId || !sessionData) return
    onMetaSave(currentSessionId, {
      hyperparameters: {
        ...sessionData.hyperparameters,
        top_p: topP,
      },
    })
  }, [currentSessionId, onMetaSave, topP, sessionData])

  const handleTopKMouseUp = useCallback((): void => {
    if (!currentSessionId || !sessionData) return
    onMetaSave(currentSessionId, {
      hyperparameters: {
        ...sessionData.hyperparameters,
        top_k: topK,
      },
    })
  }, [currentSessionId, onMetaSave, topK, sessionData])

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
