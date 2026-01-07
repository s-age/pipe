import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import React, { useState } from 'react'
import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'

import { TextArea } from '../index'

const Meta = {
  title: 'Atoms/TextArea',
  component: TextArea,
  tags: ['autodocs']
} satisfies StoryMeta<typeof TextArea>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    placeholder: 'Write something…',
    name: 'notes',
    rows: 4,
    'aria-label': 'Notes'
  }
}

export const Controlled: Story = {
  render: (): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState('initial text')

      return (
        <div>
          <TextArea
            value={value}
            onChange={(v: string) => setValue(v)}
            rows={6}
            aria-label="Controlled textarea"
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
        <TextArea name="comments" rows={4} aria-label="Comments" aria-required={true} />
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
          <TextArea name="plainNotes" rows={4} aria-label="Plain notes" />
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <PlainExample />
  }
}
