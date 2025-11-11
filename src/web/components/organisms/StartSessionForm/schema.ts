import { boolean, coerce, object, type TypeOf } from 'zod'

import {
  commaSeparatedList,
  optionalNumber,
  optionalString,
  requiredString
} from '@/lib/validation'

export const formSchema = object({
  purpose: requiredString('Purpose'),
  background: requiredString('Background'),
  roles: commaSeparatedList(),
  parent: optionalString(),
  references: commaSeparatedList().transform((paths) =>
    paths ? paths.map((path) => ({ path })) : null
  ),
  artifacts: commaSeparatedList(),
  procedure: optionalString(),
  instruction: requiredString('First Instruction'),
  multi_step_reasoning_enabled: boolean().default(false),
  hyperparameters: object({
    temperature: optionalNumber(0, 2).default(0.7),
    top_p: optionalNumber(0, 1).default(0.9),
    top_k: coerce.number().int().min(1).max(50).nullable().default(5)
  })
    .nullable()
    .default(null)
})

export type StartSessionFormInputs = TypeOf<typeof formSchema>
