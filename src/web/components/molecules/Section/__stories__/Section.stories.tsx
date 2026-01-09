import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Section } from '../index'

const Meta = {
  title: 'Molecules/Section',
  component: Section,
  tags: ['autodocs'],
  args: {
    children: (
      <div
        style={{
          backgroundColor: '#f0f0f0',
          border: '1px dashed #ccc',
          padding: '1rem',
          textAlign: 'center'
        }}
      >
        Section Content
      </div>
    )
  }
} satisfies StoryMeta<typeof Section>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    padding: 'none'
  }
}

export const SmallPadding: Story = {
  args: {
    padding: 's'
  }
}

export const MediumPadding: Story = {
  args: {
    padding: 'm'
  }
}

export const LargePadding: Story = {
  args: {
    padding: 'l'
  }
}

export const CustomClassName: Story = {
  args: {
    className: 'custom-section',
    style: { border: '2px solid blue' }
  }
}
