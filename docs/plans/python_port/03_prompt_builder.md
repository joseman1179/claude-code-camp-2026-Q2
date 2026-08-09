# Plan: Port 03_prompt_builder from Ruby → Python

## Overview

Port `week1_baseline/ruby/03_prompt_builder` to Python as
`week1_baseline/python/03_prompt_builder/`.

The Python snapshot already exists as a copy of `02_the_registry`. This plan
covers only the **step 3 delta**: compare Ruby `02_the_registry` to Ruby
`03_prompt_builder`, then apply those changes to the existing Python snapshot.

This step introduces the **Prompt Builder** — a serializer that converts
`Context` (tools + messages + system prompt) into the exact JSON payload each
LLM provider expects. Six backends are supported: Anthropic, DeepSeek, Gemini,
Ollama, Ollama Cloud, and OpenAI. Each backend owns its model catalog with
pricing metadata and validates models at construction time. A new error class
(`UnsupportedModelError`) signals unknown models.

---

## What's new vs 02_the_registry

| Component | Status |
|-----------|--------|
| `Config`, `Tasks::Base`, `Tasks::Player` | Unchanged |
| `Tool`, `Message`, `Context` | Unchanged |
| `Registry`, `UnknownToolError` | Unchanged |
| `UnsupportedModelError` | NEW — raised when a backend is given an unknown model |
| `Backends::Base` | NEW — shared contract: model validation, model metadata, cost estimation |
| `Backends::Anthropic` | NEW — Anthropic Messages API serializer |
| `Backends::DeepSeek` | NEW — DeepSeek Chat Completions serializer (OpenAI-compatible) |
| `Backends::Gemini` | NEW — Gemini generateContent serializer |
| `Backends::Ollama` | NEW — Local Ollama chat serializer |
| `Backends::OllamaCloud` | NEW — Ollama Cloud chat serializer |
| `Backends::OpenAI` | NEW — OpenAI Chat Completions serializer |
| `PromptBuilder` | NEW — delegates serialization to the active backend |
| `prompts/system.md` | NEW in this step (copied from Ruby; Python already has it from step 0 copy) |
| `boukensha.rb` (top-level exports) | Updated — adds prompt_builder + all backends |
| `examples/example.rb` | Replaced — selects backend by provider, prints JSON payload |

No new dependencies — `Gemfile` unchanged (just `dotenv`).

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/errors.rb` | → | `boukensha/errors.py` | **Update** — add `UnsupportedModelError` |
| `lib/boukensha/backends/base.rb` | → | `boukensha/backends/base.py` | **Create** |
| `lib/boukensha/backends/anthropic.rb` | → | `boukensha/backends/anthropic.py` | **Create** |
| `lib/boukensha/backends/deepseek.rb` | → | `boukensha/backends/deepseek.py` | **Create** |
| `lib/boukensha/backends/gemini.rb` | → | `boukensha/backends/gemini.py` | **Create** |
| `lib/boukensha/backends/ollama.rb` | → | `boukensha/backends/ollama.py` | **Create** |
| `lib/boukensha/backends/ollama_cloud.rb` | → | `boukensha/backends/ollama_cloud.py` | **Create** |
| `lib/boukensha/backends/openai.rb` | → | `boukensha/backends/openai.py` | **Create** |
| `lib/boukensha/prompt_builder.rb` | → | `boukensha/prompt_builder.py` | **Create** |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** — add PromptBuilder + backend exports, `__all__` |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |
| — | → | `bin/python/03_prompt_builder` | **Create** launcher |

All other files (`config.py`, `context.py`, `tool.py`, `message.py`,
`registry.py`, `tasks/`, `agent.py`, `prompts/system.md`, `requirements.txt`)
remain unchanged.

> **Note:** `prompts/system.md` already exists in the Python snapshot (carried
> from the step 0 copy). The Ruby step 3 also has it. The file is identical.

---

## Mapping: Ruby → Python

### `__init__.py` for backends

Each backend directory needs an `__init__.py`:

```
boukensha/backends/
├── __init__.py        # empty
├── base.py
├── anthropic.py
├── deepseek.py
├── gemini.py
├── ollama.py
├── ollama_cloud.py
└── openai.py
```

### UnsupportedModelError (`errors.py` update)

Add to existing `boukensha/errors.py`:

```python
class UnsupportedModelError(Exception):
    """Raised when a backend is given a model it doesn't support."""
    pass
