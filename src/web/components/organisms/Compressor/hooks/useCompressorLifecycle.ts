import { useMemo } from 'react'

import type { CompressorFormInputs } from '../schema'

type UseCompressorLifecycleProperties = {
  effectiveMax: number
  startLocal: number
}

type UseCompressorLifecycleReturn = {
  defaultValues: CompressorFormInputs
  mergedDefaultValues: Record<string, unknown>
  endOptions: number[]
}

export const useCompressorLifecycle = ({
  effectiveMax,
  startLocal
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

  // Ensure the form's defaultValues set `end_turn` to the current maximum when
  // no end_turn is provided by the handler. This initializes End to Max.
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

  const endOptions = useMemo(() => {
    const minEnd = startLocal + 1
    const maxEnd = effectiveMax

    return Array.from(
      { length: Math.max(0, maxEnd - minEnd + 1) },
      (_, i) => minEnd + i
    )
  }, [startLocal, effectiveMax])

  return {
    defaultValues,
    mergedDefaultValues,
    endOptions
  }
}
