import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { Decorator } from '@storybook/react-vite'
import { expect, fn, userEvent, within } from 'storybook/test'

import { AppStoreProvider } from '@/stores/useAppStore'

import { InstructionForm } from '../index'

const withAppStore: Decorator = (Story) => (
  <AppStoreProvider>
    <Story />
  </AppStoreProvider>
)

const Meta = {
  title: 'Organisms/InstructionForm',
  component: InstructionForm,
  tags: ['autodocs'],
  decorators: [withAppStore],
  args: {
    onSendInstruction: fn(),
    onRefresh: fn()
  }
} satisfies StoryMeta<typeof InstructionForm>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state of the instruction form, ready for user input.
 */
export const Default: Story = {
  args: {
    contextLimit: 10000,
    currentSessionId: 'session-123',
    isStreaming: false,
    tokenCount: 1000
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByPlaceholderText(/enter your instruction here/i)
    const sendButton = canvas.getByRole('button', { name: /send instruction/i })

    await expect(textarea).toBeInTheDocument()
    await expect(sendButton).toBeInTheDocument()

    await userEvent.type(textarea, 'Hello, this is a test instruction')
    await userEvent.click(sendButton)

    await expect(args.onSendInstruction).toHaveBeenCalledWith(
      'Hello, this is a test instruction'
    )
  }
}

/**
 * State when the session is streaming a response.
 * The input is disabled and a stop button is shown.
 */
export const Streaming: Story = {
  args: {
    contextLimit: 10000,
    currentSessionId: 'session-123',
    isStreaming: true,
    tokenCount: 2000
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByPlaceholderText(/enter your instruction here/i)
    const stopButton = canvas.getByRole('button', { name: /stop session/i })

    await expect(textarea).toBeDisabled()
    await expect(stopButton).toBeInTheDocument()
  }
}

/**
 * State when the context limit is nearly reached.
 * Shows a warning about the remaining context.
 */
export const LowContext: Story = {
  args: {
    contextLimit: 10000,
    currentSessionId: 'session-123',
    isStreaming: false,
    tokenCount: 9500
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const contextText = canvas.getByText(/\(5% context left\)/i)
    await expect(contextText).toBeInTheDocument()
  }
}
