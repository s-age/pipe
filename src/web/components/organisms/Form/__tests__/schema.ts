import { object, string, type TypeOf } from 'zod'

export const schema = object({
  name: string().min(1, 'Name is required'),
  email: string().email('Invalid email address'),
})

export type FormData = TypeOf<typeof schema>
