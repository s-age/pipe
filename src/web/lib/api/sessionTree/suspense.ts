import { getSessionTree } from './getSessionTree'
import type { SessionOverview } from './getSessionTree'

type SessionsResponse = {
  sessions: [string, SessionOverview][]
}

let sessionsPromise: Promise<SessionsResponse> | null = null
let sessionsCache: SessionsResponse | null = null

export const fetchSessionTree = (): SessionsResponse => {
  if (!sessionsCache) {
    if (!sessionsPromise) {
      sessionsPromise = getSessionTree()
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
