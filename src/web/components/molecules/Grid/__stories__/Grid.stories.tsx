import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX, ReactNode } from 'react'

import { Grid } from '../index'

const Meta = {
  title: 'Molecules/Grid',
  component: Grid,
  tags: ['autodocs'],
  argTypes: {
    columns: {
      control: 'select',
      options: ['1', '2', '3', '4', 'auto-fit', 'auto-fill', '100px 1fr']
    },
    gap: {
      control: 'select',
      options: ['s', 'm', 'l', 'xl', 'none']
    }
  }
} satisfies StoryMeta<typeof Grid>

export default Meta

type Story = StoryObj<typeof Meta>

const Box = ({ children }: { children: ReactNode }): JSX.Element => (
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
        <Box>Item 4</Box>
      </>
    ),
    columns: '2',
    gap: 'm'
  }
}

export const Responsive: Story = {
  args: {
    children: (
      <>
        <Box>Item 1</Box>
        <Box>Item 2</Box>
        <Box>Item 3</Box>
        <Box>Item 4</Box>
        <Box>Item 5</Box>
        <Box>Item 6</Box>
      </>
    ),
    columns: 'auto-fit',
    gap: 's'
  },
  parameters: {
    docs: {
      description: {
        story:
          'Uses `auto-fit` to create a responsive grid that fills the available space.'
      }
    }
  }
}

export const CustomColumns: Story = {
  args: {
    children: (
      <>
        <Box>Sidebar</Box>
        <Box>Main Content</Box>
      </>
    ),
    columns: '200px 1fr',
    gap: 'l'
  },
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates custom grid template columns using a string value.'
      }
    }
  }
}
