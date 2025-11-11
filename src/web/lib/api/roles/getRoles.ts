import { client } from '../client'

export type RoleOption = {
  label: string
  value: string
}

export const getRoles = async (): Promise<RoleOption[]> =>
  client.get<RoleOption[]>('/roles')
