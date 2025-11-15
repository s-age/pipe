# Component Architecture Guidelines

## Overview

This project follows a modified Atomic Design pattern with strict access control rules for state management. Components are organized into four layers: Pages, Organisms, Molecules, and Atoms.

## Directory Structure

```
src/web/components/
├── pages/          # Page-level components (routing, data orchestration)
├── organisms/      # Complex sections (forms, lists, headers)
├── molecules/      # Composite UI components (input groups, cards)
└── atoms/          # Basic UI elements (buttons, icons, labels)
```

## Layer Responsibilities and Rules

### State Management and Atomic Design Rules

#### 1. Store (State Management) Responsibilities

| Item                          | Rules and Policy                                                                                                                                                 | Purpose                                                                         |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **Store Placement**           | Place **global stores** (useAppStore) at the **top level** in `App.tsx` using Provider pattern to make them accessible throughout the application.               | Global access and single source of truth.                                       |
| **Page Store Initialization** | **Page-specific stores** are initialized within Page components using custom hooks (e.g., `useSessionStore()`), not as Context Providers.                        | Prevent global Store bloat and maintain clear boundaries.                       |
| **Store Types**               | For **global temporary UI** (toast, loading) and **frequently updated state**, adopt `useReducer` to minimize re-render scope.                                   | Performance optimization and avoiding Provider re-render issues.                |
| **Pages Responsibility**      | Pages layer is responsible for managing **domain state specific to that page** (e.g., session list, filters, settings).                                          | Prevent global Store from becoming bloated and maintain separation of concerns. |
| **Action Encapsulation**      | Store actions (`dispatch`) must always be **encapsulated as action creators**, ensuring that **child components don't need to know Store's internal structure**. | Reduce coupling and improve maintainability.                                    |

#### 2. Atomic Design Access Rules

Clear boundaries for Store (Context) access permissions.

| Layer         | Scope of Responsibility                                                                | Store/State Access                                                                                      |
| :------------ | :------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| **Pages**     | **Data flow orchestration**, **business logic integration**, **routing**.              | ✅ **Access allowed** (manages and accesses Stores).                                                    |
| **Organisms** | **Complex sections** (e.g., forms, lists). Data integration logic.                     | ✅ **Partially allowed**<br>• Direct access to `useAppStore` (global UI)<br>• Page Store via Props only |
| Molecules     | **Composite UI components**. Local UI state (open/closed, input values) is acceptable. | ❌ **No direct access to global/page stores** (Props only).<br>✅ **Allowed to access form context** via `react-hook-form` hooks. |
| **Atoms**     | **Minimal UI elements** (buttons, icons). Pure rendering.                              | ❌ **No access** (Props only). No internal State.                                                       |

### Store Access Pattern Details

```typescript
// ✅ Global Store - Direct access from Pages and Organisms
import { useAppStore } from '@/stores/useAppStore'

const MyOrganism = () => {
  const { pushToast, isLoading } = useAppStore()
  // Direct access OK for global UI concerns
}

// ✅ Page Store - Initialized in Page, passed via Props
const ChatHistoryPage = () => {
  const { state, actions } = useSessionStore()  // Initialize here

  return (
    <SessionMeta
      sessionDetail={state.sessionDetail}      // Pass as Props
      onRefresh={actions.refreshSessions}      // Pass as Props
    />
  )
}

// ❌ Molecules/Atoms - No Store access
const InputGroup = ({ value, onChange }) => {
  // Only use Props - no useAppStore, no useSessionStore
  return <input value={value} onChange={onChange} />
}
```

## Component Layer Guidelines

- [Pages](./pages.md) - Page-level routing and state orchestration
- [Organisms](./organisms.md) - Complex sections with business logic
- [Molecules](./molecules.md) - Composite UI components
- [Atoms](./atoms.md) - Basic UI elements

## Development Process and Custom Hook Rules

### 1. Custom Hook Rules (Strict SRP)

| Item                     | Rules and Policy                                                                                                                                    | Evaluation                                                                                                |
| :----------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **Naming Convention**    | Custom hooks must use **`use*`** naming convention (e.g., `useSessionHandlers.ts`) in the same directory.                                           | ✅ **Excellent**: Adheres to React rules and makes it immediately obvious that the file is a custom hook. |
| **Responsibility (SRP)** | Strictly follow **Single Responsibility Principle (SRP)**. One hook handles one logic concern (e.g., data fetching, auth state, toast operations).  | ✅ **Very Important**: Reduces coupling and makes testing and reuse easier.                               |
| **Placement**            | If a hook is only used by a specific component, place it in the same directory. For general-purpose hooks, place in `src/hooks` or `src/web/hooks`. | Improves organization and discoverability.                                                                |
| **Hook Categories**      | Follow [Actions/Handlers/Lifecycle](../hooks/hooks.md) pattern for component-specific hooks.                                                        | Consistent separation of concerns.                                                                        |

