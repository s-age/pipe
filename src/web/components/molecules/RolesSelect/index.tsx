import type { SelectHTMLAttributes, JSX } from 'react'
import type { UseFormRegister } from 'react-hook-form'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { MultipleSelect } from '../MultipleSelect'

type RolesSelectProperties = {
  register?: UseFormRegister<Record<string, unknown>>
  name?: string
  placeholder?: string
  sessionDetail?: SessionDetail | null
  roleOptions: RoleOption[]
} & SelectHTMLAttributes<HTMLSelectElement>

export const RolesSelect = (properties: RolesSelectProperties): JSX.Element => {
  const {
    register,
    name = 'roles',
    placeholder = 'Select roles',
    sessionDetail,
    roleOptions,
    className,
    ...rest
  } = properties

  return (
    <MultipleSelect
      register={register}
      name={name}
      options={roleOptions}
      searchable={true}
      placeholder={placeholder}
      defaultValue={sessionDetail?.roles}
      className={className}
      {...rest}
    />
  )
}

// (Removed temporary default export) Use named export `RolesSelect`.
