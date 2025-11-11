/**
 * Validation Rules
 *
 * Common Zod validation schemas for use across the application.
 * These rules promote consistency and reduce duplication in form validation.
 *
 * @module validation
 */

export * from './stringRules'
export * from './numberRules'
export * from './enumRules'

/**
 * Usage Guidelines:
 *
 * 1. Import specific rules you need:
 *    ```ts
 *    import { requiredString, optionalNumber } from '@/lib/validation'
 *    ```
 *
 * 2. Use in schema.ts files:
 *    ```ts
 *    import { z } from 'zod'
 *    import { requiredString, commaSeparatedList } from '@/lib/validation'
 *
 *    export const formSchema = z.object({
 *      purpose: requiredString('Purpose'),
 *      roles: commaSeparatedList()
 *    })
 *    ```
 *
 * 3. Only define schemas in schema.ts files (enforced by ESLint)
 *
 * 4. For custom validation, extend these rules:
 *    ```ts
 *    import { requiredString } from '@/lib/validation'
 *
 *    export const formSchema = z.object({
 *      email: requiredString('Email').email('Invalid email format')
 *    })
 *    ```
 */
