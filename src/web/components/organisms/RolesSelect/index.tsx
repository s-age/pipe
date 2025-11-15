import { useCallback, useState } from 'react'
import type { JSX } from 'react'

import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useRolesActions } from './hooks/useRolesActions'
import { container } from './style.css'

type RolesSelectProperties = {
  placeholder?: string
  sessionDetail: SessionDetail | null
  onChange?: (roles: string[]) => void
}

export const RolesSelect = (properties: RolesSelectProperties): JSX.Element => {
  const { placeholder = 'Select roles', sessionDetail, onChange } = properties

  const [roleOptions, setRoleOptions] = useState<RoleOption[]>([])
  const { fetchRoles } = useRolesActions()

  const handleFocus = useCallback(async () => {
    if (roleOptions.length === 0) {
      try {
        const roles = await fetchRoles()
        setRoleOptions(roles)
      } catch (error) {
        console.error('Failed to fetch roles:', error)
      }
    }
  }, [roleOptions.length, fetchRoles])

  const handleRolesChange = useCallback(
    (values: string[]): void => {
      onChange?.(values)
    },
    [onChange]
  )

  const list = roleOptions.map((role) => ({
    label: role.label,
    value: role.value
  }))

  const existsValue = sessionDetail?.roles ?? []

  return (
    <div className={container}>
      <FileSearchExplorer
        existsValue={existsValue}
        list={list}
        isMultiple={true}
        placeholder={placeholder}
        onChange={handleRolesChange}
        onFocus={handleFocus}
      />
    </div>
  )
}
