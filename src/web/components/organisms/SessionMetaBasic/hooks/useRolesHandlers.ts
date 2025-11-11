import { useEffect, useState } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'

import { useRolesActions } from './useRolesActions'

export const useRolesHandlers = (): {
  roleOptions: RoleOption[]
} => {
  const [roleOptions, setRoleOptions] = useState<RoleOption[]>([])
  const { fetchRoles } = useRolesActions()

  useEffect(() => {
    fetchRoles()
      .then(setRoleOptions)
      .catch((error) => console.error('Failed to fetch roles:', error))
  }, [fetchRoles])

  return {
    roleOptions
  }
}
