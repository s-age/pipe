import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { ScrollArea } from '../index'

const Meta = {
  title: 'Molecules/ScrollArea',
  component: ScrollArea,
  tags: ['autodocs'],
  argTypes: {
    direction: {
      control: 'select',
      options: ['vertical', 'horizontal', 'both']
    }
  }
} satisfies StoryMeta<typeof ScrollArea>

export default Meta

type Story = StoryObj<typeof Meta>

const Box = ({
  width,
  height,
  color
}: {
  width: string | number
  height: string | number
  color: string
}): JSX.Element => (
  <div
    style={{
      width,
      height,
      backgroundColor: color,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontWeight: 'bold'
    }}
  >
    {width} x {height}
  </div>
)

export const Vertical: Story = {
  render: (arguments_) => (
    <div style={{ height: '200px', border: '1px solid #ccc' }}>
      <ScrollArea {...arguments_} />
    </div>
  ),
  args: {
    direction: 'vertical',
    children: (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <Box width="100%" height="150px" color="#3b82f6" />
        <Box width="100%" height="150px" color="#10b981" />
        <Box width="100%" height="150px" color="#f59e0b" />
      </div>
    )
  }
}

export const Horizontal: Story = {
  render: (arguments_) => (
    <div style={{ width: '300px', border: '1px solid #ccc' }}>
      <ScrollArea {...arguments_} />
    </div>
  ),
  args: {
    direction: 'horizontal',
    children: (
      <div style={{ display: 'flex', gap: '10px', width: 'max-content' }}>
        <Box width="200px" height="100px" color="#3b82f6" />
        <Box width="200px" height="100px" color="#10b981" />
        <Box width="200px" height="100px" color="#f59e0b" />
      </div>
    )
  }
}

export const Both: Story = {
  render: (arguments_) => (
    <div style={{ width: '300px', height: '200px', border: '1px solid #ccc' }}>
      <ScrollArea {...arguments_} />
    </div>
  ),
  args: {
    direction: 'both',
    children: (
      <div style={{ width: '600px', height: '400px', position: 'relative' }}>
        <Box width="100%" height="100%" color="#6366f1" />
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: 'white',
            fontSize: '24px'
          }}
        >
          Large Content
        </div>
      </div>
    )
  }
}
