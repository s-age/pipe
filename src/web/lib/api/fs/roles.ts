import { client } from '../client'

export type RoleOption = {
  label: string
  value: string
}

type RolesResponse = {
  roles: RoleOption[]
}

export const getRoles = async (): Promise<RoleOption[]> => {
  const response = await client.get<RolesResponse>('/fs/roles')

  return response.roles
}
