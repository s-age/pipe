import { useCallback } from 'react'

export const useFormHandlers = (): {
  handleFormSubmit: (event: React.FormEvent<HTMLFormElement>) => void
} => {
  const handleFormSubmit = useCallback(
    (event: React.FormEvent<HTMLFormElement>): void => {
      event.preventDefault()
    },
    []
  )

  return {
    handleFormSubmit
  }
}
