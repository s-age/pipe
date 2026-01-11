import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import type { JSX } from 'react'
import { expect, fireEvent, userEvent, within } from 'storybook/test'
import { z } from 'zod'

import { Button } from '@/components/atoms/Button'
import { Form, useFormContext } from '@/components/organisms/Form'
import { API_BASE_URL } from '@/constants/uri'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { HyperParameters } from '../index'

const mockSessionDetail: SessionDetail = {
  sessionId: 'test-session-id',
  purpose: 'Test Purpose',
  background: 'Test Background',
  instruction: 'Test Instruction',
  hyperparameters: {
    temperature: 0.7,
    topP: 0.9,
    topK: 5
  },
  references: [],
  todos: [],
  turns: [],
  artifacts: [],
  roles: [],
  parent: null,
  procedure: null,
  multiStepReasoningEnabled: false
}

const Meta = {
  title: 'Organisms/HyperParameters',
  component: HyperParameters,
  tags: ['autodocs'],
  args: {
    sessionDetail: mockSessionDetail
  }
} satisfies StoryMeta<typeof HyperParameters>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state with standard hyperparameters
 */
export const Default: Story = {}

/**
 * Demonstrates error display when wrapped in a Form context
 */
export const WithErrors: Story = {
  render: (arguments_): JSX.Element => {
    const FormWithError = (): JSX.Element => {
      const methods = useFormContext()

      const handleSubmit = async (): Promise<void> => {
        await methods.trigger('hyperparameters')
      }

      return (
        <>
          <HyperParameters {...arguments_} />
          <Button type="button" onClick={handleSubmit}>
            Trigger Validation
          </Button>
        </>
      )
    }

    const schema = z.object({
      hyperparameters: z
        .object({
          temperature: z.number(),
          topP: z.number(),
          topK: z.number()
        })
        .refine(() => false, {
          message: 'Invalid hyperparameters configuration'
        })
    })

    return (
      <Form
        schema={schema}
        defaultValues={{
          hyperparameters: {
            temperature: 0.7,
            topP: 0.9,
            topK: 5
          }
        }}
      >
        <FormWithError />
      </Form>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /trigger validation/i })
    await userEvent.click(button)

    const errorMessage = await canvas.findByText(/invalid hyperparameters/i)
    await expect(errorMessage).toBeInTheDocument()
  }
}

/**
 * Interactive story demonstrating slider updates and API mocking
 */
export const Interactive: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post(
          `${API_BASE_URL}/meta/hyperparameters/:sessionId`,
          async ({ params }) =>
            HttpResponse.json({
              message: 'Hyperparameters updated successfully',
              session: {
                ...mockSessionDetail,
                sessionId: params.sessionId as string
              }
            })
        )
      ]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Find sliders. Since they might not be perfectly labeled for getByLabelText,
    // we find them by their role and name attribute.
    const sliders = canvas.getAllByRole('slider')
    const temperatureSlider = sliders.find(
      (s) => s.getAttribute('name') === 'hyperparameters.temperature'
    )

    if (!temperatureSlider) {
      throw new Error('Temperature slider not found')
    }

    // Verify initial value
    await expect(temperatureSlider).toHaveValue('0.7')

    // Simulate change using fireEvent.change (Issue 6 in storybook.md)
    fireEvent.change(temperatureSlider, { target: { value: '1.5' } })

    // Trigger API call on MouseUp
    fireEvent.mouseUp(temperatureSlider)

    // Verify UI update
    await expect(temperatureSlider).toHaveValue('1.5')
  }
}
