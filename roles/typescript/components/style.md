# Component Styles (vanilla-extract) — Guidelines

Purpose: Keep component styles co-located and maintain component encapsulation. This document provides concise rules and practical notes.

**Core Principles**

- **Co-locate styles**: Component-specific styles must live in the same directory as the component and be named `style.css.ts` (vanilla-extract).
- **Do not import another component's `style.css` directly**: Importing styles from other components breaks component isolation. Extract shared tokens or utilities into `src/web/styles/` and import them via `@/styles/...`.
- **Allow exceptions for Storybook**: Examples and demos in Storybook may use inline handlers or style props for clarity; production code should avoid these patterns.

**File naming and exports**

- Prefer `style.css.ts` for vanilla-extract style files.
- Export named symbols only (e.g. `container`, `metaItem`, `primaryButton`). Use clear, small, reusable names.
- Avoid default exports for style modules.

Example:

```ts
// good: co-located
import { container } from './style.css'

// bad: cross-component import (forbidden)
import { metaItem } from '../OtherComponent/style.css'

// allowed: shared tokens
import { colors } from '@/styles/colors.css'
```

**Shared styles / tokens**

- Place shared tokens like colors, z-index values, spacing, and small utility classes under `src/web/styles/` (for example: `colors.css.ts`, `zIndex.css.ts`, `sessionMeta.css.ts`).
- Keep shared modules small and explicit about what they export.

**Linting / automated checks**

- The repository enforces a rule (ESLint) that bans parent-relative or cross-component imports of `style.css`. Run checks with:

```bash
npx eslint "src/web/**/*.{ts,tsx}"
```

- Story/demo files are allowed to relax some of these rules via the project's ESLint overrides.

**Commands**

```bash
# Run ESLint across components
npx eslint "src/web/**/*.{ts,tsx}"

# Run TypeScript type check
npx tsc -p src/web --noEmit
```

**Practical tips**

- If you need a token that currently lives inside another component, extract it to `src/web/styles/` and import it from there.
- Keep UI token modules (colors, zIndex, spacing, etc.) explicit and minimal. Components should only reference these tokens rather than importing styles from other components.
- Avoid inline `style={{ ... }}` in production code; if necessary, move the styles into the component's `style.css.ts`.

---

This is a compact guide. If helpful, I can expand this file with recommended naming conventions, an exceptions list, or step-by-step patterns for extracting shared tokens (for example, how to refactor a cross-component import into a `@/styles` token).
