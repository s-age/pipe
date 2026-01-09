import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { FlexColumn } from '../index'

const Meta = {
  title: 'Molecules/FlexColumn',
  component: FlexColumn,
  tags: ['autodocs'],
  argTypes: {
    gap: {
      control: 'select',
      options: ['s', 'm', 'l', 'xl', 'none']
    },
    align: {
      control: 'select',
      options: ['start', 'center', 'end', 'stretch']
    },
    justify: {
      control: 'select',
      options: ['start', 'center', 'end', 'between', 'around']
    }
  }
} satisfies StoryMeta<typeof FlexColumn>

export default Meta

type Story = StoryObj<typeof Meta>

const Box = ({ children }: { children: string }): JSX.Element => (
  <div
    style={{
      padding: '1rem',
      backgroundColor: '#f0f0f0',
      border: '1px solid #ccc',
      textAlign: 'center'
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

export const Alignment: Story = {
  args: {
    children: (
      <>
        <Box>Short</Box>
        <Box>Much longer item content</Box>
        <Box>Medium item</Box>
      </>
    ),
    align: 'center',
    gap: 's'
  }
}
