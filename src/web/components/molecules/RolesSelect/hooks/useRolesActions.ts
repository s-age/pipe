import { useCallback } from 'react'

import { getRoles, type RoleOption } from '@/lib/api/roles/getRoles'

export const useRolesActions = (): {
  fetchRoles: () => Promise<RoleOption[]>
} => {
  const fetchRoles = useCallback(async (): Promise<RoleOption[]> => getRoles(), [])

  return {
    fetchRoles
  }
}
