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
    top_p: sessionDetail.hyperparameters?.top_p ?? 0.9,
    top_k: sessionDetail.hyperparameters?.top_k ?? 5
  }))

  const { temperature, top_p: topP, top_k: topK } = hpState

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
      top_p: typeof value === 'function' ? value(previous.top_p) : value
    }))
  }

  const setTopK: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      top_k: typeof value === 'function' ? value(previous.top_k) : value
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
      top_p: sessionDetail.hyperparameters?.top_p ?? hpState.top_p,
      top_k: sessionDetail.hyperparameters?.top_k ?? hpState.top_k
    }

    // Only update if any value actually differs.
    if (
      incoming.temperature !== hpState.temperature ||
      incoming.top_p !== hpState.top_p ||
      incoming.top_k !== hpState.top_k
    ) {
      setHpState(incoming)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionDetail])

  const { updateHyperparameters } = useHyperParametersActions()

  const handleTemperatureMouseUp = useCallback(
    async (event: React.MouseEvent<HTMLDivElement>): Promise<void> => {
      if (!sessionDetail.session_id) return
      const newTemperature = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { temperature: newTemperature }
      try {
        await updateHyperparameters(sessionDetail.session_id, payload)
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
      if (!sessionDetail.session_id) return
      const newTopP = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { top_p: newTopP }
      try {
        await updateHyperparameters(sessionDetail.session_id, payload)
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
      if (!sessionDetail.session_id) return
      const newTopK = Number(event.currentTarget.dataset.value)
      const payload: EditHyperparametersRequest = { top_k: newTopK }
      try {
        await updateHyperparameters(sessionDetail.session_id, payload)
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
