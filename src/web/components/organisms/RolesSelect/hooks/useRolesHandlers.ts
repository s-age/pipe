import { useCallback, useMemo } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

import type { UseRolesActionsReturn } from './useRolesActions'

export const useRolesHandlers = (
  sessionDetail: SessionDetail | null,
  actions: UseRolesActionsReturn,
  setRoleOptions: React.Dispatch<React.SetStateAction<RoleOption[]>>
): {
  roleOptions: RoleOption[]
  handleFetchRoles: () => Promise<void>
} => {
  const roleOptions = useMemo(
    () => sessionDetail?.roleOptions ?? [],
    [sessionDetail?.roleOptions]
  )

  const handleFetchRoles = useCallback(async (): Promise<void> => {
    const roles = await actions.fetchRoles()
    if (roles) {
      setRoleOptions(roles)
    }
  }, [actions, setRoleOptions])

  return {
    roleOptions,
    handleFetchRoles
  }
}
