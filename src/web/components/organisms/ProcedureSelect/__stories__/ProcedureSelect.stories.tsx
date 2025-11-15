import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { ProcedureSelect } from '../index'

const Meta = {
  title: 'Organisms/ProcedureSelect',
  component: ProcedureSelect,
  tags: ['autodocs']
} satisfies StoryMeta<typeof ProcedureSelect>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    placeholder: 'Select procedure'
  }
}
