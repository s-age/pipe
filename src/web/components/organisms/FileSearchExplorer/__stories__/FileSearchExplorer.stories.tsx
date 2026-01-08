import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import React from 'react'
import { userEvent, within } from 'storybook/test'

import { AppStoreProvider } from '@/stores/useAppStore'

import { FileSearchExplorer } from '../index'

const Wrapper = ({ children }: React.PropsWithChildren<unknown>): JSX.Element => (
  <AppStoreProvider>{children}</AppStoreProvider>
)

const Meta = {
  title: 'Organisms/FileSearchExplorer',
  component: FileSearchExplorer,
  parameters: {
    layout: 'centered'
  },
  tags: ['autodocs'],
  decorators: [
    (Story: () => JSX.Element): JSX.Element => <Wrapper>{<Story />}</Wrapper>
  ]
} satisfies StoryMeta<typeof FileSearchExplorer>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    existsValue: [],
    onChange: () => {},
    'aria-label': 'Search files or directories'
  }
}

export const WithInitialPath: Story = {
  args: {
    existsValue: ['/path1', '/path2'],
    onChange: () => {},
    'aria-label': 'Search files or directories'
  },
  play: async ({ canvasElement }: { canvasElement: HTMLElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('combobox', { name: 'Search files or directories' })
    // Verify ARIA attributes
    await userEvent.click(input)
  }
}
