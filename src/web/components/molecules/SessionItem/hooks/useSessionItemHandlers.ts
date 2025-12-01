export const useSessionItemHandlers = (
  sessionId: string,
  isSelected: boolean,
  onSelect: (sessionId: string, isSelected: boolean) => void
): { handleSelect: () => void } => {
  const handleSelect = (): void => {
    onSelect(sessionId, !isSelected)
  }

  return {
    handleSelect
  }
}
