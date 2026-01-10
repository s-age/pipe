import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import type { JSX } from 'react'
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { TodoList } from '../index'

const mockSessionDetail: SessionDetail = {
  sessionId: 'test-session-id',
  purpose: 'Test Purpose',
  background: 'Test Background',
  instruction: 'Test Instruction',
  artifacts: [],
  roles: [],
  references: [],
  hyperparameters: null,
  multiStepReasoningEnabled: false,
  parent: null,
  procedure: null,
  turns: [],
  todos: [
    { title: 'Todo 1', checked: false },
    { title: 'Todo 2', checked: true }
  ]
}

const emptySessionDetail: SessionDetail = {
  ...mockSessionDetail,
  todos: []
}

const Meta = {
  title: 'Organisms/TodoList',
  component: TodoList,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <Story />
      </AppStoreProvider>
    )
  ],
  args: {
    sessionDetail: mockSessionDetail,
    onSessionDetailUpdate: fn()
  }
} satisfies StoryMeta<typeof TodoList>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail
  }
}

export const Empty: Story = {
  args: {
    sessionDetail: emptySessionDetail
  }
}

export const Interaction: Story = {
  parameters: {
    msw: {
      handlers: [
        http.patch(`${API_BASE_URL}/session/:sessionId/todos`, () =>
          HttpResponse.json({ message: 'Todos updated' })
        ),
        http.delete(`${API_BASE_URL}/session/:sessionId/todos`, () =>
          HttpResponse.json({ message: 'All todos deleted' })
        ),
        http.get(`${API_BASE_URL}/session/:sessionId`, () =>
          HttpResponse.json(mockSessionDetail)
        )
      ]
    }
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify initial state
    const todo1 = canvas.getByText('Todo 1')
    const todo2 = canvas.getByText('Todo 2')
    await expect(todo1).toBeInTheDocument()
    await expect(todo2).toBeInTheDocument()

    // Test checkbox toggle
    const checkboxes = canvas.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])

    // Wait for API call and callback with increased timeout
    await waitFor(
      () => expect(args.onSessionDetailUpdate).toHaveBeenCalled(),
      { timeout: 3000 }
    )

    // Test Delete All button
    const deleteButton = canvas.getByRole('button', { name: /delete all todos/i })

    // Mock window.confirm
    const confirmSpy = fn(() => true)
    window.confirm = confirmSpy

    await userEvent.click(deleteButton)

    await expect(confirmSpy).toHaveBeenCalled()
    await waitFor(
      () => expect(args.onSessionDetailUpdate).toHaveBeenCalledTimes(2),
      { timeout: 3000 }
    )
  }
}
