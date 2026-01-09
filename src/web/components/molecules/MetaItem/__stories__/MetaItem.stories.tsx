import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { MetaItem, MetaLabel } from '../index'

const Meta = {
  title: 'Molecules/MetaItem',
  component: MetaItem,
  tags: ['autodocs']
} satisfies StoryMeta<typeof MetaItem>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default usage of MetaItem with MetaLabel.
 */
export const Default: Story = {
  render: (): JSX.Element => (
    <MetaItem>
      <MetaLabel>Label</MetaLabel>
      <div>Content area</div>
    </MetaItem>
  )
}

/**
 * MetaItem with a required MetaLabel.
 */
export const Required: Story = {
  render: (): JSX.Element => (
    <MetaItem>
      <MetaLabel required={true}>Required Label</MetaLabel>
      <div>Content area</div>
    </MetaItem>
  )
}

/**
 * Standalone MetaLabel.
 */
export const LabelOnly: Story = {
  render: (): JSX.Element => <MetaLabel>Standalone Label</MetaLabel>
}

/**
 * Standalone MetaLabel with required mark.
 */
export const RequiredLabelOnly: Story = {
  render: (): JSX.Element => (
    <MetaLabel required={true}>Standalone Required Label</MetaLabel>
  )
}
