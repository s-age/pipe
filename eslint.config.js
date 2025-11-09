// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import storybook from 'eslint-plugin-storybook'

// eslint.config.js (Proposed Revision)

import globals from 'globals'
import pluginJs from '@eslint/js'
// Import from typescript-eslint instead of tseslintPlugin, tseslintParser
import tseslint from 'typescript-eslint'
import pluginReact from 'eslint-plugin-react'
import pluginReactHooks from 'eslint-plugin-react-hooks'
import pluginUnicorn from 'eslint-plugin-unicorn'
// To avoid Prettier conflicts, do not use eslint-config-prettier (use plugin-prettier instead)
import pluginPrettier from 'eslint-plugin-prettier'
import pluginImport from 'eslint-plugin-import'
import pluginUnusedImports from 'eslint-plugin-unused-imports'
import { FlatCompat } from '@eslint/eslintrc' // Use Compat to expand Prettier configuration

// Configuration to expand Prettier in compatibility mode
const compat = new FlatCompat({
  baseDirectory: import.meta.url,
  // baseDirectory: __dirname, // For Node.js environment
})

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
      // Prettier is configured in rules, so it's often unnecessary here
      prettier: pluginPrettier,
    },

    rules: {
      // To avoid conflicts, remove ESLint rules that duplicate Prettier and enable pure Prettier

      // ❌ Removed: ...prettierConfig.rules, // Disable all ESLint formatting rules
      // ❌ Removed: semi: ["error", "never"], // Potential conflict with Prettier
      // ❌ Removed: quotes: ["error", "single"], // Potential conflict with Prettier

      // ✅ Run Prettier as an ESLint rule (most reliable)
      'prettier/prettier': 'error',

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
          ignoreRefs: true,
        },
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
        { prefer: 'type-imports' },
      ],
      '@typescript-eslint/explicit-function-return-type': 'error',

      // ✅ Imports / Unused
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling', 'index']],
          pathGroups: [{ pattern: '@/**', group: 'internal' }],
          alphabetize: { order: 'asc', caseInsensitive: true },
          'newlines-between': 'always',
        },
      ],
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'warn',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_',
        },
      ],
      'import/no-default-export': 'error',

      // ✅ Style encapsulation: Restrict style.css.ts imports
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['**/style.css.ts'],
              message:
                'Importing styles from style.css.ts files is only allowed from the current directory or from src/styles/.',
              // allowプロパティはpatternsの直下ではなく、groupなどと同じレベルで指定
              // ここでは、特定のパターンを許可するためにallowを直接使用するのではなく、
              // 複数のパターンを定義して、許可するパターンと禁止するパターンを分ける
            },
            {
              // 同一ディレクトリからのインポートを許可
              group: ['./style.css.ts'],
              // このパターンは許可されるため、messageは不要
            },
            {
              // src/styles/からのインポートを許可
              group: ['@/styles/**/*.css.ts'],
              // このパターンは許可されるため、messageは不要
            },
          ],
        },
      ],

      // ✅ Others
      'arrow-body-style': ['error', 'as-needed'],
      'prefer-arrow-callback': ['error', { allowNamedFunctions: true }],
      'padding-line-between-statements': [
        'error',
        { blankLine: 'always', prev: '*', next: 'return' },
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
            _: true,
          },
          checkFilenames: false,
          checkProperties: false,
        },
      ],
    },

    settings: {
      react: { version: 'detect' },
    },
  }, // 3. Apply Prettier last to disable all conflicting rules
  ...compat.extends('prettier'), // Node.js specific configuration for ts_analyzer.js
  {
    files: ['src/pipe/cli/ts_analyzer.js'],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
      'no-undef': 'off', // Disable no-undef as globals.node should handle it
    },
  },
  // Zodスキーマ定義をschema.ts以外のファイルで禁止するルール
  {
    files: ['**/*.{ts,tsx}', '!**/schema.ts'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: 'CallExpression[callee.object.name="z"]',
          message: 'Zod schema definitions are only allowed in schema.ts files.',
        },
      ],
    },
  },
  // React標準フックをuse*.ts[x]ファイル以外で禁止するルール (修正版)
  {
    files: ['**/*.{ts,tsx}'],
    // 🚨 use*.ts[x] ファイルを除外
    ignores: ['**/use*.{ts,tsx}'], // 👈 この行を追加

    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector:
            'CallExpression[callee.name=/^(use(State|Ref|Effect|Callback|Memo))$/]',
          message:
            'React standard hooks (useState, useRef, useEffect, useCallback, useMemo) are only allowed in use*.ts[x] files.',
        },
      ],
    },
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
            'Function declarations are disallowed. Use arrow functions or exported named `function` only inside use* hooks.',
        },
        {
          selector: 'FunctionExpression',
          message: 'Function expressions are disallowed. Use arrow functions instead.',
        },
      ],
    },
  },
  {
    files: ['**/use*.{ts,tsx}'], // use*.ts[x]ファイルにのみ適用
    rules: {
      // use*.ts[x] ファイルではフックの使用を許可するため、
      // 関数キーワード禁止ルールを無効化します。
      'no-restricted-syntax': 'off',
    },
  },
  ...storybook.configs['flat/recommended'],
  // Relax rules for story / demo files where inline handlers and style props
  // are common and acceptable for examples.
  {
    files: ['**/*.stories.@(js|jsx|ts|tsx)', 'src/stories/**', 'src/**/__stories__/**'],
    rules: {
      'react/jsx-no-bind': 'off',
      'react/forbid-dom-props': 'off',
      'no-restricted-syntax': 'off',
      'import/no-default-export': 'off',
    },
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
          skipBlankLines: true,
        },
      ],
    },
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
          skipBlankLines: true,
        },
      ],
    },
  },
]
