import { useCallback, useState } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import { emitToast } from '@/lib/toastEvents'

import { useRolesActions } from './useRolesActions'

export const useRolesHandlers = (): {
  roleOptions: RoleOption[]
} => {
  const [roleOptions, setRoleOptions] = useState<RoleOption[]>([])
  const { fetchRoles } = useRolesActions()

  const loadRoles = useCallback(async () => {
    try {
      const roles = await fetchRoles()
      setRoleOptions(roles)
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to fetch roles.')
    }
  }, [fetchRoles])

  useEffect(() => {
    void loadRoles()
  }, [loadRoles])

  return {
    roleOptions
  }
}
