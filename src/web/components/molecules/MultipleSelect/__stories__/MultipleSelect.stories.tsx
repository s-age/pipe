import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'

import { MultipleSelect } from '../index'

const Meta = {
  title: 'Molecules/MultipleSelect',
  component: MultipleSelect,
  tags: ['autodocs']
} satisfies StoryMeta<typeof MultipleSelect>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    options: ['Apple', 'Banana', 'Cherry'],
    placeholder: 'Choose fruits',
    name: 'fruits'
  }
}

export const Searchable: Story = {
  args: {
    options: ['Apricot', 'Blueberry', 'Cantaloupe', 'Durian', 'Elderberry'],
    searchable: true,
    placeholder: 'Search fruits',
    name: 'searchFruits'
  }
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <MultipleSelect
          name="favorites"
          options={[
            { value: 'a', label: 'Option A' },
            { value: 'b', label: 'Option B' },
            { value: 'c', label: 'Option C' }
          ]}
        />
        <Button type="submit" onClick={(data) => console.log('submit', data)}>
          Submit
        </Button>
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
          <MultipleSelect name="plainFruits" options={['One', 'Two', 'Three']} />
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <PlainExample />
  }
}
