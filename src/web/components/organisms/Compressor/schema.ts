import { z } from 'zod'

export const compressorSchema = z.object({
  policy: z.string().min(1, 'Policy is required'),
  targetLength: z.number().min(1, 'Target length must be at least 1').optional(),
  startTurn: z.number().min(1).optional(),
  endTurn: z.number().min(1).optional()
})

export type CompressorFormInputs = z.infer<typeof compressorSchema>
