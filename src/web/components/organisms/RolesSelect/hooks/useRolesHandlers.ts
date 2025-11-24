import { useCallback, useState } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

import type { UseRolesActionsReturn } from './useRolesActions'

export const useRolesHandlers = (
  _sessionDetail: SessionDetail | null,
  actions: UseRolesActionsReturn,
  onChange?: (roles: string[]) => void
): {
  roleOptions: RoleOption[]
  handleFetchRoles: () => Promise<void>
  handleFocus: () => Promise<void>
  handleRolesChange: (values: string[]) => void
} => {
  const [roleOptions, setRoleOptions] = useState<RoleOption[]>([])

  const handleFetchRoles = useCallback(async (): Promise<void> => {
    const roles = await actions.fetchRoles()
    if (roles) {
      setRoleOptions(roles)
    }
  }, [actions])

  const handleFocus = useCallback(async () => {
    if (roleOptions.length === 0) {
      void handleFetchRoles()
    }
  }, [roleOptions.length, handleFetchRoles])

  const handleRolesChange = useCallback(
    (values: string[]): void => {
      onChange?.(values)
    },
    [onChange]
  )

  return {
    roleOptions,
    handleFetchRoles,
    handleFocus,
    handleRolesChange
  }
}
