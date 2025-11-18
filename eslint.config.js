// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import { FlatCompat } from '@eslint/eslintrc' // Use Compat to expand Prettier configuration
import pluginJs from '@eslint/js'
import pluginImport from 'eslint-plugin-import'
import pluginPrettier from 'eslint-plugin-prettier'
import pluginReact from 'eslint-plugin-react'
import pluginReactHooks from 'eslint-plugin-react-hooks'
// eslint-disable-next-line import/order
import storybook from 'eslint-plugin-storybook'

// eslint.config.js (Proposed Revision)

import pluginUnicorn from 'eslint-plugin-unicorn'
import pluginUnusedImports from 'eslint-plugin-unused-imports'
import globals from 'globals'
// Import from typescript-eslint instead of tseslintPlugin, tseslintParser
import tseslint from 'typescript-eslint'
import pluginVanillaExtract from './eslint-rules/vanilla-extract-recess-order.js'
// To avoid Prettier conflicts, do not use eslint-config-prettier (use plugin-prettier instead)

// Configuration to expand Prettier in compatibility mode
const compat = new FlatCompat({
  baseDirectory: import.meta.url
  // baseDirectory: __dirname, // For Node.js environment
})

// eslint-disable-next-line import/no-default-export
export default [
  // 1. Base Configuration (JavaScript + TypeScript)
  // ESLint recommended configuration
  pluginJs.configs.recommended, // Expand TypeScript plugin configuration
  // Expand recommended configuration instead of tseslintPlugin.configs.recommended
  ...tseslint.configs.recommended, // 2. Custom Configuration (React, Import, Unused Imports, etc.)
  {
    files: ['**/*.{ts,tsx}', '!src/pipe/cli/**'],

    // 🚨 tseslint.configs.recommended has already configured the parser, so it's often unnecessary here
    // languageOptions: {
    //     parser: tseslintParser, // Removed
    //     parserOptions: { // Removed
    //         // ...
    //     },
    //     // ...
    // },

    plugins: {
      react: pluginReact,
      'react-hooks': pluginReactHooks,
      unicorn: pluginUnicorn,
      import: pluginImport,
      'unused-imports': pluginUnusedImports,
      'vanilla-extract': pluginVanillaExtract,
      // Prettier is configured in rules, so it's often unnecessary here
      prettier: pluginPrettier
    },

    rules: {
      // To avoid conflicts, remove ESLint rules that duplicate Prettier and enable pure Prettier

      // ❌ Removed: ...prettierConfig.rules, // Disable all ESLint formatting rules
      // ❌ Removed: semi: ["error", "never"], // Potential conflict with Prettier
      // ❌ Removed: quotes: ["error", "single"], // Potential conflict with Prettier

      // ✅ Run Prettier as an ESLint rule (most reliable)
      'prettier/prettier': 'error',
      'comma-dangle': ['error', 'never'],

      // ✅ React/Hooks
      ...pluginReact.configs.recommended.rules, // recommended rulesを先に適用
      ...pluginReactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off', // その後で上書き
      'react/prop-types': 'off', // prop-typesも無効化eslint
      'react/jsx-no-bind': [
        'error',
        {
          allowArrowFunctions: false,
          allowBind: false,
          ignoreRefs: true
        }
      ],
      'react/jsx-boolean-value': ['error', 'always'],
      'react/forbid-dom-props': ['error', { forbid: ['style'] }],

      // ✅ TypeScript
      'no-unused-vars': 'off', // Disable standard ESLint rules
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/consistent-type-definitions': ['error', 'type'],
      // Prefer `import type` for type-only imports to make intent explicit and avoid
      // accidental runtime imports. Start as 'warn' so we can safely roll out.
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports' }
      ],
      '@typescript-eslint/explicit-function-return-type': 'error',

      // ✅ Imports / Unused
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling', 'index']],
          pathGroups: [{ pattern: '@/**', group: 'internal' }],
          alphabetize: { order: 'asc', caseInsensitive: true },
          'newlines-between': 'always'
        }
      ],
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'warn',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_'
        }
      ],
      'import/no-default-export': 'error',

      // ✅ Style encapsulation: Restrict cross-directory style imports while allowing
      // same-directory `./style.css` and shared `@/styles/**` imports.
      // Note: `no-restricted-imports` does not support an allow-list object inside
      // `patterns`. Therefore we only ban the forms that represent cross-directory
      // imports: parent-relative imports (`../.../style.css`) and cross-component
      // alias imports under `@/components/.../style.css`.
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            // parent-relative style imports (cross-directory)
            '../**/style.css',
            '../**/style.css.ts',
            // cross-component alias imports (avoid importing another component's styles)
            '@/components/**/style.css',
            '@/components/**/style.css.ts'
          ]
        }
      ],

      // ✅ Others
      'arrow-body-style': ['error', 'as-needed'],
      'prefer-arrow-callback': ['error', { allowNamedFunctions: true }],
      'padding-line-between-statements': [
        'error',
        { blankLine: 'always', prev: '*', next: 'return' }
      ],
      // NOTE: function declarations/expressions are restricted, but we apply the
      // concrete enforcement via a dedicated override block below so we can
      // allow `function` in `use*.ts[x]` files (hooks) while banning it elsewhere.
      // Prevent abbreviation rule (unicorn)
      'unicorn/prevent-abbreviations': [
        'error',
        {
          allowList: {
            i: true,
            j: true,
            d: true,
            _: true
          },
          checkFilenames: false,
          checkProperties: false
        }
      ]
    },

    settings: {
      react: { version: 'detect' }
    }
  }, // 3. Apply Prettier last to disable all conflicting rules
  ...compat.extends('prettier'), // Node.js specific configuration for ts_analyzer.js
  {
    files: ['src/pipe/cli/ts_analyzer.js'],
    languageOptions: {
      globals: {
        ...globals.node
      }
    },
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
      'no-undef': 'off' // Disable no-undef as globals.node should handle it
    }
  },
  // Zodスキーマ定義をschema.ts以外のファイルで禁止するルール
  {
    files: ['**/*.{ts,tsx}', '!**/schema.ts'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: 'CallExpression[callee.object.name="z"]',
          message: 'Zod schema definitions are only allowed in schema.ts files.'
        }
      ]
    }
  },
  // React hooks usage restriction: disallow calling hooks in non-hook files
  // This rule forbids calls whose callee name looks like `useXxx` in files
  // that are not hook modules (use*.ts[x]). It covers both standard React
  // hooks and custom hooks named `useSomething` to avoid components
  // embedding hook logic directly.
  {
    files: ['**/*.{ts,tsx}'],
    // Exclude actual hook implementation files
    ignores: ['**/use*.{ts,tsx}'],

    rules: {
      'no-restricted-syntax': [
        'error',
        {
          // match any identifier starting with `use` followed by a capital letter
          selector: 'CallExpression[callee.name=/^use[A-Z][A-Za-z0-9]*$/]',
          message:
            'Hook calls (functions named useXxx) are only allowed in files named use*.ts or use*.tsx. Move hook usage into a hook module.'
        }
      ]
    }
  },
  // Enforce banning `function` keyword for all non-use* files.
  {
    files: ['**/*.{ts,tsx}', '!**/use*.{ts,tsx}', '!src/pipe/cli/**'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: 'FunctionDeclaration',
          message:
            'Function declarations are disallowed. Use arrow functions or exported named `function` only inside use* hooks.'
        },
        {
          selector: 'FunctionExpression',
          message: 'Function expressions are disallowed. Use arrow functions instead.'
        }
      ]
    }
  },
  {
    files: ['**/use*.{ts,tsx}'], // use*.ts[x]ファイルにのみ適用
    rules: {
      // use*.ts[x] ファイルではフックの使用を許可するため、
      // 関数キーワード禁止ルールを無効化します。
      'no-restricted-syntax': 'off'
    }
  },
  // atoms/{*ts,tsx} でuseStateを使うのを禁止するルール
  {
    files: ['src/web/components/atoms/**/*.{ts,tsx}'],
    ignores: ['**/*.stories.tsx'],
    rules: {
      // Forbid any hook call inside atoms; atoms should be pure presentational
      // and not hold local hook-based state. This matches any `useXxx` call.
      'no-restricted-syntax': [
        'error',
        { selector: 'CallExpression[callee.name=/^use[A-Z][A-Za-z0-9]*$/]' }
      ]
    }
  },
  ...storybook.configs['flat/recommended'],

  // Enforce property ordering inside vanilla-extract style objects
  {
    files: ['src/web/**/*.css.ts'],
    rules: {
      'vanilla-extract/recess-order': ['error']
    }
  },
  // Relax rules for story / demo files where inline handlers and style props
  // are common and acceptable for examples.
  {
    files: ['**/*.stories.@(js|jsx|ts|tsx)', 'src/stories/**', 'src/**/__stories__/**'],
    rules: {
      'react/jsx-no-bind': 'off',
      'react/forbid-dom-props': 'off',
      'no-restricted-syntax': 'off',
      'import/no-default-export': 'off'
    }
  },
  // ✅ Max lines per file (WARN) - 最初に適用される
  {
    files: ['**/*.{ts,tsx,js,jsx}'], // 対象ファイルを明示
    ignores: ['src/pipe/cli/**'], // src/pipe/cli 配下のファイルを無視
    rules: {
      'max-lines': [
        'warn',
        {
          max: 100,
          skipComments: true,
          skipBlankLines: true
        }
      ]
    }
  },
  // ✅ Max lines per file (ERROR) - 後から適用され、WARNを上書きする
  {
    files: ['**/*.{ts,tsx,js,jsx}'], // 対象ファイルを明示
    ignores: ['src/pipe/cli/**'], // src/pipe/cli 配下のファイルを無視
    rules: {
      'max-lines': [
        'error',
        {
          max: 300,
          skipComments: true,
          skipBlankLines: true
        }
      ]
    }
  }
]
