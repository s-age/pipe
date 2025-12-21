# Routes Layer

## Purpose

The Routes layer maps HTTP URLs to specific **Actions**. It uses Flask Blueprints to organize endpoints by domain (e.g., Session, File System, Settings).

## Responsibilities

1.  **URL Mapping**: Define the HTTP method and URL path.
2.  **Dispatching**: Delegate the request to the `ActionDispatcher`.
3.  **Response Formatting**: Convert the Action's result into a JSON response (usually handled automatically, but explicitly returned here).

## Rules

### ✅ DO

-   **Use Blueprints**: Organize routes into modules (e.g., `session_bp`, `fs_bp`).
-   **Use `dispatch_action`**: The standard way to invoke an Action.
-   **Use `dispatch_streaming_action`**: For endpoints that return a stream (SSE).
-   **Keep it Thin**: Routes should contain **ZERO** business logic. They simply pass the request to the dispatcher.
-   **Explicit Imports**: Import Action classes to pass to the dispatcher.

### ❌ DON'T

-   **NO Logic**: Do not write `if/else` or data processing in the route function.
-   **NO Direct Service Calls**: Do not instantiate Services here.
-   **NO String Dispatching**: Do not use string paths for Actions (deprecated). Use the class directly.

## File Structure

```text
src/pipe/web/routes/
├── __init__.py           # Exports blueprints
├── session.py            # Session routes
├── fs.py                 # File system routes
└── ...
```

## Example Implementation

### Standard Route

```python
from flask import Blueprint, jsonify, request
from pipe.web.dispatcher import dispatch_action
from pipe.web.actions.sessions.create_action import CreateSessionAction

session_bp = Blueprint("session", __name__, url_prefix="/api/v1/session")

@session_bp.route("/create", methods=["POST"])
def create_session():
    """
    Route for creating a session.
    Delegates entirely to CreateSessionAction.
    """
    # dispatch_action returns (response_data, status_code)
    response_data, status_code = dispatch_action(
        action=CreateSessionAction,
        params={},  # Pass path params if any (e.g. from <path:id>)
        request_data=request
    )
    return jsonify(response_data), status_code
```

### Route with Path Parameters

```python
@session_bp.route("/<path:session_id>/fork", methods=["POST"])
def fork_session(session_id):
    """
    Route with a path parameter.
    """
    response_data, status_code = dispatch_action(
        action=ForkSessionAction,
        params={"session_id": session_id}, # Explicitly pass path params
        request_data=request
    )
    return jsonify(response_data), status_code
```

### Streaming Route

```python
from pipe.web.streaming_dispatcher import dispatch_streaming_action
from pipe.web.request_context import RequestContext

@session_bp.route("/<path:session_id>/chat", methods=["POST"])
def chat(session_id):
    # Streaming requires a RequestContext wrapper manually
    request_context = RequestContext(
        path_params={"session_id": session_id}, 
        request_data=request
    )

    return dispatch_streaming_action(
        action_class=SessionChatAction,
        params={"session_id": session_id},
        request_data=request_context
    )
```

## Registration

All Blueprints must be registered in `src/pipe/web/app.py`:

```python
# src/pipe/web/app.py
from pipe.web.routes import session_bp, fs_bp

def create_app():
    app = Flask(...)
    # ...
    app.register_blueprint(session_bp)
    app.register_blueprint(fs_bp)
    # ...
```
