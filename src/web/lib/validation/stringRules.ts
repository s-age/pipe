import { z } from 'zod'

/**
 * Common string validation rules
 *
 * These functions return Zod string schemas with common validation patterns.
 * Use them to maintain consistency across forms and reduce duplication.
 */

/**
 * Required string field with minimum length
 *
 * @param fieldName - Display name for error messages
 * @param minLength - Minimum length (default: 1)
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   purpose: requiredString('Purpose'),
 *   background: requiredString('Background', 10)
 * })
 * ```
 */
export const requiredString = (fieldName: string, minLength = 1): z.ZodString =>
  z.string().min(minLength, `${fieldName} is required`)

/**
 * Optional string field that transforms empty string to null
 *
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   procedure: optionalString(),
 *   notes: optionalString()
 * })
 * ```
 */
export const optionalString = (): z.ZodDefault<
  z.ZodNullable<z.ZodEffects<z.ZodString, string | null, string>>
> =>
  z
    .string()
    .transform((value) => (value === '' ? null : value))
    .nullable()
    .default(null)

/**
 * Comma-separated string list that transforms to array or null
 *
 * Splits by comma, trims whitespace, and filters empty strings.
 *
 * @returns Zod string schema that transforms to string[] | null
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   roles: commaSeparatedList(),
 *   artifacts: commaSeparatedList()
 * })
 * // Input: "role1, role2, role3"
 * // Output: ["role1", "role2", "role3"]
 * ```
 */
export const commaSeparatedList = (): z.ZodDefault<
  z.ZodNullable<z.ZodEffects<z.ZodString, string[] | null, string>>
> =>
  z
    .string()
    .transform((value) =>
      value
        ? value
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
        : null
    )
    .nullable()
    .default(null)

/**
 * Email validation
 *
 * @param fieldName - Display name for error messages (default: 'Email')
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   email: emailString(),
 *   contactEmail: emailString('Contact Email')
 * })
 * ```
 */
export const emailString = (fieldName = 'Email'): z.ZodString =>
  z.string().email(`Invalid ${fieldName.toLowerCase()} address`)

/**
 * URL validation
 *
 * @param fieldName - Display name for error messages (default: 'URL')
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   website: urlString(),
 *   repository: urlString('Repository URL')
 * })
 * ```
 */
export const urlString = (fieldName = 'URL'): z.ZodString =>
  z.string().url(`Invalid ${fieldName.toLowerCase()} format`)

/**
 * String with minimum and maximum length constraints
 *
 * @param fieldName - Display name for error messages
 * @param min - Minimum length
 * @param max - Maximum length
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   username: boundedString('Username', 3, 20),
 *   title: boundedString('Title', 1, 100)
 * })
 * ```
 */
export const boundedString = (
  fieldName: string,
  min: number,
  max: number
): z.ZodString =>
  z
    .string()
    .min(min, `${fieldName} must be at least ${min} characters`)
    .max(max, `${fieldName} must be at most ${max} characters`)

/**
 * Pattern-based string validation
 *
 * @param pattern - Regular expression pattern
 * @param message - Error message
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   slug: patternString(/^[a-z0-9-]+$/, 'Only lowercase letters, numbers, and hyphens allowed')
 * })
 * ```
 */
export const patternString = (pattern: RegExp, message: string): z.ZodString =>
  z.string().regex(pattern, message)
