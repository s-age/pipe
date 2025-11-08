import type { Meta, StoryObj } from '@storybook/react'
import React, { useState } from 'react'
import Slider from '../index'
import { Form } from '@/components/organisms/Form'

const meta = {
  title: 'Atoms/Slider',
  component: Slider,
  tags: ['autodocs'],
} satisfies Meta<typeof Slider>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => {
    const Example = () => {
      const [v, setV] = useState(40)
      return (
        <div style={{ width: 360 }}>
          <Slider value={v} onChange={(val) => setV(val)} min={0} max={100} />
        </div>
      )
    }
    return <Example />
  },
}

export const WithRHF: Story = {
  render: () => {
    const Example = () => {
      return (
        <Form onSubmit={(data) => console.log('submit', data)}>
          <div style={{ width: 360 }}>
            <Slider name="volume" defaultValue={25} min={0} max={100} />
          </div>
          <button type="submit">Submit</button>
        </Form>
      )
    }
    return <Example />
  },
}

export const WithoutForm: Story = {
  render: () => {
    const Example = () => {
      const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        const fd = new FormData(e.currentTarget)
        const data = Object.fromEntries(fd.entries())
        // eslint-disable-next-line no-console
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
