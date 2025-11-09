import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, userEvent, within } from 'storybook/test'

import { Page } from './Page'

export default { component: Page }
export const Meta = {
  title: 'Example/Page',
  component: Page,
  parameters: {
    // More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
    layout: 'fullscreen'
  }
} satisfies StoryMeta<typeof Page>

// Storybook meta is exported as a named export to comply with import/no-default-export
type Story = StoryObj<typeof Meta>

export const LoggedOut: Story = {}

// More on component testing: https://storybook.js.org/docs/writing-tests/interaction-testing
export const LoggedIn: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const loginButton = canvas.getByRole('button', { name: /Log in/i })
    await expect(loginButton).toBeInTheDocument()
    await userEvent.click(loginButton)
    await expect(loginButton).not.toBeInTheDocument()

    const logoutButton = canvas.getByRole('button', { name: /Log out/i })
    await expect(logoutButton).toBeInTheDocument()
  }
}
