import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import React, { useState } from 'react'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'

import { Slider } from '../index'

const Meta = {
  title: 'Atoms/Slider',
  component: Slider,
  tags: ['autodocs']
} satisfies StoryMeta<typeof Slider>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const [v, setV] = useState(40)

      return (
        <div style={{ width: 360 }}>
          <Slider
            value={v}
            onChange={(value: number) => setV(value)}
            min={0}
            max={100}
          />
        </div>
      )
    }

    return <Example />
  }
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => (
      <Form>
        <div style={{ width: 360 }}>
          <Slider name="volume" defaultValue={25} min={0} max={100} />
        </div>
        <Button type="submit" onClick={(data) => console.log('submit', data)}>
          Submit
        </Button>
      </Form>
    )

    return <Example />
  }
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
  }
}
