import { useCallback } from 'react'

import { getRoles, type RoleOption } from '@/lib/api/roles/getRoles'

export type UseRolesActionsReturn = {
  fetchRoles: () => Promise<RoleOption[]>
}

export const useRolesActions = (): UseRolesActionsReturn => {
  const fetchRoles = useCallback(async (): Promise<RoleOption[]> => getRoles(), [])

  return {
    fetchRoles
  }
}
