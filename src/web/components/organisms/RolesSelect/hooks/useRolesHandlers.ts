import { useMemo } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useRolesHandlers = (
  sessionDetail: SessionDetail | null
): {
  roleOptions: RoleOption[]
} => {
  const roleOptions = useMemo(
    () => sessionDetail?.roleOptions ?? [],
    [sessionDetail?.roleOptions]
  )

  return {
    roleOptions
  }
}
