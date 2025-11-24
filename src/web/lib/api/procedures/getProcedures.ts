import { client } from '../client'

export type ProcedureOption = {
  label: string
  value: string
}

export const getProcedures = async (): Promise<ProcedureOption[]> =>
  client.get<ProcedureOption[]>('/procedures')
