// For more info, see https://github.com/storybookjs/eslint-plugin-storybook#configuration-flat-config-format
import storybook from "eslint-plugin-storybook";

// eslint.config.js (Proposed Revision)

import globals from 'globals'
import pluginJs from '@eslint/js'
// Import from typescript-eslint instead of tseslintPlugin, tseslintParser
import tseslint from 'typescript-eslint'
import pluginReact from 'eslint-plugin-react'
import pluginReactHooks from 'eslint-plugin-react-hooks'
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

export default [// 1. Base Configuration (JavaScript + TypeScript)
// ESLint recommended configuration
pluginJs.configs.recommended, // Expand TypeScript plugin configuration
// Expand recommended configuration instead of tseslintPlugin.configs.recommended
...tseslint.configs.recommended, // 2. Custom Configuration (React, Import, Unused Imports, etc.)
{
  files: ['**/*.{ts,tsx}'],

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
    'react/prop-types': 'off', // prop-typesも無効化

    // ✅ TypeScript
    'no-unused-vars': 'off', // Disable standard ESLint rules
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/consistent-type-definitions': ['error', 'type'],
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

    // ✅ Others
    'arrow-body-style': ['error', 'as-needed'],
    'prefer-arrow-callback': ['error', { allowNamedFunctions: true }],
    'padding-line-between-statements': [
      'error',
      { blankLine: 'always', prev: '*', next: 'return' },
    ],
    'no-restricted-syntax': [
      'error',
      {
        selector: 'FunctionDeclaration',
        message:
          'Function declarations are disallowed. Use arrow functions or class methods instead.',
      },
      {
        selector: 'FunctionExpression',
        message:
          'Function expressions are disallowed. Use arrow functions or class methods instead.',
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
}, ...storybook.configs["flat/recommended"]];
