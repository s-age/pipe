import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import type { JSX } from 'react'

import { AppStoreProvider } from '@/stores/useAppStore'
import { useAppStore } from '@/stores/useAppStore'

import { LoadingOverlay } from '../index'

const Wrapper = ({ children }: React.PropsWithChildren<unknown>): JSX.Element => (
  <AppStoreProvider>
    {children}
    <LoadingOverlay />
  </AppStoreProvider>
)

const Meta = {
  title: 'Organisms/Loading',
  component: LoadingOverlay,
  decorators: [
    (Story: () => JSX.Element): JSX.Element => <Wrapper>{<Story />}</Wrapper>
  ]
} satisfies StoryMeta<typeof LoadingOverlay>

export default Meta
type Story = StoryObj<typeof Meta>

const Controls = (): JSX.Element => {
  const { hideLoader, showLoader } = useAppStore()

  const start = async (): Promise<void> => {
    showLoader()
    // simulate async work
    await new Promise((r) => setTimeout(r, 1200))
    hideLoader()
  }

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      <button onClick={() => showLoader()}>Show</button>
      <button onClick={() => hideLoader()}>Hide</button>
      <button onClick={start}>Simulate async</button>
    </div>
  )
}

export const Basic: Story = {
  render: (): JSX.Element => <Controls />
}
