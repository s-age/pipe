import { array, boolean, coerce, object, string, type TypeOf } from 'zod'

import { optionalNumber, optionalString } from '@/lib/validation'

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
  hyperparameters: object({
    temperature: optionalNumber(0, 2).default(0.7),
    top_p: optionalNumber(0, 1).default(0.9),
    top_k: coerce.number().int().min(1).max(50).nullable().default(5)
  })
    .nullable()
    .default(null),
  multi_step_reasoning: boolean().default(false)
})

export type SessionMetaFormInputs = TypeOf<typeof sessionMetaSchema>
