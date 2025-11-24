#!/usr/bin/env node
/* eslint-env node */
// Simple hooks rule checker
// Usage: node scripts/check-hooks.js
//
// Checks:
// - Files under roles/typescript/**/hooks (glob) should export hooks with names matching `namingRegex` from `.rules.json`.
// - Files in hooks/ should have filenames starting with `use` unless they match allowedContextSuffixes.
// - Handler files (contains "Handlers" in name) should not reference toast or useToast.
//
// This is intentionally small and zero-dependency to keep it runnable in CI without extra installs.
import fs from 'fs'
import path from 'path'

const repoRoot = process.cwd()
const rulesPath = path.join(repoRoot, 'roles', 'typescript', 'hooks', '.rules.json')

if (!fs.existsSync(rulesPath)) {
  console.error('Rules file not found:', rulesPath)
  process.exit(2)
}

const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'))
const namingRegex = new RegExp(rules.namingRegex)
const allowedContextSuffixes = rules.allowedContextSuffixes || []
const forbiddenInHandlers = rules.forbiddenInHandlers || []

const hooksRoot = path.join(repoRoot, 'roles', 'typescript')

function walk(dir) {
  const res = []
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name)
    const st = fs.statSync(p)
    if (st.isDirectory()) res.push(...walk(p))
    else res.push(p)
  }

  return res
}

const files = walk(hooksRoot).filter((f) => f.endsWith('.ts') || f.endsWith('.tsx'))

const violations = []

for (const file of files) {
  const rel = path.relative(repoRoot, file)
  const contents = fs.readFileSync(file, 'utf8')
  const basename = path.basename(file)

  // Only enforce strong naming if file is in a hooks/ directory
  if (file.split(path.sep).includes('hooks')) {
    const isAllowedContext = allowedContextSuffixes.some((s) => basename.endsWith(s))
    if (!isAllowedContext) {
      if (!basename.startsWith('use')) {
        violations.push(
          `${rel}: hook filename should start with 'use' or match allowed context suffixes`
        )
      }

      // Find exported hook names
      const exportMatches = Array.from(
        contents.matchAll(/export\s+(?:const|function)\s+(use[A-Za-z0-9_]+)/g)
      )
      if (exportMatches.length === 0) {
        violations.push(`${rel}: no exported hook named with 'use...' found`)
      } else {
        for (const m of exportMatches) {
          const name = m[1]
          if (!namingRegex.test(name)) {
            violations.push(
              `${rel}: exported hook name '${name}' does not match naming regex ${rules.namingRegex}`
            )
          }
        }
      }

      // Handler-specific checks
      if (basename.includes('Handlers')) {
        for (const token of forbiddenInHandlers) {
          if (contents.includes(token)) {
            violations.push(
              `${rel}: contains forbidden token '${token}' in a Handlers file`
            )
            break
          }
        }
      }
    }
  }
}

if (violations.length > 0) {
  console.error('\nHooks rules violations found:')
  for (const v of violations) console.error(' -', v)
  process.exit(1)
}

console.log('Hooks rules: OK')
process.exit(0)
