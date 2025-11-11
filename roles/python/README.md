# Python Role Definitions for src/pipe/core

This directory contains clear role definitions for each layer in `src/pipe/core`. Based on the TypeScript version in `roles/typescript`, these define Python-specific architecture patterns and conventions.

## 📚 Documentation Structure

### Overall Guidelines

- **[python.md](./python.md)** - Project-wide Python conventions, forbidden patterns, core principles

### Layer-Specific Role Definitions

#### Core Layer (core/)

Detailed definitions of responsibilities, characteristics, dependencies, and examples for each layer:

1. **[agents.md](./core/agents.md)** - External AI API interface layer
2. **[services.md](./core/services.md)** - Application orchestration layer
3. **[domains.md](./core/domains.md)** - Business logic layer
4. **[repositories.md](./core/repositories.md)** - Persistence layer
5. **[models.md](./core/models.md)** - Pydantic data model layer
6. **[delegates.md](./core/delegates.md)** - High-level workflow orchestration layer
7. **[collections.md](./core/collections.md)** - Type-safe container layer
8. **[factories.md](./core/factories.md)** - Dependency injection layer
9. **[tools.md](./core/tools.md)** - AI-callable function layer
10. **[utils.md](./core/utils.md)** - Pure utility layer
11. **[validators.md](./core/validators.md)** - Complex validation layer

#### Web Layer (web/)

BFF (Backend for Frontend) layer role definitions:

