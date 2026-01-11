import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { ErrorMessage } from '../index'

const Meta = {
  title: 'Atoms/ErrorMessage',
  component: ErrorMessage,
  tags: ['autodocs'],
  argTypes: {
    error: { control: 'object' },
    message: { control: 'text' }
  }
} satisfies StoryMeta<typeof ErrorMessage>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default usage with a plain string message.
 */
export const Default: Story = {
  args: {
    message: 'This is an error message'
  }
}

/**
 * Usage with a FieldError object from react-hook-form.
 */
export const WithFieldError: Story = {
  args: {
    error: {
      type: 'required',
      message: 'This field is required'
    }
  }
}

/**
 * Demonstrates that the 'message' prop takes precedence over the 'error' prop.
 */
export const Precedence: Story = {
  args: {
    message: 'Custom message (takes precedence)',
    error: {
      type: 'validation',
      message: 'FieldError message (should be ignored)'
    }
  }
}

/**
 * Tests the component with a long error message to verify layout and wrapping.
 */
export const LongMessage: Story = {
  args: {
    message:
      'This is a very long error message to test how the component handles wrapping and layout when the text exceeds the container width. It should remain readable and properly styled.'
  }
}

/**
 * Tests with a FieldError where message is not a string (line 19 coverage).
 */
export const WithNonStringFieldErrorMessage: Story = {
  args: {
    error: {
      type: 'custom',
      message: { key: 'error.required' } as unknown as string
    }
  }
}
