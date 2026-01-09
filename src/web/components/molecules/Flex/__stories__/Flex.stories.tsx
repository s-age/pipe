import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Flex } from '../index'

const Meta = {
  title: 'Molecules/Flex',
  component: Flex,
  tags: ['autodocs'],
  argTypes: {
    gap: {
      control: 'select',
      options: ['s', 'm', 'l', 'xl', 'none']
    },
    align: {
      control: 'select',
      options: ['start', 'center', 'end', 'baseline', 'stretch']
    },
    justify: {
      control: 'select',
      options: ['start', 'center', 'end', 'between', 'around']
    }
  }
} satisfies StoryMeta<typeof Flex>

export default Meta

type Story = StoryObj<typeof Meta>

const Box = ({ children }: { children: string }): JSX.Element => (
  <div
    style={{
      padding: '1rem',
      backgroundColor: '#eee',
      border: '1px solid #ccc',
      borderRadius: '4px'
    }}
  >
    {children}
  </div>
)

export const Default: Story = {
  args: {
    children: (
      <>
        <Box>Item 1</Box>
        <Box>Item 2</Box>
        <Box>Item 3</Box>
      </>
    ),
    gap: 'm'
  }
}

export const AlignAndJustify: Story = {
  args: {
    children: (
      <>
        <Box>Item 1</Box>
        <Box>Item 2</Box>
      </>
    ),
    gap: 'l',
    align: 'center',
    justify: 'between',
    style: { height: '200px', border: '1px dashed #ccc' }
  }
}

export const Wrap: Story = {
  args: {
    children: Array.from({ length: 10 }).map((_, i) => (
      <Box key={i}>{`Item ${i + 1}`}</Box>
    )),
    gap: 's',
    wrap: true
  }
}
