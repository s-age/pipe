import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'

import { InputRadio } from '../index'

export default {}
export const Meta = {
  title: 'Atoms/InputRadio',
  component: InputRadio,
  tags: ['autodocs']
} satisfies StoryMeta<typeof InputRadio>

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    label: 'Option A',
    id: 'radio-default-a',
    value: 'A',
    name: 'radio-default'
  }
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <InputRadio name="option" value="A" label="A" />
        <InputRadio name="option" value="B" label="B" />
        <button type="submit" onClick={(data) => console.log('submit', data)}>
          Submit
        </button>
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
          <InputRadio name="plainOption" value="A" label="A" />
          <InputRadio name="plainOption" value="B" label="B" />
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <PlainExample />
  }
}
