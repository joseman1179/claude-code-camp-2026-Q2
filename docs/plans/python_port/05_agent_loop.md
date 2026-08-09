# Plan: Port 05_agent_loop from Ruby → Python

## Overview

Port `week1_baseline/ruby/05_agent_loop` to Python as
`week1_baseline/python/05_agent_loop/`.

The Python snapshot already exists as a copy of `04_api_client`. This is the
**big step** — the Agent loop ties together every piece built so far. The Agent
orchestrates the full turn: call API → parse response → dispatch tools → inject
results → repeat, until the model returns text or the iteration limit is hit.

---

## What's new vs 04_api_client

| Component | Status |
|-----------|--------|
| `Agent` | **NEW** — the loop orchestrator (replaces the old BFS `agent.py` from step 0) |
| `Config`, `Tool`, `Message`, `Context`, `Registry` | Unchanged |
| `UnknownToolError`, `UnsupportedModelError`, `ApiError` | Unchanged |
| `Tasks::Base` | **Updated** — adds `max_iterations()`, `max_output_tokens()`, `_integer_setting()` |
| `PromptBuilder` | **Updated** — adds `parse_response()`, `to_api_payload` gets `tools=` kwarg |
| `Client` | **Updated** — `call()` gets `tools=` kwarg |
| All backends | **Updated** — add `parse_response()`, `to_payload` gets `tools=`, `to_messages` handles assistant blocks |
| `lib/boukensha.rb` | Updated — adds agent require |
| `examples/example.rb` | Replaced — builds Agent, runs the full loop |
| `README.md` | Replaced |

No new dependencies.

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/agent.rb` | → | `boukensha/agent.py` | **Replace** — old BFS agent replaced by loop agent |
| `lib/boukensha/tasks/base.rb` | → | `boukensha/tasks/base.py` | **Update** — add iteration/token settings |
| `lib/boukensha/prompt_builder.rb` | → | `boukensha/prompt_builder.py` | **Update** — add `parse_response`, `tools=` kwarg |
| `lib/boukensha/client.rb` | → | `boukensha/client.py` | **Update** — add `tools=` kwarg |
| `lib/boukensha/backends/base.rb` | → | `boukensha/backends/base.py` | Unchanged (no new behaviour in base) |
| `lib/boukensha/backends/anthropic.rb` | → | `boukensha/backends/anthropic.py` | **Update** |
| `lib/boukensha/backends/deepseek.rb` | → | `boukensha/backends/deepseek.py` | **Update** |
| `lib/boukensha/backends/openai.rb` | → | `boukensha/backends/openai.py` | **Update** |
| `lib/boukensha/backends/ollama.rb` | → | `boukensha/backends/ollama.py` | **Update** |
| `lib/boukensha/backends/ollama_cloud.rb` | → | `boukensha/backends/ollama_cloud.py` | **Update** |
| `lib/boukensha/backends/gemini.rb` | → | `boukensha/backends/gemini.py` | **Update** |
| `lib/boukensha/backends/_openai_compatible.rb` (conceptual) | → | `boukensha/backends/_openai_compatible.py` | **Update** — shared logic for OpenAI/DeepSeek/Ollama/OllamaCloud |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |
| — | → | `bin/python/05_agent_loop` | **Create** launcher |

---

## Mapping: Ruby → Python

### Agent (`agent.rb` → `agent.py`)

This is a **new** Agent class that completely replaces the old BFS pathfinding
`agent.py` from step 0. The old file was a simple BFS navigator; the new one
is the main loop orchestrator.

| Ruby | Python |
|------|--------|
| `MAX_ITERATIONS = 25` | Class constant |
| `WRAP_UP_OUTPUT_TOKENS = 400` | Class constant |
| `WRAP_UP_DIRECTIVE = "..."` | Class constant (multiline string) |
| `initialize(context:, registry:, builder:, client:, task_settings:, max_iterations:, max_output_tokens:)` | `__init__` with same kwargs |
| `run` → loop with iteration counter | Same |
| `wrap_up(reason)` → final tools-disabled call | Same |
| `handle_tool_calls(content)` → dispatch each tool_use block | Same |
| `extract_text(content)` → join text blocks | Same |
| `@iteration += 1` | Same |
| `@client.call(**call_opts)` | `self.client.call(**self._call_opts())` |
| `@builder.parse_response(response)` | `self.builder.parse_response(response)` |
| `@registry.dispatch(name, args)` | `self.registry.dispatch(name, args)` |
| `@context.add_message(:assistant, content)` | `self.context.add_message("assistant", content)` |
| `@context.add_message(:tool_result, result, tool_use_id:)` | `self.context.add_message("tool_result", result, tool_use_id=use_id)` |

Agent loop pseudocode:

```
def run():
    while True:
        if iteration >= max_iterations:
            return wrap_up("max_iterations")

        iteration += 1
        print "[iteration N/M]"

        response = client.call()
        parsed = builder.parse_response(response)

        if parsed["stop_reason"] == "tool_use":
            context.add_message("assistant", parsed["content"])
            for each tool_use block in content:
                result = registry.dispatch(name, args)
                context.add_message("tool_result", result, tool_use_id=id)
        else:
            return extract_text(parsed["content"])
