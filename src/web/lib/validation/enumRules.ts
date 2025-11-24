import { z } from 'zod'

/**
 * Enum validation rules
 *
 * These functions create Zod schemas that validate against predefined sets of values.
 */

/**
 * Validate against a list of allowed values
 *
 * @param allowedValues - Array of allowed string values
 * @param fieldName - Display name for error messages
 * @returns Zod enum schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   status: enumFromList(['draft', 'published', 'archived'], 'Status'),
 *   priority: enumFromList(['low', 'medium', 'high'], 'Priority')
 * })
 * ```
 */
export const enumFromList = <T extends string>(
  allowedValues: readonly T[],
  fieldName: string
): z.ZodEnum<[T, ...T[]]> | z.ZodLiteral<T> => {
  if (allowedValues.length === 0) {
    throw new Error(`enumFromList: allowedValues cannot be empty for ${fieldName}`)
  }

  // Zod requires at least 2 values for z.enum, handle single value case
  if (allowedValues.length === 1) {
    return z.literal(allowedValues[0])
  }

  return z.enum([allowedValues[0], ...allowedValues.slice(1)] as [T, ...T[]], {
    errorMap: () => ({
      message: `${fieldName} must be one of: ${allowedValues.join(', ')}`
    })
  })
}
