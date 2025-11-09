import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { fn } from 'storybook/test'

import { Header } from './Header'

export default { component: Header }
export const Meta = {
  title: 'Example/Header',
  component: Header,
  // This component will have an automatically generated Autodocs entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  parameters: {
    // More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
    layout: 'fullscreen'
  },
  args: {
    onLogin: fn(),
    onLogout: fn(),
    onCreateAccount: fn()
  }
} satisfies StoryMeta<typeof Header>

// Storybook meta is exported as a named export to comply with import/no-default-export
type Story = StoryObj<typeof Meta>

export const LoggedIn: Story = {
  args: {
    user: {
      name: 'Jane Doe'
    }
  }
}

export const LoggedOut: Story = {}
