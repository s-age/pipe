import { array, boolean, coerce, number, object, string, type TypeOf } from 'zod'

import { optionalString } from '@/lib/validation'

const hyperparametersSchema = object({
  temperature: number().nullable(),
  topP: number().nullable(),
  topK: number().nullable()
}).nullable()

const referenceSchema = object({
  path: string(),
  ttl: coerce.number().int().nullable().optional().default(3),
  persist: boolean().optional().default(false),
  disabled: boolean().optional().default(false)
})

export const sessionMetaSchema = object({
  purpose: optionalString(),
  background: optionalString(),
  roles: array(string()).nullable().default(null),
  procedure: optionalString(),
  references: array(referenceSchema).default([]),
  artifacts: array(string()).nullable().default(null),
  hyperparameters: hyperparametersSchema.nullable().default(null),
  multiStepReasoning: boolean().default(false)
})

export type SessionMetaFormInputs = TypeOf<typeof sessionMetaSchema>
