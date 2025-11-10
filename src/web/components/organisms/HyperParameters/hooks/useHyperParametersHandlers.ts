import { useState, useCallback, useLayoutEffect } from 'react'

import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersActions } from './useHyperParametersActions'

type UseSessionHyperparametersProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave?: (sessionId: string, meta: EditSessionMetaRequest) => void | Promise<void>
}

export const useHyperParametersHandlers = ({
  sessionDetail,
  currentSessionId,
  onMetaSave
}: UseSessionHyperparametersProperties): {
  temperature: number
  setTemperature: React.Dispatch<React.SetStateAction<number>>
  handleTemperatureMouseUp: () => Promise<void>
  handleTemperatureMouseDown: () => void
  topP: number
  setTopP: React.Dispatch<React.SetStateAction<number>>
  handleTopPMouseUp: () => Promise<void>
  handleTopPMouseDown: () => void
  topK: number
  setTopK: React.Dispatch<React.SetStateAction<number>>
  handleTopKMouseUp: () => Promise<void>
  handleTopKMouseDown: () => void
} => {
  // Use a single object to hold hyperparameter UI state to avoid multiple
  // sequential setState calls inside an effect which the linter warns about.
  const [hpState, setHpState] = useState(() => ({
    temperature: sessionDetail?.hyperparameters?.temperature ?? 0.7,
    top_p: sessionDetail?.hyperparameters?.top_p ?? 0.9,
    top_k: sessionDetail?.hyperparameters?.top_k ?? 5
  }))

  const { temperature, top_p: topP, top_k: topK } = hpState

  // Provide individual setter functions compatible with existing callers.
  const setTemperature: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      temperature:
        typeof value === 'function'
          ? (value as (p: number) => number)(previous.temperature)
          : value
    }))
  }

  const setTopP: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      top_p:
        typeof value === 'function'
          ? (value as (p: number) => number)(previous.top_p)
          : value
    }))
  }

  const setTopK: React.Dispatch<React.SetStateAction<number>> = (value) => {
    setHpState((previous) => ({
      ...previous,
      top_k:
        typeof value === 'function'
          ? (value as (p: number) => number)(previous.top_k)
          : value
    }))
  }

  // Sync authoritative sessionDetail into local UI state before paint to
  // avoid visual flicker. We use useLayoutEffect and a single state update
  // so the linter's concern about cascading renders is mitigated.
  const [isInteracting, setIsInteracting] = useState<boolean>(false)

  useLayoutEffect(() => {
    if (!sessionDetail) return
    // If the user is actively interacting with the slider, don't overwrite
    // their in-progress UI changes with the authoritative sessionDetail.
    if (isInteracting) return

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
  }, [sessionDetail, isInteracting])

  const { updateHyperparameters } = useHyperParametersActions()

  const handleTemperatureMouseUp = useCallback(async (): Promise<void> => {
    if (!currentSessionId || !sessionDetail) return

    const payload = { temperature }

    try {
      const result = await updateHyperparameters(currentSessionId, payload)

      if (onMetaSave)
        await onMetaSave(currentSessionId, {
          hyperparameters: result.session.hyperparameters
        })
    } finally {
      // end interaction on commit (whether success or failure)
      setIsInteracting(false)
    }
  }, [currentSessionId, onMetaSave, temperature, sessionDetail, updateHyperparameters])

  const handleTemperatureMouseDown = useCallback((): void => {
    setIsInteracting(true)
  }, [])

  const handleTopPMouseUp = useCallback(async (): Promise<void> => {
    if (!currentSessionId || !sessionDetail) return

    const payload = { top_p: topP }

    try {
      const result = await updateHyperparameters(currentSessionId, payload)

      if (onMetaSave)
        await onMetaSave(currentSessionId, {
          hyperparameters: result.session.hyperparameters
        })
    } finally {
      setIsInteracting(false)
    }
  }, [currentSessionId, onMetaSave, topP, sessionDetail, updateHyperparameters])

  const handleTopPMouseDown = useCallback((): void => {
    setIsInteracting(true)
  }, [])

  const handleTopKMouseUp = useCallback(async (): Promise<void> => {
    if (!currentSessionId || !sessionDetail) return

    const payload = { top_k: topK }

    try {
      const result = await updateHyperparameters(currentSessionId, payload)

      if (onMetaSave)
        await onMetaSave(currentSessionId, {
          hyperparameters: result.session.hyperparameters
        })
    } finally {
      setIsInteracting(false)
    }
  }, [currentSessionId, onMetaSave, topK, sessionDetail, updateHyperparameters])

  const handleTopKMouseDown = useCallback((): void => {
    setIsInteracting(true)
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
