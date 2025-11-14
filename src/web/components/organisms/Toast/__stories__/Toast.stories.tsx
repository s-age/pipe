import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import type { JSX } from 'react'

import { emitToast } from '@/lib/toastEvents'
import { AppStoreProvider } from '@/stores/useAppStore'

import { Toasts } from '../index'

const Wrapper = ({ children }: React.PropsWithChildren<unknown>): JSX.Element => (
  <AppStoreProvider>
    {children}
    <Toasts />
  </AppStoreProvider>
)

const Meta = {
  title: 'Organisms/Toast',
  component: Toasts,
  tags: ['autodocs'],
  decorators: [
    (Story: () => JSX.Element): JSX.Element => <Wrapper>{<Story />}</Wrapper>
  ]
} satisfies StoryMeta<typeof Toasts>

export default Meta
type Story = StoryObj<typeof Meta>

const Controls = (): JSX.Element => (
  <div style={{ display: 'flex', gap: 8 }}>
    <button
      onClick={() => {
        emitToast.success({
          title: 'Saved',
          description: 'Your changes were saved.'
        })
      }}
    >
      Success
    </button>
    <button
      onClick={() => {
        emitToast.failure({
          title: 'Failed',
          description: 'Something went wrong.'
        })
      }}
    >
      Failure
    </button>
    <button
      onClick={() => {
        emitToast.warning({
          title: 'Warning',
          description: 'Check this out.'
        })
      }}
    >
      Warning
    </button>
    <button
      onClick={() => {
        emitToast.show({
          status: 'success',
          description: 'No title example',
          duration: 3000
        })
      }}
    >
      No title
    </button>
  </div>
)

export const Basic: Story = {
  render: (): JSX.Element => <Controls />
}
