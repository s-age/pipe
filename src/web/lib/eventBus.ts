type EventCallback<T = unknown> = (data: T) => void

class EventBus {
  private events: Map<string, Set<EventCallback>> = new Map()

  on = <T = unknown>(event: string, callback: EventCallback<T>): (() => void) => {
    if (!this.events.has(event)) {
      this.events.set(event, new Set())
    }
    this.events.get(event)!.add(callback as EventCallback)

    return () => {
      this.off(event, callback)
    }
  }

  off = <T = unknown>(event: string, callback: EventCallback<T>): void => {
    const callbacks = this.events.get(event)
    if (callbacks) {
      callbacks.delete(callback as EventCallback)
      if (callbacks.size === 0) {
        this.events.delete(event)
      }
    }
  }

  emit = <T = unknown>(event: string, data: T): void => {
    const callbacks = this.events.get(event)
    if (callbacks) {
      callbacks.forEach((callback) => callback(data))
    }
  }

  clear = (): void => {
    this.events.clear()
  }
}

export const eventBus = new EventBus()