- **[web.md](./web.md)** - Overall web layer guidelines and BFF architecture
- **[controllers.md](./web/controllers.md)** - Multi-action orchestration layer
- **[actions.md](./web/actions.md)** - Single-purpose operation layer
- **[requests.md](./web/requests.md)** - Request validation model layer
- **[validators.md](./web/validators.md)** - Reusable validation function layer

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────┐
│ Web Layer (BFF)                             │
│  ├─ Controllers (Multi-action)              │  ← HTTP orchestration
│  ├─ Actions (Single operation)              │  ← HTTP → Core adapter
│  ├─ Requests (Validation)                   │  ← Input validation
│  └─ Validators (Rules)                      │  ← Reusable validation
├─────────────────────────────────────────────┤
│ Core Layer                                  │
│  ├─ delegates/      (Orchestration)         │  ← Command entry points
│  ├─ services/       (Application)           │  ← Business orchestration
│  ├─ domains/        (Domain Logic)          │  ← Business rules
│  ├─ agents/         (External Integration)  │  ← AI API wrappers
│  ├─ repositories/   (Persistence)           │  ← Data access
│  ├─ collections/    (Data Structures)       │  ← Specialized containers
│  ├─ models/         (Data)                  │  ← Pydantic models
│  ├─ validators/     (Validation)            │  ← Data validation
│  ├─ utils/          (Infrastructure)        │  ← Pure functions
│  ├─ tools/          (AI Capabilities)       │  ← AI tool functions
│  └─ factories/      (DI)                    │  ← Dependency injection
└─────────────────────────────────────────────┘
```

## 🎯 Key Principles

### 1. Inter-Layer Dependency Rules

**Allowed Dependencies:**

- Web Controllers → Web Actions, Core Services
- Web Actions → Core Services, Web Requests, Core Models
- Web Requests → Web Validators, Core Models
- Web Validators → No dependencies (pure functions)
- `delegates/` → services, agents, models
- `services/` → repositories, domains, collections, agents, models, utils
- `domains/` → collections, models, utils
- `agents/` → services (specific methods), models, utils
- `repositories/` → models, utils
- `collections/` → models
- `models/` → No dependencies (standard library and Pydantic only)

**Forbidden Dependencies:**

- ❌ Web layer must NOT import Core domains directly
- ❌ Web Actions must NOT call other actions
- ❌ Web Requests must NOT import services
- ❌ Core `models/` must NOT import other core layers
- ❌ Core `repositories/` must NOT import services or domains
- ❌ Core `domains/` must NOT import services or agents
- ❌ Core `utils/` must NOT import other core layers

### 2. Forbidden Patterns

1. **Direct file I/O in Services or Domains** - Use `repositories/`
2. **Business logic in Models** - Use `domains/`
3. **Mutable global state** - Use dependency injection
4. **Direct AI API calls outside agents/** - Use `agents/` layer
5. **print() for logging** - Use `logging` module
6. **Business logic in Web layer** - Keep web layer thin, use core services
7. **Orchestration in Actions** - Use controllers for multi-action coordination

### 3. Type Safety

- Complete type hints for all public functions
- Runtime type validation with Pydantic models
- Avoid circular imports with `TYPE_CHECKING`

## 🎯 Quick Task Guide

**For LLMs: Start here to quickly find the right documentation.**

### Common Development Tasks

| Task                      | Read These (in order)                                                  | Key Points                                                            |
| ------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Add HTTP endpoint**     | 1. `web/actions.md`<br>2. `web/requests.md`<br>3. `core/services.md`   | Action = 1 operation<br>Validate in Request model<br>Logic in Service |
| **Add business logic**    | 1. `core/domains.md`<br>2. `core/services.md`                          | Pure logic → Domain<br>Orchestration → Service                        |
| **Add data persistence**  | 1. `core/repositories.md`<br>2. `core/models.md`                       | All file I/O in Repository<br>Models are pure data                    |
| **Add AI integration**    | 1. `core/agents.md`<br>2. `core/tools.md`                              | API calls only in Agents<br>Tool = AI-callable function               |
| **Add validation**        | 1. `core/validators.md` (complex)<br>2. `web/requests.md` (HTTP input) | Complex rules → Validator<br>HTTP input → Request model               |
| **Multi-step workflow**   | 1. `core/delegates.md`<br>2. `core/services.md`                        | CLI entry → Delegate<br>Coordinate → Service                          |
| **Combine API responses** | 1. `web/controllers.md`<br>2. `web/actions.md`                         | Multiple actions → Controller<br>Single op → Action                   |

### Decision Tree

```
Need to add code?
│
├─ HTTP/API related?
│  ├─ Validate input? → web/requests.md
│  ├─ Single operation? → web/actions.md
│  └─ Multiple operations? → web/controllers.md
│
├─ Business logic?
│  ├─ Pure calculation/rules? → core/domains.md
│  ├─ Coordinate components? → core/services.md
│  └─ CLI workflow? → core/delegates.md
│
├─ Data related?
│  ├─ Define structure? → core/models.md
│  ├─ Save/load files? → core/repositories.md
│  ├─ Type-safe container? → core/collections.md
│  └─ Complex validation? → core/validators.md
│
├─ External integration?
│  ├─ AI API calls? → core/agents.md
│  └─ AI-callable function? → core/tools.md
│
└─ Utilities?
   ├─ Reusable helpers? → core/utils.md
   └─ Object creation? → core/factories.md
