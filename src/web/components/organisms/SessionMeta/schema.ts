import { array, number, object, string, type TypeOf } from 'zod'

import { optionalString } from '@/lib/validation'

const hyperparametersSchema = object({
  temperature: number().nullable(),
  topP: number().nullable(),
  topK: number().nullable()
}).nullable()

export const sessionMetaSchema = object({
  purpose: optionalString(),
  background: optionalString(),
  roles: array(string()).nullable().default(null),
  procedure: optionalString(),
  artifacts: array(string()).nullable().default(null),
  hyperparameters: hyperparametersSchema.nullable().default(null)
})

export type SessionMetaFormInputs = TypeOf<typeof sessionMetaSchema>
