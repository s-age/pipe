import { zodResolver } from '@hookform/resolvers/zod'
import type { Meta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { z } from 'zod'

import { Form, useFormContext } from '../index'

const meta = {
  title: 'Organisms/Form',
  component: Form,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {},
} satisfies Meta<typeof Form>

export default meta
type Story = StoryObj<typeof meta>

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
})

type FormData = z.infer<typeof schema>

const MyFormContent = (): JSX.Element => {
  const {
    register,
    formState: { errors },
  } = useFormContext<FormData>()

  return (
    <div>
      <div>
        <label htmlFor="name">Name:</label>
        <input id="name" {...register('name')} />
        {errors.name && <p>{errors.name.message}</p>}
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input id="email" type="email" {...register('email')} />
        {errors.email && <p>{errors.email.message}</p>}
      </div>
      <button type="submit">Submit</button>
    </div>
  )
}

export const Default: Story = {
  render: (arguments_): JSX.Element => (
    <Form {...arguments_}>
      <MyFormContent />
    </Form>
  ),
  args: {
    onSubmit: (data) => console.log(data),
    resolver: zodResolver(schema),
    children: <MyFormContent />,
  },
}
