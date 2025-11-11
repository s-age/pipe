import { z } from 'zod'

/**
 * Common number validation rules
 *
 * These functions return Zod number schemas with common validation patterns.
 */

/**
 * Number within a range
 *
 * @param fieldName - Display name for error messages
 * @param min - Minimum value
 * @param max - Maximum value
 * @returns Zod number schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   temperature: rangedNumber('Temperature', 0, 2),
 *   top_p: rangedNumber('Top P', 0, 1)
 * })
 * ```
 */
export const rangedNumber = (
  fieldName: string,
  min: number,
  max: number
): z.ZodNumber =>
  z.coerce
    .number()
    .min(min, `${fieldName} must be at least ${min}`)
    .max(max, `${fieldName} must be at most ${max}`)

/**
 * Optional number that can be null
 *
 * @param min - Minimum value (optional)
 * @param max - Maximum value (optional)
 * @returns Zod number schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   temperature: optionalNumber(0, 2).default(0.7),
 *   top_k: optionalNumber(1, 50).default(5)
 * })
 * ```
 */
export const optionalNumber = (
  min?: number,
  max?: number
): z.ZodNullable<z.ZodNumber> => {
  let schema = z.coerce.number()

  if (min !== undefined) {
    schema = schema.min(min) as z.ZodNumber
  }
  if (max !== undefined) {
    schema = schema.max(max) as z.ZodNumber
  }

  return schema.nullable()
}

/**
 * Positive integer validation
 *
 * @param fieldName - Display name for error messages (default: 'Value')
 * @returns Zod number schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   count: positiveInteger('Count'),
 *   quantity: positiveInteger()
 * })
 * ```
 */
export const positiveInteger = (fieldName = 'Value'): z.ZodNumber =>
  z.coerce
    .number()
    .int(`${fieldName} must be an integer`)
    .positive(`${fieldName} must be positive`)

/**
 * Non-negative integer (includes 0)
 *
 * @param fieldName - Display name for error messages (default: 'Value')
 * @returns Zod number schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   index: nonNegativeInteger('Index'),
 *   offset: nonNegativeInteger()
 * })
 * ```
 */
export const nonNegativeInteger = (fieldName = 'Value'): z.ZodNumber =>
  z.coerce
    .number()
    .int(`${fieldName} must be an integer`)
    .min(0, `${fieldName} must be non-negative`)

/**
 * Percentage (0-100)
 *
 * @param fieldName - Display name for error messages (default: 'Percentage')
 * @returns Zod number schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   progress: percentage(),
 *   completion: percentage('Completion Rate')
 * })
 * ```
 */
export const percentage = (fieldName = 'Percentage'): z.ZodNumber =>
  z.coerce
    .number()
    .min(0, `${fieldName} must be at least 0%`)
    .max(100, `${fieldName} must be at most 100%`)
