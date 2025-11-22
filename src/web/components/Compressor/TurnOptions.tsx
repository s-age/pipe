import React from 'react'

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
