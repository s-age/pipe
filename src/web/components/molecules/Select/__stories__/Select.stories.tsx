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

export const CloseAndClearHighlight: Story = {
  args: {
    options: ['First', 'Second', 'Third'],
    name: 'test-select',
    searchable: false
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')

    await userEvent.click(trigger)
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    const firstOption = within(listbox).getByRole('option', { name: /first/i })
    await userEvent.click(firstOption)

    await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()
  }
}

/**
 * Tests outside click to trigger close and clearHighlight (lines 85-86 coverage).
 */
export const OutsideClick: Story = {
  args: {
    options: ['Alpha', 'Beta', 'Gamma'],
    name: 'outside-test',
    searchable: false
  },
  render: (arguments_): JSX.Element => (
    <div>
      <div
        id="outside-area"
        style={{ marginBottom: '1rem', padding: '1rem', background: '#eee' }}
      >
        Click here after opening
      </div>
      <Select {...arguments_} />
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')

    // Open the select
    await userEvent.click(trigger)
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    // Hover to highlight an option
    const firstOption = within(listbox).getByRole('option', { name: /alpha/i })
    await userEvent.hover(firstOption)

    // Click outside to trigger close and clearHighlight
    const outsideArea = canvas.getByText(/click here after opening/i)
    await userEvent.click(outsideArea)

    // Verify listbox is closed
    await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()
  }
}

/**
 * Tests fallback to native select when no options and not searchable (line 97-98 coverage).
 */
export const NativeSelectFallback: Story = {
  args: {
    name: 'native-fallback',
    searchable: false,
    options: undefined
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const nativeSelect = canvas.getByRole('combobox')
    await expect(nativeSelect).toBeInTheDocument()
    await expect(nativeSelect.tagName.toLowerCase()).toBe('select')
  }
}

/**
 * Tests displayLabel computation (line 102 coverage).
 * This covers the displayLabel = selectedLabel ?? placeholder ?? 'Select an option...' line.
 * When an option is selected, displayLabel should show the selected label.
 */
export const DisplayLabelCoverage: Story = {
  args: {
    name: 'display-label',
    options: [
      { value: 'a', label: 'Option A' },
      { value: 'b', label: 'Option B' }
    ],
    placeholder: 'Choose an option'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')

    // Initially should show placeholder
    await expect(trigger).toHaveTextContent('Choose an option')

    // Click to open
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const optionA = within(listbox).getByRole('option', { name: /option a/i })

    // Click option to select it
    await userEvent.click(optionA)

    // After selection, displayLabel should show the selected label
    await expect(trigger).toHaveTextContent('Option A')
  }
}

/**
 * Tests options with disabled and non-string labels (lines 116-117, 171-173, 177-179 coverage).
 */
export const DisabledOptions: Story = {
  args: {
    name: 'disabled-options',
    options: [
      { value: 'enabled', label: 'Enabled Option' },
      { value: 'disabled', label: 'Disabled Option', disabled: true },
      { value: 'number-label', label: 42 as unknown as string }
    ]
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const options = within(listbox).getAllByRole('option')

    await expect(options).toHaveLength(3)
    await expect(options[1]).toHaveAttribute('aria-disabled', 'true')

    // Try to click disabled option (should not trigger handleOptionClick)
    await userEvent.click(options[1])

    // Try to hover disabled option (should not trigger handleMouseEnter)
    await userEvent.hover(options[1])
    await userEvent.unhover(options[1])
  }
}

/**
 * Tests when name is undefined (line 90 coverage).
 */
export const NoName: Story = {
  args: {
    name: undefined,
    options: ['A', 'B', 'C']
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toHaveAttribute('id', 'select-listbox')
  }
}

/**
 * Tests options with empty/null values for key generation (line 168 coverage).
 */
export const EmptyOptionValues: Story = {
  args: {
    name: 'empty-values',
    options: [
      { value: '', label: 'Empty Value', id: 'empty-id' },
      { value: 'normal', label: 'Normal Value' }
    ]
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const options = within(listbox).getAllByRole('option')
    await expect(options).toHaveLength(2)
  }
}
