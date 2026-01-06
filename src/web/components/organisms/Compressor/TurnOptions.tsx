import React from 'react'

import type { SelectOption } from '@/components/molecules/Select/hooks/useSelect'

export const renderTurnOptions = (
  limit: number,
  disableAbove?: number | ''
): React.ReactNode => {
  if (limit <= 0) return null

  return Array.from({ length: limit }, (_ignored, index) => index + 1).map((turn) => (
    <option
      key={turn}
      value={String(turn)}
      disabled={
        disableAbove !== '' && disableAbove !== undefined && turn > Number(disableAbove)
      }
    >
      {turn}
    </option>
  ))
}

export const getTurnOptions = (
  limit: number,
  disableFrom?: number | ''
): SelectOption[] => {
  if (limit <= 0) return []

  return Array.from({ length: limit }, (_ignored, index) => index + 1).map((turn) => ({
    value: String(turn),
    label: String(turn),
    disabled:
      disableFrom !== '' && disableFrom !== undefined && turn >= Number(disableFrom)
  }))
}

export const getTurnOptionsDisableBelow = (
  limit: number,
  disableBelow?: number | ''
): SelectOption[] => {
  if (limit <= 0) return []

  return Array.from({ length: limit }, (_ignored, index) => index + 1).map((turn) => ({
    value: String(turn),
    label: String(turn),
    disabled:
      disableBelow !== '' && disableBelow !== undefined && turn <= Number(disableBelow)
  }))
}
