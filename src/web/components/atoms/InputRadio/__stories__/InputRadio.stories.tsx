import type { Meta, StoryObj } from '@storybook/react'
import InputRadio from '../index'
import { Form } from '@/components/organisms/Form'

const meta = {
  title: 'Atoms/InputRadio',
  component: InputRadio,
  tags: ['autodocs'],
} satisfies Meta<typeof InputRadio>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    label: 'Option A',
    id: 'radio-default-a',
    value: 'A',
    name: 'radio-default',
  },
}

export const WithRHF: Story = {
  render: () => {
    const FormExample = () => {
      return (
        <Form onSubmit={(data) => console.log('submit', data)}>
          <InputRadio name="option" value="A" label="A" />
          <InputRadio name="option" value="B" label="B" />
          <button type="submit">Submit</button>
        </Form>
      )
    }
    return <FormExample />
  },
}

export const WithoutForm: Story = {
  render: () => {
    const PlainExample = () => {
      const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        const fd = new FormData(e.currentTarget)
        const data = Object.fromEntries(fd.entries())
        // eslint-disable-next-line no-console
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
  },
}
