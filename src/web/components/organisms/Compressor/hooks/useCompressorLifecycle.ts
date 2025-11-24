import { useMemo } from 'react'

import type { CompressorFormInputs } from '../schema'

type UseCompressorLifecycleProperties = {
  effectiveMax: number
}

type UseCompressorLifecycleReturn = {
  defaultValues: CompressorFormInputs
  mergedDefaultValues: Record<string, unknown>
}

export const useCompressorLifecycle = ({
  effectiveMax
}: UseCompressorLifecycleProperties): UseCompressorLifecycleReturn => {
  const defaultValues = useMemo<CompressorFormInputs>(
    () => ({
      policy:
        'Keep key findings and preserve meaning. Use concise, objective language.',
      targetLength: 1000,
      startTurn: 1,
      endTurn: effectiveMax
    }),
    [effectiveMax]
  )

  // Ensure the form's defaultValues set `endTurn` to the current maximum when
  // no endTurn is provided by the handler. This initializes End to Max.
  const mergedDefaultValues = useMemo(() => {
    try {
      const dv = { ...(defaultValues as Record<string, unknown>) }
      if ((dv.startTurn === undefined || dv.startTurn === null) && effectiveMax > 0) {
        ;(dv as Record<string, number>).startTurn = 1
      }
      if ((dv.endTurn === undefined || dv.endTurn === null) && effectiveMax > 0) {
        ;(dv as Record<string, number>).endTurn = effectiveMax
      }

      return dv as typeof defaultValues
    } catch {
      return defaultValues
    }
  }, [defaultValues, effectiveMax])

  return {
    defaultValues,
    mergedDefaultValues
  }
}
