import { zodResolver } from '@hookform/resolvers/zod'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'

import { Button } from '@/components/atoms/Button'

import { Form, useFormContext } from '../index'
import { schema } from './schema'
import type { FormData } from './schema'

const MyFormContent = ({
  handleSubmit
}: {
  handleSubmit: () => void
}): React.JSX.Element => {
  const {
    formState: { errors },
    register
  } = useFormContext<FormData>()

  return (
    <div>
      <input data-testid="name-input" {...register('name')} />
      {errors.name && <p data-testid="name-error">{errors.name.message}</p>}
      <input data-testid="email-input" type="email" {...register('email')} />
      {errors.email && <p data-testid="email-error">{errors.email.message}</p>}
      <Button type="submit" data-testid="submit-button" onSubmit={handleSubmit}>
        Submit
      </Button>
    </div>
  )
}

describe('Form', () => {
  const handleSubmit = jest.fn()

  it('renders and submits successfully with valid data', async () => {
    render(
      <Form resolver={zodResolver(schema)}>
        <MyFormContent handleSubmit={handleSubmit} />
      </Form>
    )

    fireEvent.change(screen.getByTestId('name-input'), {
      target: { value: 'John Doe' }
    })
    fireEvent.change(screen.getByTestId('email-input'), {
      target: { value: 'john.doe@example.com' }
    })
    fireEvent.click(screen.getByTestId('submit-button'))

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith(
        {
          name: 'John Doe',
          email: 'john.doe@example.com'
        },
        expect.anything()
      )
    })
    expect(screen.queryByTestId('name-error')).not.toBeInTheDocument()
    expect(screen.queryByTestId('email-error')).not.toBeInTheDocument()
  })

  it('shows validation errors with invalid data', async () => {
    render(
      <Form resolver={zodResolver(schema)}>
        <MyFormContent handleSubmit={handleSubmit} />
      </Form>
    )

    fireEvent.change(screen.getByTestId('name-input'), { target: { value: '' } })
    fireEvent.change(screen.getByTestId('email-input'), {
      target: { value: 'invalid-email' }
    })
    fireEvent.click(screen.getByTestId('submit-button'))

    await waitFor(() => {
      expect(screen.getByTestId('name-error')).toHaveTextContent('Name is required')
      expect(screen.getByTestId('email-error')).toHaveTextContent(
        'Invalid email address'
      )
    })
    expect(handleSubmit).not.toHaveBeenCalled()
  })
})
