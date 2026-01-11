import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { ScrollArea } from '@/components/molecules/ScrollArea'

import { Text } from '../index'

const Meta = {
  title: 'Atoms/Text',
  component: Text,
  tags: ['autodocs'],
  argTypes: {
    align: {
      control: 'select',
      options: ['left', 'center', 'right', 'justify']
    },
    size: {
      control: 'select',
      options: ['xs', 's', 'm', 'l', 'xl']
    },
    variant: {
      control: 'select',
      options: ['default', 'muted', 'error', 'success']
    },
    weight: {
      control: 'select',
      options: ['normal', 'medium', 'semibold', 'bold']
    }
  }
} satisfies StoryMeta<typeof Text>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'The quick brown fox jumps over the lazy dog'
  }
}

export const Variants: Story = {
  render: (): JSX.Element => (
    <ScrollArea height="320px">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <h4 style={{ marginBottom: '8px', color: '#666' }}>Sizes</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Text size="xs">Extra Small Text (xs)</Text>
            <Text size="s">Small Text (s)</Text>
            <Text size="m">Medium Text (m - Default)</Text>
            <Text size="l">Large Text (l)</Text>
            <Text size="xl">Extra Large Text (xl)</Text>
          </div>
        </div>

        <div>
          <h4 style={{ marginBottom: '8px', color: '#666' }}>Weights</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Text weight="normal">Normal Weight</Text>
            <Text weight="medium">Medium Weight</Text>
            <Text weight="semibold">Semibold Weight</Text>
            <Text weight="bold">Bold Weight</Text>
          </div>
        </div>

        <div>
          <h4 style={{ marginBottom: '8px', color: '#666' }}>Variants</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Text variant="default">Default Variant</Text>
            <Text variant="muted">Muted Variant</Text>
            <Text variant="success">Success Variant</Text>
            <Text variant="error">Error Variant</Text>
          </div>
        </div>

        <div>
          <h4 style={{ marginBottom: '8px', color: '#666' }}>Alignment</h4>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              width: '300px',
              border: '1px solid #eee'
            }}
          >
            <Text align="left">Left Aligned</Text>
            <Text align="center">Center Aligned</Text>
            <Text align="right">Right Aligned</Text>
            <Text align="justify">
              Justify Aligned: This is a longer text to demonstrate the justification
              alignment property of the Text component.
            </Text>
          </div>
        </div>
      </div>
    </ScrollArea>
  )
}

export const Truncate: Story = {
  args: {
    children:
      'This is a very long text that should be truncated when the truncate prop is set to true and the container is narrow.',
    truncate: true
  },
  render: (arguments_): JSX.Element => (
    <div style={{ width: '200px', border: '1px solid #eee', padding: '8px' }}>
      <Text {...arguments_} />
    </div>
  )
}
