import type { Meta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import React, { useState } from 'react'

import { Form } from '@/components/organisms/Form'

import Slider from '../index'

const meta = {
  title: 'Atoms/Slider',
  component: Slider,
  tags: ['autodocs'],
} satisfies Meta<typeof Slider>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const [v, setV] = useState(40)

      return (
        <div style={{ width: 360 }}>
          <Slider value={v} onChange={(value) => setV(value)} min={0} max={100} />
        </div>
      )
    }

    return <Example />
  },
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => (
      <Form onSubmit={(data) => console.log('submit', data)}>
        <div style={{ width: 360 }}>
          <Slider name="volume" defaultValue={25} min={0} max={100} />
        </div>
        <button type="submit">Submit</button>
      </Form>
    )

    return <Example />
  },
}

export const WithoutForm: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const handleSubmit = (event: React.FormEvent<HTMLFormElement>): void => {
        event.preventDefault()
        const fd = new FormData(event.currentTarget)
        const data = Object.fromEntries(fd.entries())

        console.log('submit plain', data)
      }

      return (
        <form onSubmit={handleSubmit}>
          <div style={{ width: 360 }}>
            <Slider name="plainVolume" defaultValue={50} min={0} max={100} />
          </div>
          <button type="submit">Submit</button>
        </form>
      )
    }

    return <Example />
  },
}