```

## 📖 Usage Guide

### When Adding New Components

1. **Use the Quick Task Guide above** to find relevant docs
2. Read the role definition for the appropriate layer
3. Reference templates and real examples in the docs
4. Avoid forbidden patterns (marked with ❌)
5. Respect inter-layer dependency rules

### During Code Review

1. Verify components are in the correct layer
2. Check adherence to layer responsibilities
3. Ensure no forbidden patterns are used
4. Verify dependency rules are followed

### During Refactoring

1. Verify business logic is in `domains/`
2. Ensure file I/O is isolated in `repositories/`
3. Confirm API calls are limited to `agents/`
4. Verify Models are pure data containers

## 🔍 Document Contents

### Quick Reference by Layer

Each document follows this structure:

1. **Purpose** - What this layer does
2. **Characteristics** - ✅ Do / ❌ Don't
3. **Template** - Copy-paste starting point
4. **Real Examples** - From actual codebase
5. **Testing** - How to test this layer
6. **Best Practices** - Common patterns

| Layer                    | Purpose                    | Read When                          |
| ------------------------ | -------------------------- | ---------------------------------- |
| **web.md**               | BFF architecture overview  | Adding any HTTP endpoint           |
| **web/controllers.md**   | Multi-action orchestration | Combining multiple API operations  |
| **web/actions.md**       | Single HTTP operations     | Adding one API endpoint            |
| **web/requests.md**      | Input validation           | Validating HTTP request data       |
| **web/validators.md**    | Reusable validation rules  | Sharing validation across requests |
| **core/delegates.md**    | CLI workflow entry points  | Adding CLI command                 |
| **core/services.md**     | Business orchestration     | Coordinating multiple components   |
| **core/domains.md**      | Pure business logic        | Adding calculation/rules           |
| **core/agents.md**       | AI API wrappers            | Calling external AI APIs           |
| **core/repositories.md** | Data persistence           | Reading/writing files              |
| **core/models.md**       | Data structures            | Defining new data types            |
| **core/collections.md**  | Type-safe containers       | Managing lists of models           |
| **core/factories.md**    | Dependency injection       | Creating service instances         |
| **core/tools.md**        | AI-callable functions      | Adding AI tool                     |
| **core/utils.md**        | Pure utility functions     | Reusable helpers                   |
| **core/validators.md**   | Complex validation         | Multi-field validation rules       |

### Detailed Documentation

### python.md (Overall Guidelines)

- Core principles
- Architecture layers
- Forbidden patterns
- Type hint guidelines
- Error handling
- Code quality tools

### Web Layer (web/)

- **web.md** - BFF architecture overview, layer responsibilities, forbidden patterns
- **web/controllers.md** - Multi-action orchestration, composite responses, frontend-specific views
- **web/actions.md** - Single-purpose operations, service coordination, error handling
- **web/requests.md** - Request validation models, Pydantic validators, input parsing
- **web/validators.md** - Reusable validation functions, custom rules, pure validation

### Core Layer (core/)

- **core/agents.md** - External AI API wrappers, request/response transformation, retry logic
- **core/services.md** - Application orchestration, session lifecycle, prompt construction
- **core/domains.md** - Pure business logic, data transformation, state transitions
- **core/repositories.md** - Data persistence, file I/O, locking, backup
- **core/models.md** - Pydantic data models, type safety, validation, serialization
- **core/delegates.md** - Workflow orchestrators, high-level entry points
- **core/collections.md** - Type-safe containers, specialized data structures
- **core/factories.md** - Dependency injection, object creation
- **core/tools.md** - AI-callable functions, schema generation
- **core/utils.md** - Pure utility functions, infrastructure helpers
- **core/validators.md** - Complex validation logic, business rule enforcement

## 🎓 Learning Path

### For LLMs/AI Assistants

**Efficient Reading Strategy:**

1. Start with this README (Quick Task Guide + Decision Tree)
2. Read only the specific layer doc needed for your task
3. Focus on ✅/❌ patterns and templates
4. Reference real examples when implementing

**Token Optimization:**

- Each layer doc is ~400-700 lines
- Average task needs 1-2 docs only
- Use Quick Reference table to find docs
- Skip "Testing" and "Best Practices" sections initially

### For Beginners

1. `python.md` - Understand the big picture
2. `core/models.md` - Understand data structures
3. `core/repositories.md` - Understand persistence

### For Intermediate Users

4. `core/domains.md` - Understand business logic
5. `core/services.md` - Understand orchestration
6. `core/agents.md` - Understand external integration

### For Advanced Users

7. `core/delegates.md`, `core/collections.md`, etc. - Understand support layers
8. Grasp overall architecture patterns
9. Design new layers and features

## � Common Mistakes & Solutions

### Mistake 1: Business Logic in Models

```python
# ❌ BAD
class Session(BaseModel):
    turns: list[Turn]

    def get_active_turns(self):  # Logic in model!
        return [t for t in self.turns if t.is_active]
