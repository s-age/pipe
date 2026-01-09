import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { fn } from 'storybook/test'

import { ConfirmModal } from '../index'

const Meta = {
  title: 'Molecules/ConfirmModal',
  component: ConfirmModal,
  tags: ['autodocs'],
  args: {
    onCancel: fn(),
    onConfirm: fn()
  }
} satisfies StoryMeta<typeof ConfirmModal>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed with this action?'
  }
}

export const WithIcon: Story = {
  args: {
    title: 'Delete Item',
    message: 'This action cannot be undone. Are you sure?',
    icon: <span>⚠️</span>,
    confirmText: 'Delete'
  }
}

export const CustomLabels: Story = {
  args: {
    title: 'Save Changes',
    message: 'Do you want to save the changes you made?',
    cancelText: 'Discard',
    confirmText: 'Save'
  }
}

export const LongMessage: Story = {
  args: {
    title: 'Terms and Conditions',
    message:
      'Please read the following terms and conditions carefully before proceeding. By clicking OK, you agree to be bound by these terms. This is a very long message intended to test how the modal content handles overflow and wrapping in the UI.'
  }
}
