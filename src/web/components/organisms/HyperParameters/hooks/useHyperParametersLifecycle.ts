import { useEffect } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

export type HyperParameterState = {
  temperature: number
  topP: number
  topK: number
}

export type UseHyperParametersLifecycleProperties = {
  sessionDetail: SessionDetail
  hpState: HyperParameterState
  setHpState: React.Dispatch<React.SetStateAction<HyperParameterState>>
  isInteractingReference: React.MutableRefObject<boolean>
}

/**
 * useHyperParametersLifecycle
 *
 * Manages HyperParameters lifecycle effects (sync from props).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useHyperParametersLifecycle = ({
  sessionDetail,
  hpState,
  setHpState,
  isInteractingReference
}: UseHyperParametersLifecycleProperties): void => {
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
}
