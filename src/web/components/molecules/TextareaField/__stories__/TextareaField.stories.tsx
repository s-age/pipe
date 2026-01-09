import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { z } from 'zod'

import { Form } from '@/components/organisms/Form'

import { TextareaField } from '../index'

const Meta = {
  title: 'Molecules/TextareaField',
  component: TextareaField,
  tags: ['autodocs'],
  args: {
    id: 'textarea-field',
    label: 'Description',
    name: 'description',
    placeholder: 'Enter description here...'
  }
} satisfies StoryMeta<typeof TextareaField>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state of the TextareaField.
 */
export const Default: Story = {
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ [arguments_.name]: '' }}>
      <TextareaField {...arguments_} />
    </Form>
  )
}

/**
 * TextareaField in a read-only state.
 */
export const ReadOnly: Story = {
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ [arguments_.name]: 'This is a read-only value.' }}>
      <TextareaField {...arguments_} readOnly={true} />
    </Form>
  )
}

/**
 * TextareaField marked as required.
 */
export const Required: Story = {
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ [arguments_.name]: '' }}>
      <TextareaField {...arguments_} required={true} />
    </Form>
  )
}

/**
 * Integration with React Hook Form demonstrating validation and error states.
 */
export const WithRHF: Story = {
  render: (arguments_): JSX.Element => {
    const schema = z.object({
      [arguments_.name]: z.string().min(1, 'Description is required')
    })

    return (
      <Form schema={schema} defaultValues={{ [arguments_.name]: '' }} mode="onBlur">
        <TextareaField {...arguments_} />
        <div style={{ marginTop: '1rem' }}>
          <button type="submit">Submit</button>
        </div>
      </Form>
    )
  }
}
