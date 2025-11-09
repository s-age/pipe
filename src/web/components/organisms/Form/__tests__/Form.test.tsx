import { zodResolver } from '@hookform/resolvers/zod'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'

import { Form, useFormContext } from '../index'
import { schema } from './schema'
import type { FormData } from './schema'

const MyFormContent = (): React.JSX.Element => {
  const {
    register,
    formState: { errors }
  } = useFormContext<FormData>()

  return (
    <div>
      <input data-testid="name-input" {...register('name')} />
      {errors.name && <p data-testid="name-error">{errors.name.message}</p>}
      <input data-testid="email-input" type="email" {...register('email')} />
      {errors.email && <p data-testid="email-error">{errors.email.message}</p>}
      <button type="submit" data-testid="submit-button">
        Submit
      </button>
    </div>
  )
}

describe('Form', () => {
  it('renders and submits successfully with valid data', async () => {
    const handleSubmit = jest.fn()
    render(
      <Form onSubmit={handleSubmit} resolver={zodResolver(schema)}>
        <MyFormContent />
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
    const handleSubmit = jest.fn()
    render(
      <Form onSubmit={handleSubmit} resolver={zodResolver(schema)}>
        <MyFormContent />
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
