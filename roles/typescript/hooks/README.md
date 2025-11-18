# Hooks Rules (machine-checkable)

This folder contains minimal machine-checkable rules for hooks used by the `roles/typescript` guidance.

How to run the checker locally:

```bash
# from repo root
node scripts/check-hooks.js
```

What the checker validates:
- Filenames in `hooks/` should start with `use` (exceptions: `*Context.tsx`, `*Provider.tsx`).
- Exported hook names must match the naming regex defined in `.rules.json` (default: `^use[A-Z]...`).
- `Handlers` hooks are scanned to ensure they do not reference `toast` or `useToast` (enforces separation of concerns).

If you want to tighten or relax rules, edit `.rules.json` in this directory.
