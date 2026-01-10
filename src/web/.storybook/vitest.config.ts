import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from '../vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      coverage: {
        exclude: [
          '**/hooks/**',
          '**/__stories__/**',
          '**/*.stories.{ts,tsx}',
          'node_modules/**'
        ]
      }
    }
  })
)