```

### Backends::Base (`backends/base.rb` → `backends/base.py`)

| Ruby | Python |
|------|--------|
| `attr_reader :model` | `self.model` attribute |
| `const_get(:MODELS)` | `cls.MODELS` (class attribute) |
| `validate_model!(model)` class method → returns model string or raises | `@classmethod` — looks up model in `cls.MODELS`, raises `UnsupportedModelError` if missing |
| `configure_model(model)` private instance method | `self._configure_model(model)` |
| `model_info` instance method | Returns `self.MODELS[self.model]` after lookup |
| `context_window`, `input_token_cost_per_million`, `output_token_cost_per_million` | Properties reading from `model_info` dict |
| `estimate_cost(input_tokens:, output_tokens:)` | Same signature, returns `float` or `None` |
| `usage_unit`, `usage_level` | Properties from `model_info` |

Python target (`base.py`):

```python
class Base:
    MODELS: dict[str, dict] = {}

    @classmethod
    def model_info(cls, model):
        return cls.MODELS.get(str(model))

    @classmethod
    def validate_model(cls, model):
        model = str(model)
        if cls.model_info(model):
            return model
        supported = ", ".join(sorted(cls.MODELS.keys()))
        raise UnsupportedModelError(
            f"{cls.__name__} does not support model {model!r}. "
            f"Supported models: {supported}"
        )

    def _configure_model(self, model):
        self.model = self.validate_model(model)
        self._model_info = self.MODELS[self.model]

    @property
    def model_info(self):
        return self._model_info

    @property
    def context_window(self):
        return self.model_info["context_window"]

    @property
    def input_token_cost_per_million(self):
        return self.model_info["cost_per_million"]["input"]

    @property
    def output_token_cost_per_million(self):
        return self.model_info["cost_per_million"]["output"]

    @property
    def usage_unit(self):
        return self.model_info["usage_unit"]

    @property
    def usage_level(self):
        return self.model_info.get("usage_level")

    def estimate_cost(self, input_tokens, output_tokens):
        if self.input_token_cost_per_million is None or self.output_token_cost_per_million is None:
            return None
        return ((input_tokens * self.input_token_cost_per_million) +
                (output_tokens * self.output_token_cost_per_million)) / 1_000_000.0
```

### Backends::Anthropic → `backends/anthropic.py`

| Ruby | Python |
|------|--------|
| `BASE_URL` constant | Class attribute |
| `MODELS` constant hash | Class attribute dict |
| `initialize(api_key:, model:)` | `__init__(self, api_key, model)` |
| `to_messages(messages)` — tool_result → user msg with tool_result content block | Same logic, list of dicts |
| `to_tools(tools)` — `input_schema` envelope | Same |
| `to_payload(context, max_output_tokens:)` | Same |
| `headers` — `x-api-key`, `anthropic-version` | Same dict |
| `url` — returns `BASE_URL` | Same |

### Backends::DeepSeek, OpenAI, Ollama, OllamaCloud

These four share the **same OpenAI-compatible format** — identical
`to_messages`, `to_tools`, `to_payload`, and `headers` shapes. Only `BASE_URL`
and `MODELS` differ.

To avoid duplication, extract the shared logic into `backends/_openai_compatible.py`
as a mixin or base class:

```python
class OpenAICompatibleBase(Base):
    """Shared serialization for OpenAI-compatible APIs (OpenAI, DeepSeek, Ollama, OllamaCloud)."""

    def to_messages(self, system, messages):
        system_msg = [{"role": "system", "content": system}]
        conversation = []
        for msg in messages:
            if msg.role == "tool_result":
                conversation.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_use_id,
                    "content": msg.content,
                })
            else:
                conversation.append({"role": msg.role, "content": msg.content})
        return system_msg + conversation

    def to_tools(self, tools):
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": {
                        "type": "object",
                        "properties": t.parameters,
                        "required": list(t.parameters.keys()),
                    },
                },
            }
            for t in tools.values()
        ]

    def to_payload(self, context, max_output_tokens=1024):
        return {
            "model": self.model,
            "messages": self.to_messages(context.system, context.messages),
            "tools": self.to_tools(context.tools),
            "max_tokens": max_output_tokens,
        }

    def headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def url(self):
        return self.BASE_URL
```

Then each backend is just `BASE_URL` + `MODELS` + `__init__`:

```python
class OpenAI(OpenAICompatibleBase):
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODELS = { ... }

    def __init__(self, api_key, model):
        self.api_key = api_key
        self._configure_model(model)
