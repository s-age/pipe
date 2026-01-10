import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import { expect, userEvent, within } from 'storybook/test'

import { API_BASE_URL } from '@/constants/uri'

import { MultiStepReasoning } from '../index'

const Meta = {
  title: 'Organisms/MultiStepReasoning',
  component: MultiStepReasoning,
  tags: ['autodocs'],
  parameters: {
    msw: {
      handlers: [
        http.patch(
          `${API_BASE_URL}/session/:sessionId/multi_step_reasoning`,
          async ({ request }) => {
            const body = await request.json()

            return HttpResponse.json({
              message: 'Multi-step reasoning updated',
              session: {
                multiStepReasoningEnabled: (
                  body as { multiStepReasoningEnabled: boolean }
                ).multiStepReasoningEnabled
              }
            })
          }
        )
      ]
    }
  }
} satisfies StoryMeta<typeof MultiStepReasoning>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state: Multi-step reasoning is disabled.
 */
export const Default: Story = {
  args: {
    currentSessionId: 'test-session-id',
    multiStepReasoningEnabled: false
  }
}

/**
 * Enabled state: Multi-step reasoning is enabled.
 */
export const Enabled: Story = {
  args: {
    currentSessionId: 'test-session-id',
    multiStepReasoningEnabled: true
  }
}

/**
 * Interaction: Verifies that clicking the checkbox toggles the state.
 * The API call is mocked via MSW.
 */
export const Interaction: Story = {
  args: {
    currentSessionId: 'test-session-id',
    multiStepReasoningEnabled: false
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox', { name: /multi-step reasoning/i })

    // Initial state
    await expect(checkbox).not.toBeChecked()

    // Toggle to enabled
    await userEvent.click(checkbox)
    await expect(checkbox).toBeChecked()

    // Toggle back to disabled
    await userEvent.click(checkbox)
    await expect(checkbox).not.toBeChecked()
  }
}
