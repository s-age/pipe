import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { ReactNode } from 'react'

import { Fieldset } from '../index'

const Meta = {
  title: 'Molecules/Fieldset',
  component: Fieldset,
  tags: ['autodocs'],
  args: {
    legend: 'Fieldset Legend',
    children: (
      <input
        type="text"
        placeholder="Input inside fieldset"
        style={{
          padding: '8px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          width: '100%'
        }}
      />
    )
  }
} satisfies StoryMeta<typeof Fieldset>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default Fieldset with a legend and a simple input child.
 */
export const Default: Story = {}

/**
 * Fieldset with a hint message to provide additional context.
 */
export const WithHint: Story = {
  args: {
    hint: 'This is a hint message that helps the user understand what to enter.'
  }
}

/**
 * Fieldset with a string error message.
 */
export const WithErrorString: Story = {
  args: {
    error: 'This is a validation error message.'
  }
}

/**
 * Fieldset with a FieldError object, commonly used with react-hook-form.
 */
export const WithFieldError: Story = {
  args: {
    error: {
      type: 'required',
      message: 'This field is required and cannot be left empty.'
    } as unknown as ReactNode
  }
}

/**
 * Fieldset displaying both a hint and an error message.
 * Note: The hint is typically hidden from screen readers when an error is present (aria-hidden={!!error}).
 */
export const WithHintAndError: Story = {
  args: {
    hint: 'This hint might be hidden from screen readers if an error is present.',
    error: 'An error occurred while processing this field.'
  }
}

/**
 * Demonstrates the render prop pattern where children is a function.
 * This allows the child components to access the generated hintId and errorId for ARIA attributes.
 */
export const RenderPropertyPattern: Story = {
  args: {
    legend: 'Render Prop Pattern',
    hint: 'Hint for ARIA',
    error: 'Error for ARIA',
    children: (ids) => (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label htmlFor="aria-input">Label</label>
        <input
          id="aria-input"
          type="text"
          placeholder="Input with ARIA"
          aria-describedby={
            `${ids.hintId || ''} ${ids.errorId || ''}`.trim() || undefined
          }
          style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
      </div>
    )
  }
}

/**
 * Fieldset with a custom className applied for additional styling.
 */
export const CustomClassName: Story = {
  args: {
    className: 'custom-fieldset-class',
    legend: 'Custom Styled Fieldset'
  }
}