### 2. Props Drilling vs Store

#### Use Props (Preferred)

```typescript
// ✅ Good - Explicit data flow
const ParentPage = () => {
  const { state, actions } = useSessionStore()
  return <ChildOrganism data={state.data} onUpdate={actions.update} />
}
```

#### Use Store (When Necessary)

```typescript
// ✅ Acceptable - Global UI concerns
const DeepNestedOrganism = () => {
  const { pushToast } = useAppStore()  // OK for toast/loading
  return <button onClick={() => pushToast({ ... })}>Save</button>
}
```

#### Anti-pattern

```typescript
// ❌ Bad - Molecule accessing Store
const InputMolecule = () => {
  const { pushToast } = useAppStore()  // ❌ Not allowed!
  return <input />
}
```

## Component Communication Patterns

### 1. Parent to Child (Props Down)

```typescript
<ChildComponent
  data={parentData}
  onAction={handleAction}
/>
```

### 2. Child to Parent (Callbacks Up)

```typescript
const Parent = () => {
  const handleUpdate = (newValue) => {
    // Handle update
  }
  return <Child onUpdate={handleUpdate} />
}
```

### 3. Sibling Communication (Lift State Up)

```typescript
const Parent = () => {
  const [sharedState, setSharedState] = useState()
  return (
    <>
      <SiblingA state={sharedState} onUpdate={setSharedState} />
      <SiblingB state={sharedState} onUpdate={setSharedState} />
    </>
  )
}
```

### 4. Cross-component UI (Global Store)

```typescript
// Component A
const { pushToast } = useAppStore()
pushToast({ status: 'success', message: 'Saved!' })

// Component B (anywhere in tree)
const { state } = useAppStore()
return state.toasts.map(toast => <Toast {...toast} />)
```

## Testing Strategy by Layer

### Pages

- Integration tests with mocked APIs
- Router behavior
- Store initialization and data flow

### Organisms

- Component tests with mocked hooks
- User interaction flows
- Props interface contracts

### Molecules

- Unit tests with various prop combinations
- UI state transitions
- Accessibility

### Atoms

- Snapshot tests
- Style variations
- Accessibility compliance

## File Organization

### Component Directory Structure

```
ComponentName/
├── index.tsx           # Main component
├── style.css.ts        # Vanilla Extract styles
├── hooks/              # Component-specific hooks
│   ├── useComponentActions.ts
│   ├── useComponentHandlers.ts
│   └── useComponentLifecycle.ts
├── types.ts            # Component-specific types (if needed)
└── __stories__/        # Storybook stories
    └── ComponentName.stories.tsx
```

### When to Split a Component

Split a component when:

- ✅ File exceeds ~200-300 lines
- ✅ Multiple distinct responsibilities
- ✅ Part of the component is reusable
- ✅ Logic becomes too complex

Keep together when:

- ❌ Split would create tight coupling
- ❌ Components are always used together
- ❌ Splitting makes code harder to understand

## Best Practices

1. **Explicit over implicit** - Make data flow obvious through Props
2. **Colocate related code** - Keep hooks, styles, and components together
3. **Limit Store access** - Use Props for most data passing
4. **Single responsibility** - Each component should do one thing well
5. **Compose, don't inherit** - Build complex UIs from simple components
6. **Type everything** - Use TypeScript strictly
7. **Test at the right level** - Unit test atoms, integration test pages

## Anti-patterns to Avoid

❌ **Deep Store access in Molecules**

```typescript
// ❌ Bad
const InputMolecule = () => {
  const { sessionDetail } = useSessionStore() // Not allowed!
}
```

❌ **Props drilling many levels**

```typescript
// ❌ Bad - too many levels
<Page> → <Organism> → <Molecule> → <Atom> → <DeepAtom>
// Consider: lifting state or using composition
```

❌ **Mixed responsibilities**

```typescript
// ❌ Bad - Page doing too much
const Page = () => {
  // 50 lines of business logic
  // 100 lines of JSX
  // Multiple API calls inline
}
// Split into: Page + Organisms + custom hooks
```

❌ **God components**

```typescript
// ❌ Bad - Organism doing everything
const GiantOrganism = () => {
  // Data fetching
  // Form handling
  // Validation
  // Rendering
  // 500+ lines
}
// Split into: multiple smaller Organisms + hooks
```

## Related Documentation

- [Stores Guidelines](../stores.md) - State management patterns
- [Custom Hooks Guidelines](../hooks/hooks.md) - Hook organization
- [API Guidelines](../api.md) - API integration patterns