```

### Tasks::Base updates (`tasks/base.py`)

| Ruby | Python |
|------|--------|
| `DEFAULT_MAX_ITERATIONS = 25` | Class constant |
| `DEFAULT_MAX_OUTPUT_TOKENS = 1024` | Class constant |
| `max_iterations(settings)` class method | `@classmethod` — `_integer_setting(settings, "max_iterations", DEFAULT_MAX_ITERATIONS)` |
| `max_output_tokens(settings)` class method | `@classmethod` — `_integer_setting(settings, "max_output_tokens", DEFAULT_MAX_OUTPUT_TOKENS)` |
| `integer_setting(settings, key, default)` private | `@staticmethod` `_integer_setting` — `int(value)` or default |
| `fetch` updated: `return nil unless settings.is_a?(Hash)` | `if not isinstance(settings, dict): return None` |

### PromptBuilder updates (`prompt_builder.py`)

| Change | Detail |
|--------|--------|
| `to_api_payload` | Add `tools=None` parameter, pass to backend |
| `parse_response(response)` | New method — delegates to `self.backend.parse_response(response)` |

### Client updates (`client.py`)

| Change | Detail |
|--------|--------|
| `call` signature | Add `tools=None` parameter |
| Pass to builder | `self.builder.to_api_payload(max_output_tokens=max_output_tokens, tools=tools)` |

### `_openai_compatible.py` updates (shared base)

This is the shared base for OpenAI, DeepSeek, Ollama, and OllamaCloud. All get
the same three additions:

**1. `to_messages` — handle assistant blocks:**

```python
elif msg.role == "assistant":
    conversation.append(self._assistant_message(msg.content))
```

When the Agent adds an assistant message with normalized content blocks
(`[{"type": "text", ...}, {"type": "tool_use", ...}]`), `_assistant_message`
rebuilds them back into the provider-specific format. This is the inverse of
`parse_response`.

**2. `to_payload` — add `tools=` kwarg:**

```python
def to_payload(self, context, max_output_tokens=1024, tools=None):
    return {
        ...
        "tools": tools if tools is not None else self.to_tools(context.tools),
        ...
    }
```

When `tools=[]` is passed (wrap-up call), tools are disabled so the model can't
make more tool calls.

**3. `parse_response(response)` — normalize API response:**

OpenAI/DeepSeek format:

```python
def parse_response(self, response):
    message = response.get("choices", [{}])[0].get("message", {})
    tool_calls = message.get("tool_calls", [])

    content = []
    if message.get("content"):
        content.append({"type": "text", "text": message["content"]})

    for tc in tool_calls:
        fn = tc.get("function", {})
        content.append({
            "type": "tool_use",
            "id": tc["id"],
            "name": fn.get("name"),
            "input": json.loads(fn.get("arguments", "{}")),
        })

    stop_reason = "tool_use" if tool_calls else "end_turn"
    return {"stop_reason": stop_reason, "content": content}
```

**4. `_assistant_message(content)` — rebuild assistant message:**

OpenAI/DeepSeek format:

```python
def _assistant_message(self, content):
    if isinstance(content, str):
        blocks = [{"type": "text", "text": content}]
    else:
        blocks = content

    text = "".join(b["text"] for b in blocks if b["type"] == "text")
    tool_blocks = [b for b in blocks if b["type"] == "tool_use"]

    msg = {"role": "assistant", "content": text}
    if tool_blocks:
        msg["tool_calls"] = [
            {
                "id": b["id"],
                "type": "function",
                "function": {"name": b["name"], "arguments": json.dumps(b["input"])},
            }
            for b in tool_blocks
        ]
    return msg
