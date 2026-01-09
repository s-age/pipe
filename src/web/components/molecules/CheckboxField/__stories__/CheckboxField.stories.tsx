import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { z } from 'zod'

import { Form } from '@/components/organisms/Form'

import { CheckboxField } from '../index'

const Meta = {
  title: 'Molecules/CheckboxField',
  component: CheckboxField,
  tags: ['autodocs'],
  args: {
    id: 'checkbox',
    label: 'Checkbox Label',
    name: 'checkbox'
  }
} satisfies StoryMeta<typeof CheckboxField>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default usage of CheckboxField within a Form context.
 */
export const Default: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form defaultValues={{ terms: false }}>
        <CheckboxField
          id="terms"
          name="terms"
          label="I agree to the terms and conditions"
        />
      </Form>
    )

    return <FormExample />
  }
}

/**
 * CheckboxField with validation.
 * In this example, the checkbox must be checked to pass validation.
 */
export const WithValidation: Story = {
  render: (): JSX.Element => {
    const schema = z.object({
      requiredCheck: z.literal(true, {
        errorMap: () => ({ message: 'You must check this box' })
      })
    })

    const FormExample = (): JSX.Element => (
      <Form schema={schema} defaultValues={{ requiredCheck: false }}>
        <CheckboxField
          id="required_check"
          name="required_check"
          label="Required agreement"
        />
        <div style={{ marginTop: '1rem' }}>
          <button type="submit">Submit to see validation</button>
        </div>
      </Form>
    )

    return <FormExample />
  }
}
