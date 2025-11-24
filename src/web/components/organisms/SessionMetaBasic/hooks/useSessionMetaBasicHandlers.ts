import { useCallback } from 'react'

type UseSessionMetaBasicHandlersProperties = {
  setValue?: (name: string, value: unknown) => void
}

export const useSessionMetaBasicHandlers = ({
  setValue
}: UseSessionMetaBasicHandlersProperties): {
  handleRolesChange: (roles: string[]) => void
} => {
  const handleRolesChange = useCallback(
    (roles: string[]) => {
      setValue?.('roles', roles)
    },
    [setValue]
  )

  return {
    handleRolesChange
  }
}
