import { z } from 'zod'

export const instructionSchema = z.object({
  instruction: z.string().min(1, 'Instruction is required')
})

export type InstructionFormData = z.infer<typeof instructionSchema>
