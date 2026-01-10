import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'

import { API_BASE_URL } from '@/constants/uri'

import { ReferenceComponent } from '../index'

const Meta = {
  title: 'Organisms/Reference',
  component: ReferenceComponent,
  tags: ['autodocs'],
  args: {
    currentSessionId: 'test-session-id',
    index: 0,
    reference: {
      path: 'src/web/components/organisms/Reference/index.tsx',
      disabled: false,
      persist: false,
      ttl: 3
    },
    refreshSessions: fn()
  },
  parameters: {
    msw: {
      handlers: [
        http.patch(`${API_BASE_URL}/session/:sessionId/references/:index/persist`, () =>
          HttpResponse.json({ message: 'Success' })
        ),
        http.patch(`${API_BASE_URL}/session/:sessionId/references/:index/ttl`, () =>
          HttpResponse.json({ message: 'Success' })
        ),
        http.patch(`${API_BASE_URL}/session/:sessionId/references/:index/toggle`, () =>
          HttpResponse.json({
            disabled: true,
            message: 'Success'
          })
        )
      ]
    }
  }
} satisfies StoryMeta<typeof ReferenceComponent>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state of the reference component.
 */
export const Default: Story = {}

/**
 * Reference in a persisted (locked) state.
 */
export const Persisted: Story = {
  args: {
    reference: {
      path: 'src/web/components/organisms/Reference/index.tsx',
      disabled: false,
      persist: true,
      ttl: 5
    }
  }
}

/**
 * Reference in a disabled state (strikethrough).
 */
export const Disabled: Story = {
  args: {
    reference: {
      path: 'src/web/components/organisms/Reference/index.tsx',
      disabled: true,
      persist: false,
      ttl: 3
    }
  }
}

/**
 * Interaction test for TTL increment and decrement.
 */
export const TTLInteraction: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    // Increment TTL
    const incrementButton = canvas.getByRole('button', {
      name: /increase ttl/i
    })
    await userEvent.click(incrementButton)
    await waitFor(() => expect(args.refreshSessions).toHaveBeenCalled())

    // Decrement TTL
    const decrementButton = canvas.getByRole('button', {
      name: /decrease ttl/i
    })
    await userEvent.click(decrementButton)
    await waitFor(() => expect(args.refreshSessions).toHaveBeenCalled())
  }
}

/**
 * Interaction test for toggling the reference enabled state.
 */
export const ToggleInteraction: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    const toggle = canvas.getByRole('switch', { name: /toggle reference/i })
    await userEvent.click(toggle)
    await waitFor(() => expect(args.refreshSessions).toHaveBeenCalled(), {
      timeout: 3000
    })
  }
}

/**
 * Interaction test for toggling the persist (lock) state.
 */
export const PersistInteraction: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    const lockButton = canvas.getByRole('button', { name: /lock reference/i })
    await userEvent.click(lockButton)
    await waitFor(() => expect(args.refreshSessions).toHaveBeenCalled())
  }
}
