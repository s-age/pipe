import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'

import { Select } from '../index'

const Meta = {
  title: 'Atoms/Select',
  component: Select,
  tags: ['autodocs'],
} satisfies StoryMeta<typeof Select>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    options: ['Apple', 'Banana', 'Cherry'],
    placeholder: 'Choose a fruit',
    name: 'fruit',
  },
}

export const Searchable: Story = {
  args: {
    options: ['Apricot', 'Blueberry', 'Cantaloupe', 'Durian', 'Elderberry'],
    searchable: true,
    placeholder: 'Search fruits',
    name: 'searchFruit',
  },
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form onSubmit={(data) => console.log('submit', data)}>
        <Select
          name="favorite"
          options={[
            { value: 'a', label: 'Option A' },
            { value: 'b', label: 'Option B' },
          ]}
        />
        <button type="submit">Submit</button>
      </Form>
    )

    return <FormExample />
  },
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
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <PlainExample />
  },
}
