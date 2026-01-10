import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import { expect, userEvent, within } from 'storybook/test'

import { Form } from '@/components/organisms/Form'
import { API_BASE_URL } from '@/constants/uri'

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
 * Interactive story demonstrating API fetch and selection
 */
export const Interaction: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get(`${API_BASE_URL}/fs/procedures`, () =>
          HttpResponse.json({
            procedures: [
              { label: 'Procedure 1', value: 'proc-1' },
              { label: 'Procedure 2', value: 'proc-2' },
              { label: 'Procedure 3', value: 'proc-3' }
            ]
          })
        )
      ]
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
