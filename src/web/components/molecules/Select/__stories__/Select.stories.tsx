import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'

import { Select } from '../index'

const Meta = {
  title: 'Molecules/Select',
  component: Select,
  tags: ['autodocs']
} satisfies StoryMeta<typeof Select>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    options: ['Apple', 'Banana', 'Cherry'],
    placeholder: 'Choose a fruit',
    name: 'fruit'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /choose a fruit/i })
    await expect(trigger).toBeInTheDocument()

    await userEvent.click(trigger)
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    const options = within(listbox).getAllByRole('option')
    await expect(options).toHaveLength(3)
    await expect(options[0]).toHaveTextContent('Apple')
    await expect(options[1]).toHaveTextContent('Banana')
    await expect(options[2]).toHaveTextContent('Cherry')
  }
}

export const Searchable: Story = {
  args: {
    options: ['Apricot', 'Blueberry', 'Cantaloupe', 'Durian', 'Elderberry'],
    searchable: true,
    placeholder: 'Search fruits',
    name: 'searchFruit'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /search fruits/i })
    await userEvent.click(trigger)

    const searchInput = await canvas.findByLabelText(/search options/i)
    await expect(searchInput).toBeInTheDocument()

    await userEvent.type(searchInput, 'Blue')

    const listbox = canvas.getByRole('listbox')
    const visibleOptions = within(listbox).getAllByRole('option')
    await expect(visibleOptions).toHaveLength(1)
    await expect(visibleOptions[0]).toHaveTextContent('Blueberry')
  }
}

export const Disabled: Story = {
  args: {
    options: ['One', 'Two'],
    disabled: true,
    placeholder: 'Disabled select'
  }
}

export const Controlled: Story = {
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState<string | undefined>(undefined)

      return (
        <div>
          <Select
            {...arguments_}
            value={value}
            onChange={(event) => setValue(event.target.value)}
          />
          <div style={{ marginTop: 16 }}>Selected: {value ?? 'None'}</div>
        </div>
      )
    }

    return <ControlledExample />
  },
  args: {
    options: ['Red', 'Green', 'Blue'],
    placeholder: 'Select a color'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /select a color/i })
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const option = within(listbox).getByRole('option', { name: /green/i })
    await userEvent.click(option)

    // Wait for listbox to close
    await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()

    // Verify the selected value is displayed
    const selectedText = await canvas.findByText(/selected:/i)
    await expect(selectedText).toHaveTextContent('Selected: Green')
  }
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <Select
          name="favorite"
          options={[
            { value: 'a', label: 'Option A' },
            { value: 'b', label: 'Option B' }
          ]}
        />
        <Button type="submit">Submit</Button>
      </Form>
    )

    return <FormExample />
  }
}

export const WithoutForm: Story = {
  render: (): JSX.Element => {
    const PlainExample = (): JSX.Element => {
      const handleSubmit = (event: React.FormEvent<HTMLFormElement>): void => {
        event.preventDefault()
        const fd = new FormData(event.currentTarget)
        const data = Object.fromEntries(fd.entries())
        console.log('submit plain', data)
      }

      return (
        <form onSubmit={handleSubmit}>
          <Select name="plainFruit" options={['One', 'Two', 'Three']} />
          <button type="submit" style={{ marginTop: 8 }}>
            Submit
          </button>
        </form>
      )
    }

    return <PlainExample />
  }
}
