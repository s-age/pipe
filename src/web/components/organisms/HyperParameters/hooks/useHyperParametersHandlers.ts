import { useState, useCallback, useRef } from 'react'

import type { EditHyperparametersRequest } from '@/lib/api/meta/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersActions } from './useHyperParametersActions'
import { useHyperParametersLifecycle } from './useHyperParametersLifecycle'

type UseSessionHyperparametersProperties = {
  sessionDetail: SessionDetail
}

export const useHyperParametersHandlers = ({
  sessionDetail
}: UseSessionHyperparametersProperties): {
  setTemperature: React.Dispatch<React.SetStateAction<number>>
  setTopK: React.Dispatch<React.SetStateAction<number>>
  setTopP: React.Dispatch<React.SetStateAction<number>>
  temperature: number
  topK: number
  topP: number
  handleTemperatureMouseDown: () => void
  handleTemperatureMouseUp: (event: React.MouseEvent<HTMLDivElement>) => void
  handleTopKMouseDown: () => void
  handleTopKMouseUp: (event: React.MouseEvent<HTMLDivElement>) => void
  handleTopPMouseDown: () => void
  handleTopPMouseUp: (event: React.MouseEvent<HTMLDivElement>) => void
} => {
  // Use a single object to hold hyperparameter UI state to avoid multiple
  // sequential setState calls inside an effect which the linter warns about.
  const [hpState, setHpState] = useState(() => ({
    temperature: sessionDetail.hyperparameters?.temperature ?? 0.7,
    topP: sessionDetail.hyperparameters?.topP ?? 0.9,
    topK: sessionDetail.hyperparameters?.topK ?? 5
  }))

  const { temperature, topK: topK, topP: topP } = hpState

  // Provide individual setter functions compatible with existing callers.
  const setTemperature: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      temperature: typeof value === 'function' ? value(previous.temperature) : value
    }))
  }

  const setTopP: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      topP: typeof value === 'function' ? value(previous.topP) : value
    }))
  }

  const setTopK: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      topK: typeof value === 'function' ? value(previous.topK) : value
    }))
  }

  const isInteractingReference = useRef<boolean>(false)

  // Lifecycle: sync sessionDetail props to local state
  useHyperParametersLifecycle({
    sessionDetail,
    hpState,
    setHpState,
    isInteractingReference
  })

  const { updateHyperparameters } = useHyperParametersActions()

  const handleTemperatureMouseUp = useCallback(
    async (event: React.MouseEvent<HTMLDivElement>): Promise<void> => {
      if (!sessionDetail.sessionId) return
      const newTemperature = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { temperature: newTemperature }
      await updateHyperparameters(sessionDetail.sessionId, payload)
      isInteractingReference.current = false
    },
    [sessionDetail, updateHyperparameters]
  )

  const handleTemperatureMouseDown = useCallback((): void => {
    isInteractingReference.current = true
  }, [])

  const handleTopPMouseUp = useCallback(
    async (event: React.MouseEvent<HTMLDivElement>): Promise<void> => {
      if (!sessionDetail.sessionId) return
      const newTopP = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { topP: newTopP }
      await updateHyperparameters(sessionDetail.sessionId, payload)
      isInteractingReference.current = false
    },
    [sessionDetail, updateHyperparameters]
  )

  const handleTopPMouseDown = useCallback((): void => {
    isInteractingReference.current = true
  }, [])

  const handleTopKMouseUp = useCallback(
    async (event: React.MouseEvent<HTMLDivElement>): Promise<void> => {
      if (!sessionDetail.sessionId) return
      const newTopK = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { topK: newTopK }
      await updateHyperparameters(sessionDetail.sessionId, payload)
      isInteractingReference.current = false
    },
    [sessionDetail, updateHyperparameters]
  )

  const handleTopKMouseDown = useCallback((): void => {
    isInteractingReference.current = true
  }, [])

  return {
    temperature,
    setTemperature,
    handleTemperatureMouseUp,
    handleTemperatureMouseDown,
    topP,
    setTopP,
    handleTopPMouseUp,
    handleTopPMouseDown,
    topK,
    setTopK,
    handleTopKMouseUp,
    handleTopKMouseDown
  }
}
