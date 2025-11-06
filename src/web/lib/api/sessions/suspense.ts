import { getSessions } from './getSessions'
import type { SessionOverview } from './getSessions'

type SessionsResponse = {
  sessions: [string, SessionOverview][]
}

let sessionsPromise: Promise<SessionsResponse> | null = null
let sessionsCache: SessionsResponse | null = null

export const fetchSessions = (): SessionsResponse => {
  if (!sessionsCache) {
    if (!sessionsPromise) {
      sessionsPromise = getSessions()
    }
    throw sessionsPromise.then((data) => {
      sessionsCache = data

      return data
    })
  }

  return sessionsCache
}

export const clearSessionsCache = (): void => {
  sessionsPromise = null
  sessionsCache = null
}
