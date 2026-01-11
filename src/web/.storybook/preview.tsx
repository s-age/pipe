/* eslint-disable import/no-default-export */
import type { Preview, Decorator } from '@storybook/react-vite'
import { initialize, mswLoader } from 'msw-storybook-addon'

// Load app global vanilla-extract styles so Storybook matches app appearance.
// The file uses `globalStyle(...)` and side-effects on import are intended.
import '@/styles/global.css'
import { themeClass } from '../styles/theme.css'

// Initialize MSW
initialize({
  onUnhandledRequest: 'bypass',
  quiet: true
})

// Apply theme class to all stories
const withTheme: Decorator = (Story) => (
  <div className={themeClass}>
    <Story />
  </div>
)

const preview: Preview = {
  decorators: [withTheme],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i
      }
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo'
    }
  },
  loaders: [mswLoader]
}

export default preview
