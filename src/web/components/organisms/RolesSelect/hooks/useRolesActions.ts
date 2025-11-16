import { useCallback } from 'react'

import { getRoles, type RoleOption } from '@/lib/api/roles/getRoles'
import { emitToast } from '@/lib/toastEvents'

export type UseRolesActionsReturn = {
  fetchRoles: () => Promise<RoleOption[] | void>
}

export const useRolesActions = (): UseRolesActionsReturn => {
  const fetchRoles = useCallback(async (): Promise<RoleOption[] | void> => {
    try {
      const roles = await getRoles()

      return roles
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to fetch roles.')
    }
  }, [])

  return {
    fetchRoles
  }
}
