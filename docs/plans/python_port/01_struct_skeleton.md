# Plan: Port 01_struct_skeleton from Ruby → Python

## Overview

Port `week1_baseline/ruby/01_struct_skeleton` to Python as
`week1_baseline/python/01_struct_skeleton/`.

`week1_baseline/python/01_struct_skeleton` has already been created by copying
the completed `week1_baseline/python/00_config` port. This plan is therefore
only for the **step 1 delta**: compare Ruby `00_config` to Ruby
`01_struct_skeleton`, then apply only those new changes to the existing Python
snapshot.

This step introduces three lightweight data structures — `Tool`, `Message`,
`Context` — that will carry state through the agentic loop.

---

## What's new vs 00_config

| Component | Status |
|-----------|--------|
| `Config`, `Tasks::Base`, `Tasks::Player` | Unchanged — already present from 00_config copy |
| `Agent` | Unchanged — kept from 00_config copy (Ruby side drops `agent.rb`, but we leave the Python file as-is) |
| `prompts/system.md` | Unchanged — already present from 00_config copy |
| `Tool` | NEW |
| `Message` | NEW |
| `Context` | NEW |

---

## Files to Port (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | Update — add Tool, Message, Context exports |
| `lib/boukensha/tool.rb` | → | `boukensha/tool.py` | Create |
| `lib/boukensha/message.rb` | → | `boukensha/message.py` | Create |
| `lib/boukensha/context.rb` | → | `boukensha/context.py` | Create |
| `examples/example.rb` | → | `examples/example.py` | Replace |
| `README.md` | → | `README.md` | Replace with step 1 content |
| `bin/ruby/01_struct_skeleton` | → | `bin/python/01_struct_skeleton` | Create launcher |

`config.py`, `tasks/`, `agent.py`, `requirements.txt`, and `prompts/system.md`
are already present from the copied 00_config port and do not change.

---

## Mapping: Ruby → Python (new structs only)

### Tool (`tool.rb` → `tool.py`)

Ruby uses `Struct.new(:name, :description, :parameters, :block)` with a block
for custom methods. Python equivalent: `@dataclass`.

| Ruby | Python |
|------|--------|
| `Tool = Struct.new(:name, :description, :parameters, :block)` | `@dataclass class Tool:` |
| Struct members | Dataclass fields with type hints |
| `block` (lambda) | `block: Callable[..., Any] \| None = None` |
| `parameters.keys` | `list(parameters.keys())` — Python's `['direction']` won't match Ruby's `[:direction]`, acceptable |
| `description[0..40]` truncation | `description[:40]` |
| `to_s` in Struct block | `__str__` + `__repr__` |

### Message (`message.rb` → `message.py`)

| Ruby | Python |
|------|--------|
| `Struct.new(:role, :content, :tool_use_id)` | `@dataclass class Message:` |
| `tool_use_id` (nil default) | `tool_use_id: str \| None = None` |
| `"[#{tool_use_id}]"` tag when present | Same logic, f-string |
| `content[0..60]` truncation + `...` | `content[:60] + "..."` |

### Context (`context.rb` → `context.py`)

Plain Ruby class → plain Python class.

| Ruby | Python |
|------|--------|
| `attr_reader :task, :system, :messages, :tools` | Instance attributes in `__init__` |
| `@messages = []` | `self.messages: list[Message] = []` |
| `@tools = {}` | `self.tools: dict[str, Tool] = {}` |
| `register_tool(tool)` → `@tools[tool.name]` | Same |
| `add_message(role, content, tool_use_id:)` | Same signature |
| `tool_count` / `turn_count` | `@property` returning `len()` |
| `to_s` → `#<Context task=#{task.task_name} ...>` | `__str__` calls `self.task.task_name()` |

> **Key detail:** `Context.__str__` calls `task.task_name()` so
> `Context(task=Player, ...)` prints `task=player`. Context stores `system` but
> does **not** print it in `__str__`, matching the Ruby implementation.

---

## Dependencies

Unchanged from 00_config:

| Python Package |
|---------------|
| `python-dotenv` |
| `pyyaml` |

No new packages — `dataclasses` is stdlib (Python 3.10).

---

## Project Structure (target)

