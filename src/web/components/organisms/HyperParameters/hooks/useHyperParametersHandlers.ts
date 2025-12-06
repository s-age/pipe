import { useState, useCallback, useEffect, useRef } from 'react'

import type { EditHyperparametersRequest } from '@/lib/api/session/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersActions } from './useHyperParametersActions'

type UseSessionHyperparametersProperties = {
  sessionDetail: SessionDetail
}

export const useHyperParametersHandlers = ({
  sessionDetail
}: UseSessionHyperparametersProperties): {
  temperature: number
  setTemperature: React.Dispatch<React.SetStateAction<number>>
  handleTemperatureMouseUp: (event: React.MouseEvent<HTMLDivElement>) => void
  handleTemperatureMouseDown: () => void
  topP: number
  setTopP: React.Dispatch<React.SetStateAction<number>>
  handleTopPMouseUp: (event: React.MouseEvent<HTMLDivElement>) => void
  handleTopPMouseDown: () => void
  topK: number
  setTopK: React.Dispatch<React.SetStateAction<number>>
  handleTopKMouseUp: (event: React.MouseEvent<HTMLDivElement>) => void
  handleTopKMouseDown: () => void
} => {
  // Use a single object to hold hyperparameter UI state to avoid multiple
  // sequential setState calls inside an effect which the linter warns about.
  const [hpState, setHpState] = useState(() => ({
    temperature: sessionDetail.hyperparameters?.temperature ?? 0.7,
    topP: sessionDetail.hyperparameters?.topP ?? 0.9,
    topK: sessionDetail.hyperparameters?.topK ?? 5
  }))

  const { temperature, topP: topP, topK: topK } = hpState

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

  // Sync authoritative sessionDetail into local UI state before paint to
  // avoid visual flicker. We use useEffect and a single state update
  // so the linter's concern about cascading renders is mitigated.
  const isInteractingReference = useRef<boolean>(false)

  useEffect(() => {
    if (!sessionDetail) return
    // If the user is actively interacting with the slider, don't overwrite
    // their in-progress UI changes with the authoritative sessionDetail.
    if (isInteractingReference.current) return

    const incoming = {
      temperature: sessionDetail.hyperparameters?.temperature ?? hpState.temperature,
      topP: sessionDetail.hyperparameters?.topP ?? hpState.topP,
      topK: sessionDetail.hyperparameters?.topK ?? hpState.topK
    }

    // Only update if any value actually differs.
    if (
      incoming.temperature !== hpState.temperature ||
      incoming.topP !== hpState.topP ||
      incoming.topK !== hpState.topK
    ) {
      setHpState(incoming)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionDetail])

  const { updateHyperparameters } = useHyperParametersActions()

  const handleTemperatureMouseUp = useCallback(
    async (event: React.MouseEvent<HTMLDivElement>): Promise<void> => {
      if (!sessionDetail.sessionId) return
      const newTemperature = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { temperature: newTemperature }
      try {
        await updateHyperparameters(sessionDetail.sessionId, payload)
      } finally {
        isInteractingReference.current = false
      }
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
      try {
        await updateHyperparameters(sessionDetail.sessionId, payload)
      } finally {
        isInteractingReference.current = false
      }
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
      try {
        await updateHyperparameters(sessionDetail.sessionId, payload)
      } finally {
        isInteractingReference.current = false
      }
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
