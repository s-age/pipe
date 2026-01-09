import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import type { JSX } from 'react'
import { expect, userEvent, within, fn } from 'storybook/test'

import { Tabs } from '../index'

const Meta = {
  title: 'Molecules/Tabs',
  component: Tabs,
  tags: ['autodocs'],
  args: {
    onChange: fn()
  }
} satisfies StoryMeta<typeof Tabs>

export default Meta
type Story = StoryObj<typeof Meta>

const mockTabs = [
  { key: 'home', label: 'Home' },
  { key: 'profile', label: 'Profile' },
  { key: 'settings', label: 'Settings' }
]

export const Default: Story = {
  args: {
    activeKey: 'home',
    tabs: mockTabs
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const homeTab = canvas.getByRole('tab', { name: /home/i })
    const profileTab = canvas.getByRole('tab', { name: /profile/i })

    await expect(homeTab).toBeInTheDocument()
    await expect(homeTab).toHaveAttribute('aria-selected', 'true')
    await expect(profileTab).toHaveAttribute('aria-selected', 'false')
  }
}

export const Controlled: Story = {
  args: {
    activeKey: 'home',
    tabs: mockTabs
  },
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [activeKey, setActiveKey] = useState('home')

      const handleChange = (key: string): void => {
        setActiveKey(key)
        arguments_.onChange?.(key)
      }

      return (
        <div>
          <Tabs
            {...arguments_}
            activeKey={activeKey}
            tabs={mockTabs}
            onChange={handleChange}
          />
          <div style={{ marginTop: 16, padding: 16, border: '1px solid #ccc' }}>
            {activeKey === 'home' && <div role="tabpanel">Home Content</div>}
            {activeKey === 'profile' && <div role="tabpanel">Profile Content</div>}
            {activeKey === 'settings' && <div role="tabpanel">Settings Content</div>}
          </div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const profileTab = canvas.getByRole('tab', { name: /profile/i })

    await userEvent.click(profileTab)

    await expect(profileTab).toHaveAttribute('aria-selected', 'true')
    await expect(canvas.getByText(/profile content/i)).toBeInTheDocument()
    await expect(args.onChange).toHaveBeenCalledWith('profile')
  }
}
