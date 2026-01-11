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

/**
 * Compressed history turn showing compressed previous conversation.
 * Covers lines 114-116 and 137-144 in index.tsx
 */
export const CompressedHistory: Story = {
  args: {
    turn: {
      type: 'compressed_history',
      content:
        'Previous conversation has been compressed. The user asked about weather and I provided information.',
      timestamp: '2024-01-01T11:00:00Z',
      originalTurnsRange: [0, 1, 2, 3, 4, 5]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    // Use getAllByText since "Compressed" appears in multiple places
    const compressedElements = canvas.getAllByText(/Compressed/i)
    expect(compressedElements.length).toBeGreaterThan(0)
    // Use getAllByText since content appears in both raw and rendered markdown
    const contentElements = canvas.getAllByText(
      /Previous conversation has been compressed/i
    )
    expect(contentElements.length).toBeGreaterThan(0)
  }
}

/**
 * Unknown turn type showing the default handling with JSON display.
 * Covers lines 159-164 in index.tsx (default case)
 */
export const UnknownType: Story = {
  args: {
    turn: {
      type: 'unknown_type',
      someData: 'Example data',
      timestamp: '2024-01-01T12:00:00Z'
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    // Use getAllByText since "Unknown" appears in the header and the JSON
    const unknownElements = canvas.getAllByText(/Unknown/i)
    expect(unknownElements.length).toBeGreaterThan(0)
    // The turn data should be rendered as JSON
    await expect(canvas.getByText(/unknown_type/i)).toBeInTheDocument()
  }
}

/**
 * User task with missing instruction field.
 * Covers line 134 in index.tsx (instruction fallback to empty string)
 */
export const UserTaskWithoutInstruction: Story = {
  args: {
    turn: {
      type: 'user_task',
      timestamp: '2024-01-01T12:00:00Z'
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getAllByText(/You/i)[0]).toBeInTheDocument()
  }
}

/**
 * Turn without timestamp field.
 * Covers line 178 in index.tsx (timestamp fallback to empty string)
 */
export const TurnWithoutTimestamp: Story = {
  args: {
    turn: {
      type: 'model_response',
      content: 'Response without timestamp'
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getByText(/Model/i)).toBeInTheDocument()
  }
}

/**
 * Turn without type field.
 * Covers line 199 in index.tsx (type fallback to 'unknown')
 */
export const TurnWithoutType: Story = {
  args: {
    turn: {
      content: 'Data without type',
      timestamp: '2024-01-01T12:00:00Z'
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const unknownElements = canvas.getAllByText(/Unknown/i)
    expect(unknownElements.length).toBeGreaterThan(0)
  }
}

/**
 * Expert mode with edit and delete buttons.
 * Covers expert mode interactions and handler fallbacks (lines 96-102)
 */
export const ExpertMode: Story = {
  args: {
    expertMode: true,
    turn: {
      type: 'user_task',
      instruction: 'Test instruction',
      timestamp: '2024-01-01T12:00:00Z'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(canvas.getByLabelText(/Edit turn/i)).toBeInTheDocument()
    await expect(canvas.getByLabelText(/Delete turn/i)).toBeInTheDocument()
  }
}

/**
 * Expert mode with model response showing fork button.
 * Covers fork button visibility and handler fallback
 */
export const ExpertModeModelResponse: Story = {
  args: {
    expertMode: true,
    turn: {
      type: 'model_response',
      content: 'Test model response',
      timestamp: '2024-01-01T12:00:00Z'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(
      canvas.getByLabelText(/Fork conversation from this turn/i)
    ).toBeInTheDocument()
    await expect(canvas.getByLabelText(/Edit turn/i)).toBeInTheDocument()
    await expect(canvas.getByLabelText(/Delete turn/i)).toBeInTheDocument()
  }
}
