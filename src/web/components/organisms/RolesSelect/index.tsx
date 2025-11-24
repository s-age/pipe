import type { JSX } from 'react'

import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useRolesActions } from './hooks/useRolesActions'
import { useRolesHandlers } from './hooks/useRolesHandlers'
import { container } from './style.css'

type RolesSelectProperties = {
  placeholder?: string
  sessionDetail: SessionDetail | null
  onChange?: (roles: string[]) => void
}

export const RolesSelect = (properties: RolesSelectProperties): JSX.Element => {
  const { placeholder = 'Select roles', sessionDetail, onChange } = properties

  const actions = useRolesActions()
  const { roleOptions, handleFocus, handleRolesChange } = useRolesHandlers(
    sessionDetail,
    actions,
    onChange
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
