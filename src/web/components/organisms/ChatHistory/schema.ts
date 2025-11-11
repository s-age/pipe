import { z } from 'zod'

import { requiredString } from '@/lib/validation'

export const instructionSchema = z.object({
  instruction: requiredString('Instruction')
})

export type InstructionFormData = z.infer<typeof instructionSchema>
