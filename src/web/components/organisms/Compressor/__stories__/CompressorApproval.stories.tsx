import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { fn } from 'storybook/test'

import { AppStoreProvider } from '@/stores/useAppStore'

import { CompressorApproval } from '../CompressorApproval'

const Meta = {
  title: 'Organisms/Compressor/CompressorApproval',
  component: CompressorApproval,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <Story />
      </AppStoreProvider>
    )
  ],
  parameters: {
    layout: 'fullscreen'
  },
  args: {
    compressorSessionId: 'comp-session-123',
    sessionId: 'session-123',
    summary:
      'This is a verified summary of the turns. It contains the essence of the conversation.',
    start: 1,
    end: 5,
    isSubmitting: false,
    handleDeny: fn(),
    onRefresh: fn(async () => {}),
    setCompressorSessionId: fn(),
    setError: fn(),
    setIsSubmitting: fn(),
    setSummary: fn()
  }
} satisfies StoryMeta<typeof CompressorApproval>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {}

export const Submitting: Story = {
  args: {
    isSubmitting: true
  }
}

export const LongSummary: Story = {
  args: {
    summary: 'Summary line 1\nSummary line 2\n' + 'Very long summary text '.repeat(50)
  }
}

export const MissingRange: Story = {
  args: {
    start: undefined,
    end: undefined
  }
}
