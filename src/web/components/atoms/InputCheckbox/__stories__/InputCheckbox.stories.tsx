import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'

import { InputCheckbox } from '../index'

export default {}
export const Meta = {
  title: 'Atoms/InputCheckbox',
  component: InputCheckbox,
  tags: ['autodocs']
} satisfies StoryMeta<typeof InputCheckbox>

// Storybook meta is exported as a named export to comply with import/no-default-export
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    label: 'Check me',
    id: 'cb-default'
  }
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form onSubmit={(data) => console.log('submit', data)}>
        <InputCheckbox name="apple" label="Apple" />
        <InputCheckbox name="banana" label="Banana" />
        <button type="submit">Submit</button>
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
          <InputCheckbox name="plainApple" label="Apple" />
          <br />
          <InputCheckbox name="plainBanana" label="Banana" />
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <PlainExample />
  }
}
