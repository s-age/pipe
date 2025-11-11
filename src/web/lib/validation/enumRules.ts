import fs from 'fs'
import path from 'path'

import { z } from 'zod'

/**
 * Enum validation rules
 *
 * These functions create Zod schemas that validate against predefined sets of values,
 * including dynamically loaded options from the file system.
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

/**
 * Validate file paths against existing files in a directory
 *
 * Dynamically loads .md files from a directory and validates that the input
 * matches one of the available files.
 *
 * @param directoryPath - Absolute or relative path to directory
 * @param fieldName - Display name for error messages
 * @param extension - File extension to match (default: '.md')
 * @returns Zod string schema with refinement
 *
 * @example
 * ```ts
 * // Validate against roles/*.md files
 * const schema = z.object({
 *   role: filePathEnum('roles', 'Role', '.md')
 * })
 * // Valid: "roles/engineer.md"
 * // Invalid: "roles/nonexistent.md"
 * ```
 */
export const filePathEnum = (
  directoryPath: string,
  fieldName: string,
  extension = '.md'
): z.ZodEffects<z.ZodString, string, string> => {
  // Resolve relative paths
  const resolvedPath = path.isAbsolute(directoryPath)
    ? directoryPath
    : path.resolve(process.cwd(), directoryPath)

  return z.string().superRefine((value, context) => {
    // Check if file exists
    const fullPath = path.isAbsolute(value) ? value : path.resolve(process.cwd(), value)

    if (!fs.existsSync(fullPath)) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: `${fieldName} file does not exist: ${value}`
      })

      return
    }

    // Check if file is in the allowed directory
    const relativePath = path.relative(resolvedPath, fullPath)
    if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: `${fieldName} must be within ${directoryPath} directory`
      })

      return
    }

    // Check file extension
    if (path.extname(fullPath) !== extension) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: `${fieldName} must be a ${extension} file`
      })
    }
  })
}

/**
 * Validate comma-separated file paths against existing files
 *
 * Combines commaSeparatedList with filePathEnum validation.
 *
 * @param directoryPath - Absolute or relative path to directory
 * @param fieldName - Display name for error messages
 * @param extension - File extension to match (default: '.md')
 * @returns Zod string schema
 *
 * @example
 * ```ts
 * const schema = z.object({
 *   roles: commaSeparatedFilePathEnum('roles', 'Roles')
 * })
 * // Input: "roles/engineer.md, roles/reviewer.md"
 * // Valid if both files exist
 * ```
 */
export const commaSeparatedFilePathEnum = (
  directoryPath: string,
  fieldName: string,
  extension = '.md'
): z.ZodEffects<
  z.ZodDefault<z.ZodNullable<z.ZodEffects<z.ZodString, string[] | null, string>>>,
  string[] | null
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
    .superRefine((paths, context) => {
      if (!paths) return

      const resolvedPath = path.isAbsolute(directoryPath)
        ? directoryPath
        : path.resolve(process.cwd(), directoryPath)

      paths.forEach((filePath, index) => {
        const fullPath = path.isAbsolute(filePath)
          ? filePath
          : path.resolve(process.cwd(), filePath)

        if (!fs.existsSync(fullPath)) {
          context.addIssue({
            code: z.ZodIssueCode.custom,
            message: `${fieldName}[${index}]: File does not exist: ${filePath}`,
            path: [index]
          })

          return
        }

        const relativePath = path.relative(resolvedPath, fullPath)
        if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
          context.addIssue({
            code: z.ZodIssueCode.custom,
            message: `${fieldName}[${index}]: Must be within ${directoryPath} directory`,
            path: [index]
          })

          return
        }

        if (path.extname(fullPath) !== extension) {
          context.addIssue({
            code: z.ZodIssueCode.custom,
            message: `${fieldName}[${index}]: Must be a ${extension} file`,
            path: [index]
          })
        }
      })
    })

/**
 * Get available file paths from a directory (for UI autocomplete)
 *
 * Helper function to retrieve list of files for dropdown/autocomplete components.
 *
 * @param directoryPath - Absolute or relative path to directory
 * @param extension - File extension to match (default: '.md')
 * @param includeSubdirectories - Whether to search recursively (default: false)
 * @returns Array of relative file paths
 *
 * @example
 * ```ts
 * const roleOptions = getFilePathOptions('roles', '.md')
 * // Returns: ['roles/engineer.md', 'roles/reviewer.md', ...]
 * ```
 */
export const getFilePathOptions = (
  directoryPath: string,
  extension = '.md',
  includeSubdirectories = false
): string[] => {
  const resolvedPath = path.isAbsolute(directoryPath)
    ? directoryPath
    : path.resolve(process.cwd(), directoryPath)

  if (!fs.existsSync(resolvedPath)) {
    return []
  }

  const files: string[] = []

  const scanDirectory = (directory: string): void => {
    const entries = fs.readdirSync(directory, { withFileTypes: true })

    for (const entry of entries) {
      const fullPath = path.join(directory, entry.name)

      if (entry.isDirectory() && includeSubdirectories) {
        scanDirectory(fullPath)
      } else if (entry.isFile() && path.extname(entry.name) === extension) {
        const relativePath = path.relative(process.cwd(), fullPath)
        files.push(relativePath)
      }
    }
  }

  scanDirectory(resolvedPath)

  return files.sort()
}
