import { useCallback } from 'react'

export const useSessionItemHandlers = (
  sessionId: string,
  isSelected: boolean,
  onSelect: (sessionId: string, isSelected: boolean) => void
): { handleSelect: () => void } => {
  const handleSelect = useCallback((): void => {
    onSelect(sessionId, !isSelected)
  }, [sessionId, isSelected, onSelect])

  return {
    handleSelect
  }
}
