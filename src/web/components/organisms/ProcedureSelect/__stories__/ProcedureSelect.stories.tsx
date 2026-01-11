import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'
import { z } from 'zod'

import { Button } from '@/components/atoms/Button'
import { Form, useFormContext } from '@/components/organisms/Form'
import { fsHandlers } from '@/msw/resources/fs'

import { ProcedureSelect } from '../index'

const Meta = {
  title: 'Organisms/ProcedureSelect',
  component: ProcedureSelect,
  tags: ['autodocs'],
  args: {
    placeholder: 'Select procedure'
  }
} satisfies StoryMeta<typeof ProcedureSelect>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state without form context
 */
export const Default: Story = {}

/**
 * Integrated with React Hook Form
 */
export const WithRHF: Story = {
  render: (arguments_) => (
    <Form defaultValues={{ procedure: 'proc-1' }}>
      <ProcedureSelect {...arguments_} />
    </Form>
  )
}

/**
 * Demonstrates error display (line 44 coverage).
 */
export const WithError: Story = {
  render: (arguments_): JSX.Element => {
    const FormWithError = (): JSX.Element => {
      const methods = useFormContext()

      const handleSubmit = async (): Promise<void> => {
        await methods.trigger('procedure')
      }

      return (
        <>
          <ProcedureSelect {...arguments_} />
          <Button type="button" onClick={handleSubmit}>
            Trigger Validation
          </Button>
        </>
      )
    }

    const schema = z.object({
      procedure: z.string().min(1, 'Procedure is required')
    })

    return (
      <Form schema={schema} defaultValues={{ procedure: '' }}>
        <FormWithError />
      </Form>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /trigger validation/i })
    await userEvent.click(button)

    const errorMessage = await canvas.findByText(/procedure is required/i)
    await expect(errorMessage).toBeInTheDocument()
  }
}

/**
 * Interactive story demonstrating API fetch and selection
 */
export const Interaction: Story = {
  parameters: {
    msw: {
      handlers: fsHandlers
    }
  },
  render: (arguments_) => (
    <Form defaultValues={{ procedure: '' }}>
      <ProcedureSelect {...arguments_} />
    </Form>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('combobox')

    // Focus to trigger fetch
    await userEvent.click(input)

    // Type to trigger suggestions
    await userEvent.type(input, 'Proc')

    // Wait for the procedure options to appear in the listbox
    const listbox = await canvas.findByRole('listbox', {}, { timeout: 3000 })
    await expect(listbox).toBeInTheDocument()

    // Find and click the option
    const option = within(listbox).getByText('Procedure 2')
    await userEvent.click(option)

    // Wait for selection to be applied - the option text should still be visible in the selected tag
    const selectedTag = await canvas.findByText('proc-2', {}, { timeout: 2000 })
    await expect(selectedTag).toBeInTheDocument()
  }
}
