import type { Meta, StoryObj } from '@storybook/react'
import InputCheckbox from '../index'
import { Form } from '@/components/organisms/Form'

const meta = {
  title: 'Atoms/InputCheckbox',
  component: InputCheckbox,
  tags: ['autodocs'],
} satisfies Meta<typeof InputCheckbox>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    label: 'Check me',
    id: 'cb-default',
  },
}

export const WithRHF: Story = {
  render: () => {
    const FormExample = () => {
      return (
        <Form onSubmit={(data) => console.log('submit', data)}>
          <InputCheckbox name="apple" label="Apple" />
          <InputCheckbox name="banana" label="Banana" />
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
          <InputCheckbox name="plainApple" label="Apple" />
          <br />
          <InputCheckbox name="plainBanana" label="Banana" />
          <button type="submit">Submit</button>
        </form>
      )
    }
    return <PlainExample />
  },
}
