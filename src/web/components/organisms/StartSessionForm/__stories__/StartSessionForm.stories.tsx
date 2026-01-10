import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, userEvent, within } from 'storybook/test'

import { StartSessionForm } from '../index'

const mockSettings = {
  apiMode: 'expert',
  contextLimit: 10,
  expertMode: true,
  hyperparameters: {
    temperature: 0.7,
    topP: 0.9,
    topK: 5
  },
  language: 'en',
  maxToolCalls: 10,
  model: 'gpt-4',
  referenceTtl: 3,
  searchModel: 'gpt-4',
  sessionsPath: '/sessions',
  timezone: 'UTC',
  toolResponseExpiration: 3600,
  yolo: false
}

const mockParentOptions = [
  { value: 'session-1', label: 'Session 1' },
  { value: 'session-2', label: 'Session 2' }
]

const Meta = {
  title: 'Organisms/StartSessionForm',
  component: StartSessionForm,
  tags: ['autodocs'],
  args: {
    settings: mockSettings,
    parentOptions: mockParentOptions
  },
  parameters: {
    layout: 'fullscreen'
  }
} satisfies StoryMeta<typeof StartSessionForm>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state of the form with empty fields.
 */
export const Default: Story = {
  args: {}
}

/**
 * Form pre-filled with default values.
 */
export const WithDefaultValues: Story = {
  args: {
    defaultValues: {
      purpose: 'Test Purpose',
      background: 'Test Background',
      instruction: 'Test Instruction'
    }
  }
}

/**
 * Demonstrates form validation and submission interaction.
 */
export const Interaction: Story = {
  args: {
    defaultValues: {
      purpose: 'Interaction Test',
      background: 'Testing user interactions',
      instruction: 'Initial instruction'
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify the heading is present
    await expect(
      canvas.getByRole('heading', { name: /create new session/i })
    ).toBeInTheDocument()

    // Find the instruction field and change its value
    const instructionField = canvas.getByLabelText(/first instruction/i)
    await userEvent.clear(instructionField)
    await userEvent.type(instructionField, 'Updated instruction')
    await expect(instructionField).toHaveValue('Updated instruction')

    // Click the Create Session button
    const createButton = canvas.getByRole('button', { name: /create session/i })
    await expect(createButton).toBeEnabled()
    await userEvent.click(createButton)

    // Note: Navigation to /session/:id happens on success, which isn't easily
    // testable in Storybook, but we've verified the interaction triggers.
  }
}
