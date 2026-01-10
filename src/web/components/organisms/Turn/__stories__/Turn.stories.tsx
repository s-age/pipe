import type { Decorator, Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, fn, within } from 'storybook/test'

import { AppStoreProvider } from '@/stores/useAppStore'

import { TurnComponent } from '../index'

const withAppStore: Decorator = (Story) => (
  <AppStoreProvider>
    <Story />
  </AppStoreProvider>
)

const Meta = {
  title: 'Organisms/Turn',
  component: TurnComponent,
  decorators: [withAppStore],
  tags: ['autodocs'],
  args: {
    index: 0,
    expertMode: false,
    onCancelEdit: fn(),
    onCopy: fn(),
    onDelete: fn(),
    onEditedChange: fn(),
    onFork: fn(),
    onRefresh: fn(),
    onSaveEdit: fn(),
    onStartEdit: fn()
  }
} satisfies StoryMeta<typeof TurnComponent>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * User task turn showing the user's instruction.
 */
export const UserTask: Story = {
  args: {
    turn: {
      type: 'user_task',
      instruction: 'Hello, how are you?',
      timestamp: '2024-01-01T12:00:00Z'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getAllByText(/1:/i)[0]).toBeInTheDocument()
    await expect(canvas.getAllByText(/You/i)[0]).toBeInTheDocument()
    await expect(canvas.getAllByText(/Hello, how are you\?/i)[0]).toBeInTheDocument()
  }
}

/**
 * Model response turn showing the assistant's reply with markdown rendering.
 */
export const ModelResponse: Story = {
  args: {
    turn: {
      type: 'model_response',
      content: 'I am doing well, thank you! **How can I help you today?**',
      timestamp: '2024-01-01T12:00:05Z'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getByText(/Model/i)).toBeInTheDocument()
    await expect(canvas.getAllByText(/I am doing well/i)[0]).toBeInTheDocument()
  }
}

/**
 * Tool response turn showing the result of a tool execution.
 */
export const ToolResponse: Story = {
  args: {
    turn: {
      type: 'tool_response',
      name: 'test_tool',
      response: {
        status: 'success',
        message: JSON.stringify({ result: 'Operation completed successfully' })
      },
      timestamp: '2024-01-01T12:00:10Z'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getByText(/Tool Response/i)).toBeInTheDocument()
    await expect(canvas.getAllByText(/success/i)[0]).toBeInTheDocument()
  }
}

/**
 * Function calling turn showing the tool invocation details.
 */
export const FunctionCalling: Story = {
  args: {
    turn: {
      type: 'function_calling',
      response: JSON.stringify({
        name: 'get_weather',
        arguments: { location: 'Tokyo' }
      }),
      timestamp: '2024-01-01T12:00:08Z'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getByText(/Function Calling/i)).toBeInTheDocument()
    await expect(canvas.getByText(/get_weather/i)).toBeInTheDocument()
  }
}

/**
 * Turn in editing mode showing the textarea and controls.
 */
export const Editing: Story = {
  args: {
    turn: {
      type: 'user_task',
      instruction: 'Original instruction',
      timestamp: '2024-01-01T12:00:00Z'
    },
    isEditing: true,
    editedContent: 'Editing this instruction'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByRole('textbox')
    await expect(textarea).toHaveValue('Editing this instruction')
    await expect(canvas.getByRole('button', { name: /Save/i })).toBeInTheDocument()
    await expect(canvas.getByRole('button', { name: /Cancel/i })).toBeInTheDocument()
  }
}
