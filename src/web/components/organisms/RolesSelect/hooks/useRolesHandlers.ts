import { useCallback, useMemo } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

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
    try {
      const roles = await actions.fetchRoles()
      setRoleOptions(roles)
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to fetch roles.')
    }
  }, [actions, setRoleOptions])

  return {
    roleOptions,
    handleFetchRoles
  }
}
