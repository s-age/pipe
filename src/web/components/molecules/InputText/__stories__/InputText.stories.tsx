import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import React, { useState } from 'react'
import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'

import { InputText } from '../index'

const Meta = {
  title: 'Molecules/InputText',
  component: InputText,
  tags: ['autodocs']
} satisfies StoryMeta<typeof InputText>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    placeholder: 'Type here…',
    name: 'simpleText',
    'aria-label': 'Simple text input'
  }
}

export const Controlled: Story = {
  render: (): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState('hello')

      return (
        <div>
          <InputText
            value={value}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
              setValue(event.target.value)
            }
            aria-label="Controlled text input"
          />
          <div style={{ marginTop: 8 }}>Current: {value}</div>
        </div>
      )
    }

    return <ControlledExample />
  }
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <InputText
          name="firstName"
          placeholder="First name"
          aria-label="First name"
          aria-required={true}
        />
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
          <InputText
            name="plainInput"
            placeholder="Plain input"
            aria-label="Plain text input"
          />
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <PlainExample />
  }
}