```

This avoids 4× duplicated `to_messages`/`to_tools`/`to_payload`/`headers`/`url`.

> **Note:** Ollama's `__init__` takes `host` instead of `api_key` and its
> `headers` has no Authorization. It can still inherit from
> `OpenAICompatibleBase` and just override `__init__` + `headers`.

### Backends::Gemini → `backends/gemini.py`

Gemini has its own unique format — no shared base. Direct port from Ruby:

- `BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"`
- `to_messages` — assistant → `role: "model"`, tool_result → `functionResponse` part
- `to_tools` — wrapped in `functionDeclarations` array
- `to_payload` — `systemInstruction` top-level, `contents`, `generationConfig`
- `headers` — `x-goog-api-key`

### PromptBuilder (`prompt_builder.rb` → `prompt_builder.py`)

| Ruby | Python |
|------|--------|
| `def initialize(context, backend)` | `def __init__(self, context, backend)` |
| `to_messages` → delegates to backend | Same |
| `to_tools` → delegates to backend | Same |
| `to_api_payload(max_output_tokens:)` | Same |
| `headers` → delegates to backend | Same |
| `url` → delegates to backend | Same |

### `__init__.py` update

Add imports for `PromptBuilder` and all backends. Update `__all__`:

```python
from boukensha.config import Config
from boukensha.context import Context
from boukensha.errors import UnknownToolError, UnsupportedModelError
from boukensha.message import Message
from boukensha.prompt_builder import PromptBuilder
from boukensha.registry import Registry
from boukensha.tool import Tool
from boukensha.tasks.player import Player
from boukensha.agent import Agent

__all__ = [
    "Agent",
    "Config",
    "Context",
    "Message",
    "Player",
    "PromptBuilder",
    "Registry",
    "Tool",
    "UnknownToolError",
    "UnsupportedModelError",
]
```

### Example (`example.rb` → `example.py`)

Port the Ruby example as the smoke test:

1. Load config, resolve system prompt, build context
2. Register `look` and `move` tools via `@registry.tool()` decorator
3. Add 3 messages (user, assistant, tool_result)
4. Select backend via provider name dispatch:
   - `anthropic` → `Anthropic(api_key=..., model=model)`
   - `deepseek` → `DeepSeek(api_key=..., model=model)`
   - `gemini` → `Gemini(api_key=..., model=model)`
   - `ollama` → `Ollama(model=model)`
   - `ollama_cloud` → `OllamaCloud(api_key=..., model=model)`
   - `openai` → `OpenAI(api_key=..., model=model)`
   - else → `raise ValueError(...)`
5. Build `PromptBuilder(ctx, backend)` and print `json.dumps(builder.to_api_payload(), indent=2)`

> **Note:** Ruby uses symbols (`:user`, `:assistant`, `:tool_result`) for
> message roles. Python uses strings. The backend `to_messages` methods must
> check against string role names.

---

## Dependencies

Unchanged from step 2:

| Python Package |
|---------------|
| `python-dotenv` |
| `pyyaml` |

`json` is stdlib. No new packages.

---

## Project Structure (target)

```
week1_baseline/python/03_prompt_builder/
├── requirements.txt            # unchanged
├── README.md                   # replaced with step 3 content
├── boukensha/
│   ├── __init__.py             # updated — adds PromptBuilder, backends, UnsupportedModelError
│   ├── config.py               # unchanged
│   ├── agent.py                # unchanged
│   ├── context.py              # unchanged
│   ├── errors.py               # updated — adds UnsupportedModelError
│   ├── message.py              # unchanged
│   ├── prompt_builder.py       # NEW
│   ├── registry.py             # unchanged
│   ├── tool.py                 # unchanged
│   ├── backends/
│   │   ├── __init__.py         # NEW (empty)
│   │   ├── _openai_compatible.py  # NEW — shared base for OpenAI-style APIs
│   │   ├── base.py             # NEW
│   │   ├── anthropic.py        # NEW
│   │   ├── deepseek.py         # NEW
│   │   ├── gemini.py           # NEW
│   │   ├── ollama.py           # NEW
│   │   ├── ollama_cloud.py     # NEW
│   │   └── openai.py           # NEW
│   └── tasks/
│       ├── __init__.py         # unchanged
│       ├── base.py             # unchanged
│       └── player.py           # unchanged
├── examples/
│   └── example.py              # replaced
├── prompts/
│   └── system.md               # unchanged (already present)
```

---

## Behavior Parity Checklist

