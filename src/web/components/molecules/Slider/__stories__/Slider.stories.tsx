import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { useState } from 'react'
import { expect, fireEvent, fn, within } from 'storybook/test'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'

import { Slider } from '../index'

const Meta = {
  title: 'Molecules/Slider',
  component: Slider,
  tags: ['autodocs'],
  args: {
    'aria-label': 'Slider label',
    min: 0,
    max: 100,
    step: 1
  }
} satisfies StoryMeta<typeof Slider>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    defaultValue: 50
  },
  render: (arguments_): JSX.Element => (
    <div style={{ width: 360 }}>
      <Slider {...arguments_} />
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')
    await expect(slider).toHaveValue('50')
  }
}

export const Controlled: Story = {
  args: {
    onChange: fn()
  },
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState(30)

      const handleChange = (v: number): void => {
        setValue(v)
        arguments_.onChange?.(v)
      }

      return (
        <div style={{ width: 360 }}>
          <Slider {...arguments_} value={value} onChange={handleChange} />
          <div style={{ marginTop: 16 }}>Current Value: {value}</div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')

    // Simulate value change using fireEvent
    fireEvent.change(slider, { target: { value: '50' } })

    await expect(args.onChange).toHaveBeenCalled()
  }
}

export const WithRHF: Story = {
  render: (arguments_): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <div style={{ width: 360 }}>
          <Slider {...arguments_} name="volume" defaultValue={25} />
        </div>
        <div style={{ marginTop: 16 }}>
          <Button type="submit">Submit</Button>
        </div>
      </Form>
    )

    return <FormExample />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')
    await expect(slider).toHaveValue('25')
  }
}

export const Disabled: Story = {
  args: {
    disabled: true,
    defaultValue: 75
  },
  render: (arguments_): JSX.Element => (
    <div style={{ width: 360 }}>
      <Slider {...arguments_} />
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')
    await expect(slider).toBeDisabled()
  }
}

export const CustomStep: Story = {
  args: {
    min: 0,
    max: 10,
    step: 2,
    defaultValue: 4
  },
  render: (arguments_): JSX.Element => (
    <div style={{ width: 360 }}>
      <Slider {...arguments_} />
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')
    await expect(slider).toHaveAttribute('step', '2')
    await expect(slider).toHaveValue('4')
  }
}
