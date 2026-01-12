/* eslint-disable no-console */
import '@testing-library/jest-dom/vitest'

// Suppress React act() warnings for useSyncExternalStore updates in tests
// This is a known issue with React 19 and @testing-library/react
// See: https://github.com/testing-library/react-testing-library/issues/1214
const originalError = console.error
beforeAll(() => {
  console.error = (...arguments_: unknown[]): void => {
    const message =
      typeof arguments_[0] === 'string' ? arguments_[0] : String(arguments_[0])
    if (
      message.includes('An update to') &&
      message.includes('inside a test was not wrapped in act')
    ) {
      return
    }
    originalError.call(console, ...arguments_)
  }
})

afterAll(() => {
  console.error = originalError
})