```

**Error symptoms**: Models become too complex, hard to test
**Solution**: Move logic to `domains/`

```python
# ✅ GOOD
# In domains/turns.py
def get_active_turns(turns: list[Turn]) -> list[Turn]:
    return [t for t in turns if t.is_active]
```

### Mistake 2: File I/O in Services

```python
# ❌ BAD
class SessionService:
    def save_session(self, session: Session):
        with open(f"sessions/{session.id}.json", "w") as f:  # Direct I/O!
            json.dump(session.to_dict(), f)
```

**Error symptoms**: Hard to test, can't mock file operations
**Solution**: Use `repositories/`

```python
# ✅ GOOD
class SessionService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def save_session(self, session: Session):
        self.repository.save(session)  # Repository handles I/O
```

### Mistake 3: Orchestration in Actions

```python
# ❌ BAD
class SessionAction(BaseAction):
    def execute(self):
        # Doing too much!
        tree = session_service.get_tree()
        session = session_service.get_session(id)
        settings = settings_service.get_settings()
        return {"tree": tree, "session": session, "settings": settings}, 200
```

**Error symptoms**: Actions become too complex
**Solution**: Use `controllers/` for orchestration

```python
# ✅ GOOD
class SessionDetailController:
    def get_session_with_tree(self, session_id):
        tree_response, _ = SessionTreeAction(...).execute()
        session_response, _ = SessionGetAction(...).execute()
        return {"tree": tree_response, "session": session_response}, 200
```

### Mistake 4: Circular Imports

```python
# ❌ BAD
# In domains/session_logic.py
from pipe.core.repositories.session_repository import SessionRepository  # Circular!

def process_session(session):
    repo = SessionRepository()  # Domain depending on Repository
```

**Error symptoms**: `ImportError: cannot import name '...'`
**Solution**: Follow dependency rules - domains should NOT import repositories

```python
# ✅ GOOD
# In services/session_service.py
def process_session(self, session_id: str):
    session = self.repository.find(session_id)
    processed = domains.process_session(session)  # Pass data to domain
    self.repository.save(processed)
```

### Mistake 5: No Request Validation

```python
# ❌ BAD
class CreateAction(BaseAction):
    def execute(self):
        data = self.request_data.get_json()
        if not data.get("name"):  # Manual validation in action
            return {"error": "Name required"}, 400
        # ... more manual checks
```

**Error symptoms**: Validation logic scattered across actions
**Solution**: Use Pydantic request models

```python
# ✅ GOOD
# In requests/create_request.py
class CreateRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name required")
        return v

# In action
class CreateAction(BaseAction):
    def execute(self):
        request = CreateRequest(**self.request_data.get_json())  # Auto-validates
        result = service.create(request.name)
        return {"result": result}, 200
```

## 🔧 Troubleshooting

### Import Errors

**Problem**: `ImportError: cannot import name 'X'`

- **Likely cause**: Circular dependency
- **Check**: Review dependency rules in architecture diagram
- **Solution**: Use `TYPE_CHECKING` or restructure dependencies

### Validation Errors

**Problem**: Pydantic validation fails

- **Check**: `web/requests.md` for request validation patterns
- **Check**: `core/validators.md` for complex validation
- **Solution**: Add `@field_validator` or use validator function

### Type Errors

**Problem**: mypy reports type errors

- **Check**: All functions have type hints
- **Check**: Using `TYPE_CHECKING` for circular imports
- **Solution**: Add proper type annotations

### File I/O Errors

**Problem**: Permission denied, file not found

- **Check**: All file I/O goes through `repositories/`
- **Check**: Using `FileLock` for concurrent access
- **Solution**: Review `core/repositories.md`

## 🛠️ Code Quality Checks

```bash
# Type checking
mypy src/pipe/core

# Linting
ruff check src/pipe/core

# Formatting
ruff format src/pipe/core

# Testing
pytest tests/core

# Coverage
pytest --cov=src/pipe/core tests/core
```

## 📝 Additional Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## 🤝 Contributing

These role definitions are living documents. Improvement suggestions and new pattern additions are welcome.
