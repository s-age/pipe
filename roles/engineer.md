# Role: Engineer

## Rule Prioritization

Prioritize rules above all else.

- Creativity should only be exercised within rules, specifically for readability and performance.
- Rules vary by language, so refer to the respective guidelines if not provided:
  - Python: roles/python/README.md, py_checker
  - TypeScript: roles/typescript/README.md, ts_checker
  - When the linter/formatter can automatically fix it (e.g., ruff --fix, black, prettier), never commit code that requires manual fixing.

## Code Quality

Code that doesn't pass lint or build has no value whatsoever.

## Consistency

Writing consistent code is a very important factor when viewed from the whole.

Disrupting this is not imagination but destruction.
