/* eslint-disable max-lines */
// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
// Use Compat to expand Prettier configuration
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

import pluginMatchPropertiesOrder from './eslint-rules/match-props-order.js'
import pluginNoSnakeCaseProperties from './eslint-rules/no-snake-case-properties.js'
import pluginNoUselessBackticks from './eslint-rules/no-useless-backticks.js'
import pluginSortProperties from './eslint-rules/sort-props.js'
import pluginVanillaExtract from './eslint-rules/vanilla-extract-recess-order.js'
// To avoid Prettier conflicts, do not use eslint-config-prettier (use plugin-prettier instead)

// eslint-disable-next-line import/no-default-export
export default [
  // Ignore node_modules, dist, and build directories
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      '.vite/**',
      '.storybook/**',
      'storybook-static/**',
      'eslint-rules/**'
    ]
  },
  // 1. Base Configuration (JavaScript + TypeScript)
  // ESLint recommended configuration
  pluginJs.configs.recommended, // Expand TypeScript plugin configuration
  // Expand recommended configuration instead of tseslintPlugin.configs.recommended
  ...tseslint.configs.recommended, // 2. Custom Configuration (React, Import, Unused Imports, etc.)
  {
    files: ['**/*.{ts,tsx}', '!src/pipe/cli/**', '!eslint-rules/**'],

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
      'no-useless-backticks': pluginNoUselessBackticks,
      'no-snake-case-properties': pluginNoSnakeCaseProperties,
      'sort-props': pluginSortProperties,
      'match-props-order': pluginMatchPropertiesOrder,
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

      // ✅ Ban React.FC and React.FunctionComponent
      'no-restricted-syntax': [
        'error',
        {
          selector: 'TSTypeReference[typeName.name="FC"]',
          message: 'Avoid React.FC. Use JSX.Element for component return types.'
        },
        {
          selector: 'TSTypeReference[typeName.name="FunctionComponent"]',
          message:
            'Avoid React.FunctionComponent. Use JSX.Element for component return types.'
        }
      ],

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
      ],
      'no-useless-backticks/no-useless-backticks': 'error',
      'no-snake-case-properties/no-snake-case-properties': [
        'error',
        {
          ignoreDestructuring: false
        }
      ],
      'sort-props/sort-props': 'error',
      'match-props-order/match-props-order': 'error'
    },

    settings: {
      react: { version: 'detect' }
    }
  }, // 3. Apply Prettier last to disable all conflicting rules
  // Node.js specific configuration for ts_analyzer.ts
  {
    files: ['../../../src/pipe/cli/ts_analyzer.ts'],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        allowJs: true
      },
      globals: {
        ...globals.node
      }
    },
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
      'no-undef': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      'no-unexpected-multiline': 'off' // Disable no-undef as globals.node should handle it
    }
  },
  // Zodスキーマ定義をschema.ts以外のファイルで禁止するルール
  {
    files: ['**/*.{ts,tsx}'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: 'CallExpression[callee.object.name="z"]',
          message: 'Zod schema definitions are only allowed in schema.ts files.'
        },
        {
          // Forbid standard React hooks in non-hook files; custom hooks (useXxx) are allowed
          selector:
            'CallExpression[callee.name=/^use(State|Effect|Callback|Memo|Ref|Context|Reducer|ImperativeHandle|LayoutEffect|DebugValue|DeferredValue|Transition|Id|InsertionEffect)$/]',
          message:
            'Standard React hooks are only allowed in hook files (use*.ts or use*.tsx). Use custom hooks for logic.'
        },
        {
          // Forbid React.use* calls; prefer direct imports for token efficiency
          selector:
            'CallExpression[callee.object.name="React"][callee.property.name=/^(useState|useEffect|useCallback|useMemo|useRef|useContext|useReducer|useImperativeHandle|useLayoutEffect|useDebugValue|useDeferredValue|useTransition|useId|useInsertionEffect)$/]',
          message:
            "Use direct import for React hooks (e.g., import { useMemo } from 'react') instead of React.useMemo for better token efficiency."
        }
      ]
    }
  },
  // schema.tsではZodを使用許可
  {
    files: ['**/schema.ts'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: 'TSTypeReference[typeName.name="FC"]',
          message: 'Avoid React.FC. Use JSX.Element for component return types.'
        },
        {
          selector: 'TSTypeReference[typeName.name="FunctionComponent"]',
          message:
            'Avoid React.FunctionComponent. Use JSX.Element for component return types.'
        }
      ]
    }
  },
  // src/web/lib/validation ではZodを使用許可
  {
    files: ['lib/validation/**/*.ts'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: 'TSTypeReference[typeName.name="FC"]',
          message: 'Avoid React.FC. Use JSX.Element for component return types.'
        },
        {
          selector: 'TSTypeReference[typeName.name="FunctionComponent"]',
          message:
            'Avoid React.FunctionComponent. Use JSX.Element for component return types.'
        },
        {
          // Forbid standard React hooks in non-hook files; custom hooks (useXxx) are allowed
          selector:
            'CallExpression[callee.name=/^use(State|Effect|Callback|Memo|Ref|Context|Reducer|ImperativeHandle|LayoutEffect|DebugValue|DeferredValue|Transition|Id|InsertionEffect)$/]',
          message:
            'Standard React hooks are only allowed in hook files (use*.ts or use*.tsx). Use custom hooks for logic.'
        },
        {
          // Forbid React.use* calls; prefer direct imports for token efficiency
          selector:
            'CallExpression[callee.object.name="React"][callee.property.name=/^(useState|useEffect|useCallback|useMemo|useRef|useContext|useReducer|useImperativeHandle|useLayoutEffect|useDebugValue|useDeferredValue|useTransition|useId|useInsertionEffect)$/]',
          message:
            "Use direct import for React hooks (e.g., import { useMemo } from 'react') instead of React.useMemo for better token efficiency."
        }
      ]
    }
  },
  // Enforce banning `function` keyword and standard React hooks in atom files.
  {
    files: ['src/web/components/atoms/**/*.{ts,tsx}'],
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
        },
        {
          // Forbid standard React hooks in atom files; atoms should be pure presentational
          selector:
            'CallExpression[callee.name=/^use(State|Effect|Callback|Memo|Ref|Context|Reducer|ImperativeHandle|LayoutEffect|DebugValue|DeferredValue|Transition|Id|InsertionEffect)$/]',
          message:
            'Standard React hooks are only allowed in hook files (use*.ts or use*.tsx) or component files. Atoms should be pure presentational.'
        },
        {
          // Forbid React.use* calls in atom files
          selector:
            'CallExpression[callee.object.name="React"][callee.property.name=/^(useState|useEffect|useCallback|useMemo|useRef|useContext|useReducer|useImperativeHandle|useLayoutEffect|useDebugValue|useDeferredValue|useTransition|useId|useInsertionEffect)$/]',
          message:
            "Use direct import for React hooks (e.g., import { useMemo } from 'react') instead of React.useMemo for better token efficiency."
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
  },
  // ✅ console禁止ルール - *.stories.ts[x]と*.test.ts[x]以外で適用
  {
    files: ['**/*.{ts,tsx,js,jsx}'],
    ignores: ['**/*.stories.{ts,tsx}', '**/*.test.{ts,tsx}'],
    rules: {
      'no-console': 'error'
    }
  }
]
