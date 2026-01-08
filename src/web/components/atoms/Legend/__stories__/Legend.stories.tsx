import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Legend } from '../index'

const Meta = {
  title: 'Atoms/Legend',
  component: Legend,
  tags: ['autodocs'],
  args: {
    children: 'Form Legend'
  }
} satisfies StoryMeta<typeof Legend>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'Personal Information'
  }
}

export const VisuallyHidden: Story = {
  args: {
    children: 'Hidden Legend for Screen Readers',
    visuallyHidden: true
  }
}

export const LongText: Story = {
  args: {
    children:
      'This is a very long legend text to demonstrate how the component handles multiple lines of content within a fieldset context.'
  }
}