```

**Ollama/OllamaCloud overrides:**

Ollama doesn't assign call IDs — it matches tool results to calls by name.
Override `parse_response` and `_assistant_message` in `ollama.py` and
`ollama_cloud.py`:

```python
# parse_response: use fn["name"] as id (no real id from Ollama)
content.append({
    "type": "tool_use",
    "id": fn["name"],
    "name": fn["name"],
    "input": fn.get("arguments", {}),
})

# _assistant_message: no "id" or "type" fields (Ollama format)
msg["tool_calls"] = [
    {"function": {"name": b["name"], "arguments": b["input"]}}
    for b in tool_blocks
]
```

### Anthropic backend updates (`anthropic.py`)

Anthropic doesn't need `_assistant_message` (its message format doesn't embed
tool_calls in assistant messages the same way). Only two changes:

1. `to_payload` — add `tools=None` parameter
2. Add `parse_response(response)`:

```python
def parse_response(self, response):
    stop_reason = "tool_use" if response.get("stop_reason") == "tool_use" else "end_turn"
    return {"stop_reason": stop_reason, "content": response.get("content", [])}
```

### Gemini backend updates (`gemini.py`)

Gemini has its own unique format. Changes:

1. `to_messages` — handle assistant blocks: `elif msg.role == "assistant": self._assistant_parts(msg.content)`
2. `to_payload` — add `tools=None` parameter
3. Add `parse_response(response)`:

```python
def parse_response(self, response):
    parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    content = []
    tool_used = False
    for part in parts:
        if "functionCall" in part:
            fc = part["functionCall"]
            content.append({"type": "tool_use", "id": fc["name"], "name": fc["name"], "input": fc.get("args", {})})
            tool_used = True
        elif "text" in part:
            content.append({"type": "text", "text": part["text"]})
    return {"stop_reason": "tool_use" if tool_used else "end_turn", "content": content}
```

4. Add `_assistant_parts(content)`:

```python
def _assistant_parts(self, content):
    if isinstance(content, str):
        blocks = [{"type": "text", "text": content}]
    else:
        blocks = content
    parts = []
    for b in blocks:
        if b["type"] == "tool_use":
            parts.append({"functionCall": {"name": b["name"], "args": b["input"]}})
        else:
            parts.append({"text": b["text"]})
    return parts
```

### DeepSeek backend updates (`deepseek.py`)

DeepSeek inherits from `OpenAICompatibleBase` — all shared changes come from
the base. Only need to add `import json` at the top (used by parent's
`_assistant_message` and `parse_response`).

### `__init__.py` update

The `Agent` import already exists (from `from boukensha.agent import Agent`).
Since we're replacing the agent implementation, no import change is needed.
But we do need to update the module docstring or verify the import still works.

---

## Dependencies

Unchanged. No new packages.

---

## Project Structure (target)

```
week1_baseline/python/05_agent_loop/
├── requirements.txt              # unchanged
├── README.md                     # replaced
├── boukensha/
│   ├── __init__.py               # unchanged (Agent already exported)
│   ├── agent.py                  # REPLACED — loop agent replaces BFS agent
│   ├── client.py                 # updated — tools= kwarg
│   ├── config.py                 # unchanged
│   ├── context.py                # unchanged
│   ├── errors.py                 # unchanged
│   ├── message.py                # unchanged
│   ├── prompt_builder.py         # updated — parse_response, tools=
│   ├── registry.py               # unchanged
│   ├── tool.py                   # unchanged
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── _openai_compatible.py # updated — parse_response, _assistant_message, tools=
│   │   ├── base.py               # unchanged
│   │   ├── anthropic.py          # updated — parse_response, tools=
│   │   ├── deepseek.py           # updated — import json
│   │   ├── gemini.py             # updated — parse_response, _assistant_parts, tools=
│   │   ├── ollama.py             # updated — parse_response override, _assistant_message override, tools=
│   │   ├── ollama_cloud.py       # updated — parse_response override, _assistant_message override, tools=
│   │   └── openai.py             # updated — import json (inherits rest)
│   └── tasks/
│       ├── __init__.py
│       ├── base.py               # updated — max_iterations, max_output_tokens
│       └── player.py             # unchanged
├── examples/
│   └── example.py                # replaced — builds Agent, runs loop
└── prompts/
    └── system.md                 # unchanged