- [ ] `UnsupportedModelError` added to `errors.py`
- [ ] `backends/base.py` — `Base` class with `MODELS`, `validate_model()`, `_configure_model()`, cost + window properties
- [ ] `backends/_openai_compatible.py` — shared serialization for OpenAI/DeepSeek/Ollama/OllamaCloud
- [ ] `backends/anthropic.py` — `BASE_URL`, `MODELS`, `to_messages` (tool_result as user+content block), `to_tools` (input_schema), `to_payload`, `headers` (x-api-key)
- [ ] `backends/deepseek.py` — `BASE_URL`, `MODELS`, inherits from `OpenAICompatibleBase`
- [ ] `backends/openai.py` — `BASE_URL`, `MODELS`, inherits from `OpenAICompatibleBase`
- [ ] `backends/ollama.py` — inherits from `OpenAICompatibleBase`, overrides `__init__` (host, no api_key) and `headers` (no auth)
- [ ] `backends/ollama_cloud.py` — inherits from `OpenAICompatibleBase`
- [ ] `backends/gemini.py` — standalone, own `to_messages` (model role, functionResponse), `to_tools` (functionDeclarations), `to_payload` (systemInstruction)
- [ ] `prompt_builder.py` — delegates `to_messages`, `to_tools`, `to_api_payload`, `headers`, `url` to backend
- [ ] `__init__.py` updated with PromptBuilder + backend imports + `__all__`

---

## Expected Output

```
=== BOUKENSHA Step 3: Prompt Builder ===

Config: #<Boukensha::Config dir=.../.boukensha tasks=player>
Provider: deepseek
Model: deepseek-v4-pro
{
  "model": "deepseek-v4-pro",
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "I just arrived in the dungeon..." },
    { "role": "assistant", "content": "Let me take a look around first." },
    { "role": "tool", "tool_call_id": "toolu_01X", "content": "A damp stone corridor..." }
  ],
  "tools": [ ... ],
  "max_tokens": 1024
}
```

Exact provider/model/system-prompt values depend on the user's `.boukensha/`.

---

## Note: bin/ structure

```
week1_baseline/bin/
├── ruby/03_prompt_builder      ← existing
└── python/03_prompt_builder    ← NEW
```

Same explicit-venv convention:

```bash
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/../../.."
cd "$SCRIPT_DIR/../../python/03_prompt_builder"
"$REPO_ROOT/.venv/bin/python" examples/example.py
```

---

## Implementation Steps

1. Confirm snapshot is a copy of step 2 (README says "Step 2", example uses `@registry.tool()`)
2. Create `boukensha/backends/` package (`__init__.py`)
3. Create `boukensha/backends/base.py` — `Base` class
4. Create `boukensha/backends/_openai_compatible.py` — shared OpenAI-style serialization
5. Create `boukensha/backends/anthropic.py`
6. Create `boukensha/backends/deepseek.py`
7. Create `boukensha/backends/openai.py`
8. Create `boukensha/backends/ollama.py`
9. Create `boukensha/backends/ollama_cloud.py`
10. Create `boukensha/backends/gemini.py`
11. Create `boukensha/prompt_builder.py`
12. Update `boukensha/errors.py` — add `UnsupportedModelError`
13. Update `boukensha/__init__.py` — add PromptBuilder + backends + `__all__`
14. Replace `examples/example.py`
15. Replace `README.md`
16. Create `bin/python/03_prompt_builder`, make executable
17. Run smoke test — verify JSON payload output

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | DRY up OpenAI-compatible backends? | **Yes — `_openai_compatible.py` base** | OpenAI, DeepSeek, Ollama, OllamaCloud share identical serialization. Extract it once, inherit 4 times |
| 2 | `_openai_compatible.py` naming? | **Underscore prefix** | `_openai_compatible` signals it's internal — not exported in `__all__` |
| 3 | Ruby symbols → Python strings for roles? | **Strings** | `:user` → `"user"`, `:assistant` → `"assistant"`, `:tool_result` → `"tool_result"` |
| 4 | Backend selection in example? | **if/elif chain** | Matches Ruby's `case/when`. Could use a dict dispatch, but if/elif is a closer 1:1 port |
| 5 | DeepSeek backend? | **Yes** | Added to Ruby side in the previous task — port it as a first-class backend |
| 6 | `prompts/system.md`? | **Already present** | Carried from step 0 copy; identical to Ruby version |
| 7 | New dependencies? | **No** | `json` is stdlib |

---

## Out of Scope (future steps)

- Actually calling the API (POST to `backend.url` with `backend.headers` and payload)
- Parsing API responses
- The agent loop that uses `PromptBuilder` + HTTP client
- Token budget enforcement
