import { array, boolean, coerce, object, string, type TypeOf } from 'zod'

import { optionalNumber, optionalString, requiredString } from '@/lib/validation'

const referenceSchema = object({
  path: string(),
  ttl: coerce.number().int().nullable().optional().default(3),
  persist: boolean().optional().default(false),
  disabled: boolean().optional().default(false)
})

const turnSchema = object({
  type: string(),
  instruction: string().optional(),
  content: string().optional(),
  response: object({
    status: string().optional(),
    output: string().optional()
  }).optional(),
  timestamp: string().optional()
})

const todoSchema = object({
  id: string(),
  title: string(),
  description: string().optional(),
  status: string(),
  created_at: string().optional(),
  updated_at: string().optional()
})

export const formSchema = object({
  session_id: string(),
  purpose: requiredString('Purpose'),
  background: requiredString('Background'),
  roles: array(string()).default([]),
  parent: optionalString(),
  references: array(referenceSchema).default([]),
  artifacts: array(string()).default([]),
  procedure: optionalString(),
  instruction: requiredString('First Instruction'),
  multi_step_reasoning_enabled: boolean().default(false),
  hyperparameters: object({
    temperature: optionalNumber(0, 2).default(0.7),
    top_p: optionalNumber(0, 1).default(0.9),
    top_k: coerce.number().int().min(1).max(50).nullable().default(5)
  })
    .nullable()
    .default(null),
  todos: array(todoSchema).default([]),
  turns: array(turnSchema).default([]),
  roleOptions: array(
    object({
      value: string(),
      label: string()
    })
  ).optional()
})

export type StartSessionFormInputs = TypeOf<typeof formSchema>
