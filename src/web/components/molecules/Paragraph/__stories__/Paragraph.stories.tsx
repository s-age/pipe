import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Paragraph } from '../index'

const Meta = {
  title: 'Molecules/Paragraph',
  component: Paragraph,
  tags: ['autodocs'],
  args: {
    children:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
  }
} satisfies StoryMeta<typeof Paragraph>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    align: 'left',
    size: 'm',
    variant: 'default',
    weight: 'normal'
  }
}

export const Variants: Story = {
  render: (arguments_) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Paragraph {...arguments_} variant="default">
        Default Variant: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} variant="muted">
        Muted Variant: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} variant="error">
        Error Variant: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} variant="success">
        Success Variant: {arguments_.children}
      </Paragraph>
    </div>
  )
}

export const SizesAndWeights: Story = {
  render: (arguments_) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Paragraph {...arguments_} size="xs" weight="normal">
        XS Normal: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} size="s" weight="medium">
        S Medium: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} size="m" weight="semibold">
        M Semibold: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} size="l" weight="bold">
        L Bold: {arguments_.children}
      </Paragraph>
      <Paragraph {...arguments_} size="xl" weight="bold">
        XL Bold: {arguments_.children}
      </Paragraph>
    </div>
  )
}