```
week1_baseline/python/01_struct_skeleton/
├── requirements.txt            # unchanged (from 00_config copy)
├── README.md                   # replaced with step 1 content
├── boukensha/
│   ├── __init__.py             # updated — adds Tool, Message, Context exports
│   ├── config.py               # unchanged (from 00_config copy)
│   ├── agent.py                # unchanged (from 00_config copy)
│   ├── tool.py                 # NEW — @dataclass
│   ├── message.py              # NEW — @dataclass
│   ├── context.py              # NEW — class
│   └── tasks/
│       ├── __init__.py         # unchanged
│       ├── base.py             # unchanged
│       └── player.py           # unchanged
├── examples/
│   └── example.py              # replaced with step 1 smoke test
└── prompts/
    └── system.md               # unchanged (from 00_config copy)
```

---

## Behavior Parity Checklist

- [ ] `Tool` dataclass: `name`, `description`, `parameters`, `block` (default `None`)
- [ ] `Tool.__str__` truncates description to 40 chars, shows `parameters.keys()`
- [ ] `Message` dataclass: `role`, `content`, `tool_use_id` (default `None`)
- [ ] `Message.__str__` includes `[tool_use_id]` tag only when present, truncates content to 60 chars + `...`
- [ ] `Context` class: `task`, `system` (default `None`), `messages`, `tools`
- [ ] `Context.register_tool(tool)` stores by `tool.name`
- [ ] `Context.add_message(role, content, tool_use_id=None)` appends a `Message`
- [ ] `Context.tool_count` / `Context.turn_count` properties
- [ ] `Context.__str__` calls `task.task_name()` → prints `task=player`
- [ ] `Context.__str__` does NOT print `system`
- [ ] `boukensha/__init__.py` exports `Config`, `Player`, `Tool`, `Message`, `Context` (+ `Agent`)
- [ ] Config & Tasks behaviour unchanged from 00_config
- [ ] Smoke test output matches expected format

---

## Note: bin/ structure

```
week1_baseline/bin/
├── ruby/01_struct_skeleton     ← existing
└── python/01_struct_skeleton   ← NEW
```

The Python launcher uses the explicit venv path (consistent with the updated
`bin/python/00_config`):

```bash
#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/../../.."

cd "$SCRIPT_DIR/../../python/01_struct_skeleton"
"$REPO_ROOT/.venv/bin/python" examples/example.py
```

---

## Implementation Steps

1. Confirm `week1_baseline/python/01_struct_skeleton/` exists as a copy of `00_config`
2. Compare Ruby `00_config` and Ruby `01_struct_skeleton` to confirm delta: `tool.rb`, `message.rb`, `context.rb` new; top-level exports, README, example changed
3. Add `boukensha/tool.py`, `boukensha/message.py`, `boukensha/context.py`
4. Update `boukensha/__init__.py` to export `Tool`, `Message`, `Context`
5. Replace `examples/example.py` with step 1 smoke test
6. Replace `README.md` with step 1 content + venv setup instructions
7. Create `bin/python/01_struct_skeleton` launcher, make executable
8. Run smoke test through launcher — verify exit 0 and expected output

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Struct → Python equivalent? | **`@dataclass`** | `dataclasses` is stdlib in 3.10, lightweight, readable — closest match to Ruby's `Struct` intent |
| 2 | Carry `Agent` forward? | **Leave as-is** | File is already present from 00_config copy; no reason to delete it |
| 3 | Carry `prompts/system.md`? | **Leave as-is** | Already present from 00_config copy |
| 4 | New dependencies? | **No** | `dataclasses` is stdlib. `requirements.txt` unchanged |
| 5 | Launcher style? | **Explicit venv path** | `$REPO_ROOT/.venv/bin/python` — consistent with updated 00_config launcher, doesn't require venv activation |
| 6 | `block` field default? | **`None`** | `Callable[..., Any] \| None = None` — optional, matches instructor spec |
| 7 | `Context.__str__` uses `task.task_name()`? | **Yes** | Calls `self.task.task_name()` so it prints `task=player` instead of `task=<class ...>` |

---

## Out of Scope (future steps)

- API calls — `Context` holds everything needed for an API call, but we don't make one yet
- Multi-turn loops
- Token budget enforcement
- The actual LLM provider integration