```

---

## Behavior Parity Checklist

- [ ] Agent receives `context`, `registry`, `builder`, `client`, `task_settings`
- [ ] Agent loop: increments iteration, calls `client.call()`, parses response
- [ ] Tool calls: adds assistant message, dispatches each tool, adds tool_result messages
- [ ] Max iterations enforced via `resolve_max_iterations` (settings → explicit → default 25)
- [ ] Wrap-up: when limit hit, sends WRAP_UP_DIRECTIVE with `tools=[]`, returns final text
- [ ] Wrap-up falls back to deterministic message on `ApiError`
- [ ] `extract_text` joins all `type: "text"` blocks
- [ ] `tasks/base.py`: `max_iterations()`, `max_output_tokens()`, `_integer_setting()`
- [ ] `prompt_builder.py`: `parse_response()` delegates to backend, `to_api_payload` accepts `tools=`
- [ ] `client.py`: `call()` accepts `tools=` kwarg
- [ ] `_openai_compatible.py`: `parse_response`, `_assistant_message`, `to_messages` handles `"assistant"` role, `to_payload` accepts `tools=`
- [ ] `ollama.py` / `ollama_cloud.py`: override `parse_response` (name as id), `_assistant_message` (no id/type fields)
- [ ] `anthropic.py`: `parse_response`, `to_payload` accepts `tools=`
- [ ] `gemini.py`: `parse_response`, `_assistant_parts`, `to_messages` handles `"assistant"` role, `to_payload` accepts `tools=`

---

## Expected Output

```
=== BOUKENSHA Step 5: Agent Loop ===

Config: #<Boukensha::Config ...>
Provider: deepseek
Model: deepseek-v4-pro
Max iterations: 25
Max output tokens: 1024

[iteration 1/25]
  tool call → read_file({"path"=>"README.md"})
  tool result → ...
  tool call → list_directory({"path"=>"."})
  tool result → ...
[iteration 2/25]

=== FINAL RESPONSE ===
... (model's text response)
```

---

## Implementation Steps

1. Confirm snapshot exists as copy of step 4
2. Update `boukensha/backends/_openai_compatible.py` — add `parse_response`, `_assistant_message`, `to_messages` assistant handling, `to_payload` `tools=`
3. Update `boukensha/backends/openai.py` — add `import json`
4. Update `boukensha/backends/deepseek.py` — add `import json`
5. Update `boukensha/backends/ollama.py` — override `parse_response` + `_assistant_message`, `to_payload` `tools=`
6. Update `boukensha/backends/ollama_cloud.py` — same overrides as ollama
7. Update `boukensha/backends/anthropic.py` — add `parse_response`, `to_payload` `tools=`
8. Update `boukensha/backends/gemini.py` — add `parse_response`, `_assistant_parts`, `to_messages` assistant handling, `to_payload` `tools=`
9. Update `boukensha/prompt_builder.py` — add `parse_response`, `to_api_payload` `tools=`
10. Update `boukensha/client.py` — `call()` `tools=` kwarg
11. Update `boukensha/tasks/base.py` — add `max_iterations`, `max_output_tokens`, `_integer_setting`, fix `_fetch`
12. Replace `boukensha/agent.py` — new Agent loop class
13. Replace `examples/example.py`
14. Replace `README.md`
15. Create `bin/python/05_agent_loop`, make executable
16. Run smoke test

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Replace old `agent.py`? | **Yes** | Old BFS agent is step 0 code not used after step 1. New Agent is completely different |
| 2 | `_assistant_message` in shared base? | **Yes, with overrides** | OpenAI/DeepSeek use the base version. Ollama/OllamaCloud override (no id/type fields) |
| 3 | `parse_response` in shared base? | **Yes, with overrides** | OpenAI/DeepSeek use `tc["id"]`. Ollama/OllamaCloud use `fn["name"]` |
| 4 | `to_payload` `tools=` default? | **`None`** (means "use context tools") | `tools=[]` disables tools for wrap-up call |
| 5 | New dependencies? | **No** | `json` already imported in some files, stdlib |

---

## Out of Scope (future steps)

- Token budget tracking during runtime
- Compaction (trimming conversation history when near context window limit)
- Streaming responses
- Multi-task agent loops
