import { useCallback } from 'react'

type UsePathTagProperties = {
  index: number
  onDelete: (index: number) => void
}

export const usePathTagHandlers = ({
  index,
  onDelete
}: UsePathTagProperties): {
  handleClick: () => void
  handleKeyDown: (event: React.KeyboardEvent<HTMLSpanElement>) => void
} => {
  const handleClick = useCallback((): void => {
    onDelete(index)
  }, [onDelete, index])

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLSpanElement>): void => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        onDelete(index)
      }
    },
    [onDelete, index]
  )

  return { handleClick, handleKeyDown }
}
