import { client } from '../client'

export type ProcedureOption = {
  label: string
  value: string
}

type ProceduresResponse = {
  procedures: ProcedureOption[]
}

export const getProcedures = async (): Promise<ProcedureOption[]> => {
  const response = await client.get<ProceduresResponse>('/fs/procedures')
  return response.procedures
}
