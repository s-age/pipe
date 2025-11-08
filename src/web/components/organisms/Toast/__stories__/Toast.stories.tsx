import type { Meta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import type { JSX } from 'react'

import { AppStoreProvider } from '@/stores/useAppStore'

import useToast from '../hooks/useToast'
import Toasts from '../index'

const Wrapper = ({ children }: React.PropsWithChildren<unknown>): JSX.Element => (
  <AppStoreProvider>
    {children}
    <Toasts />
  </AppStoreProvider>
)

const meta = {
  title: 'Organisms/Toast',
  component: Toasts,
  tags: ['autodocs'],
  decorators: [
    (Story: () => JSX.Element): JSX.Element => <Wrapper>{<Story />}</Wrapper>,
  ],
} satisfies Meta<typeof Toasts>

export default meta
type Story = StoryObj<typeof meta>

const Controls = (): JSX.Element => {
  const t = useToast()

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      <button
        onClick={() =>
          t.success({ title: 'Saved', description: 'Your changes were saved.' })
        }
      >
        Success
      </button>
      <button
        onClick={() =>
          t.failure({ title: 'Failed', description: 'Something went wrong.' })
        }
      >
        Failure
      </button>
      <button
        onClick={() => t.warning({ title: 'Warning', description: 'Check this out.' })}
      >
        Warning
      </button>
      <button
        onClick={() =>
          t.show({ status: 'success', description: 'No title example', duration: 3000 })
        }
      >
        No title
      </button>
    </div>
  )
}

export const Basic: Story = {
  render: (): JSX.Element => <Controls />,
}
