import { object, string, coerce, boolean, type TypeOf } from 'zod'

export const formSchema = object({
  purpose: string().min(1, 'Purpose is required'),
  background: string().min(1, 'Background is required'),
  roles: string()
    .transform((value) =>
      value
        ? value
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
        : null,
    )
    .nullable()
    .default(null),
  parent: string()
    .transform((value) => (value === '' ? null : value))
    .nullable()
    .default(null),
  references: string()
    .transform((value) =>
      value
        ? value
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
            .map((path) => ({ path }))
        : null,
    )
    .nullable()
    .default(null),
  artifacts: string()
    .transform((value) =>
      value
        ? value
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
        : null,
    )
    .nullable()
    .default(null),
  procedure: string()
    .transform((value) => (value === '' ? null : value))
    .nullable()
    .default(null),
  instruction: string().min(1, 'First Instruction is required'),
  multi_step_reasoning_enabled: boolean().default(false),
  hyperparameters: object({
    temperature: coerce.number().min(0).max(2).nullable().default(0.7),
    top_p: coerce.number().min(0).max(1).nullable().default(0.9),
    top_k: coerce.number().min(1).max(50).nullable().default(5),
  })
    .nullable()
    .default(null),
})

export type StartSessionFormInputs = TypeOf<typeof formSchema>
