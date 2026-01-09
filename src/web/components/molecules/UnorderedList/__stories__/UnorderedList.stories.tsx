import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { UnorderedList } from '../index'

const Meta = {
  title: 'Molecules/UnorderedList',
  component: UnorderedList,
  tags: ['autodocs'],
  argTypes: {
    gap: {
      control: 'select',
      options: ['none', 's', 'm', 'l', 'xl']
    },
    marker: {
      control: 'select',
      options: ['none', 'disc', 'circle', 'square']
    }
  }
} satisfies StoryMeta<typeof UnorderedList>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: (
      <>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
      </>
    )
  }
}

export const WithMarkers: Story = {
  args: {
    marker: 'disc',
    children: (
      <>
        <li>Disc Marker Item 1</li>
        <li>Disc Marker Item 2</li>
        <li>Disc Marker Item 3</li>
      </>
    )
  }
}

export const WithGaps: Story = {
  args: {
    gap: 'm',
    children: (
      <>
        <li>Gap Medium Item 1</li>
        <li>Gap Medium Item 2</li>
        <li>Gap Medium Item 3</li>
      </>
    )
  }
}

export const SquareMarkerLargeGap: Story = {
  args: {
    marker: 'square',
    gap: 'l',
    children: (
      <>
        <li>Square Marker Large Gap 1</li>
        <li>Square Marker Large Gap 2</li>
        <li>Square Marker Large Gap 3</li>
      </>
    )
  }
}
