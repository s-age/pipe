# Gemini API Prompt Architecture

This document details the prompt construction architecture for the Gemini API (specifically supporting Gemini 3.0 Thought Process) within the `pipe` framework.
To balance context caching efficiency with the reliable transmission of thought processes (`thought_signature`), we have adopted a **4-Layer Architecture**.

## The 4-Layer Architecture

The request payload is constructed as a list of `Content` objects (or strings compatible with the SDK) combined in the following strict order:

| Layer | Component | Format | Cacheable | Role | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Static** | Text (Jinja2 Rendered) | ✅ Yes | System/User | Immutable system instructions, roles, rules, and procedures. Explicit target for context caching. Includes explicit `cached_history`. |
| **2** | **Dynamic** | Text (JSON) | ❌ No | User | Volatile context information such as file references, artifacts, todos, and current datetime. |
| **3** | **Buffered** | List[`Content` Obj] | ❌ No | User/Model | Recent conversation history not yet cached. **Crucially contains the `thought_signature`** from the previous model response. |
| **4** | **Trigger** | `Content` Obj | ❌ No | User | The immediate trigger for execution. Either the user's new instruction (`current_task`) or a tool's execution result (`tool_response`). |

### 1. Static Layer (Explicit Cache)

*   **Content**: Definitions for `roles`, `procedure`, `constraints`, and `cached_history` (old turns exceeding the buffer threshold).
*   **Purpose**: To maximize context caching efficiency by grouping immutable or rarely changing content at the beginning of the prompt.
*   **Implementation**: Rendered from `gemini_static_prompt.j2`.

### 2. Dynamic Layer (Context Info)

*   **Content**: `file_references`, `artifacts`, `todos`, `current_datetime`.
*   **Purpose**: To provide the model with the latest state of the project and environment.
*   **Implementation**: Rendered from `gemini_dynamic_prompt.j2` as a **JSON string** and appended as a text part.
*   **Note**: Previously, `current_task` was included here, but it has been moved to the **4th Layer** to ensure correct chronological ordering.

### 3. Buffered Layer (History & Thought Signature)

*   **Content**: Recent conversation turns (`turns`) that are not yet cached.
*   **Key Mechanism**: The most recent `ModelResponseTurn` in this layer MUST contain the **`thought_signature`** (opaque binary tokens) from the previous API response to enable Gemini 3.0's continuous thought process.
*   **Implementation**: Constructed as a list of `google.genai.types.Content` objects, NOT plain text. The `Content` object containing the `thought_signature` is restored (deserialized and decoded) from the persisted `raw_response`.

### 4. Trigger Layer (User Task / Tool Response)

*   **Content**: The demand for action.
    *   **Case A (Normal Turn)**: A new instruction from the user (`UserTaskTurn`).
    *   **Case B (Post-Tool Execution)**: The result of a tool execution (`ToolResponseTurn`). In this case, `UserTaskTurn` is typically empty or None.
*   **Purpose**: Placed at the very **end** of the request to strongly prompt the model to "respond to THIS input".
*   **Ordering**: If this layer were placed before the Buffered History (e.g., inside the Dynamic Layer), the model would see "Current Question -> Past Conversation -> End", leading to confusion or empty responses (`Model stream was empty`).

## Data Flow Diagram

```mermaid
graph TD
    Start([Start Streaming Request]) --> Build[Build Prompt Model]
    
    subgraph "Layer 1: Static"
        Build --> Static[Render gemini_static_prompt.j2]
        Static -- Cache Miss --> Payload[Append to Payload]
        Static -- Cache Hit --> Cache[Use Cached Content ID]
    end
    
    subgraph "Layer 2: Dynamic"
        Build --> Dynamic[Render gemini_dynamic_prompt.j2 (JSON)]
        Dynamic --> Payload
    end
    
    subgraph "Layer 3: Buffered"
        Build --> Buffer[Process Buffered Turns]
        Buffer -- Restore --> Signature[Inject thought_signature from raw_response]
        Signature --> Payload
    end
    
    subgraph "Layer 4: Trigger"
        Build --> Check{Is Instruction Present?}
        Check -- Yes --> Task[Create Current Task Content]
        Check -- No --> Tool[Assume Tool Response is in Buffer]
        Task --> Payload
    end
    
    Payload --> API[Call Gemini API]
```

## Implementation Details

*   **Strict Ordering**: The order `Static -> Dynamic -> Buffered -> Trigger` is mandatory.
*   **Mixed Types**: The `contents` list sent to the SDK contains a mix of `str` (for Static/Dynamic layers) and `types.Content` objects (for Buffered/Trigger layers). The SDK handles this hybrid structure.
*   **Signature Restoration**: Since `thought_signature` is binary data, it may be Base64 encoded when persisted to JSON (via Pydantic). The system manually applies `base64.b64decode` if necessary during the restoration of the Buffered Layer to ensure valid bytes are sent to the API.
