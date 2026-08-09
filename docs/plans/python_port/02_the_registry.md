# Plan: Port 02_the_registry from Ruby → Python

## Overview

Port `week1_baseline/ruby/02_the_registry` to Python as
`week1_baseline/python/02_the_registry/`.

The Python snapshot already exists as a copy of `01_struct_skeleton` (README
still says "Step 1: Struct Skeleton", example still registers tools directly on
`Context`). This plan covers only the **step 2 delta**: compare Ruby
`01_struct_skeleton` to Ruby `02_the_registry`, then apply those changes to the
existing Python snapshot.

This step introduces the **Tool Registry** — the dispatcher that sits between
the agent and the tools. The agent never calls a tool directly; it emits a
structured request (name + args) and the Registry looks up the tool and runs
it. A custom error class signals unknown-tool failures explicitly.

Do not introduce API clients, a runtime/agent loop, formal tests, or the
Context/Registry data-ownership rework that the Ruby README flags as still
outstanding — that rework is explicitly deferred to a future step on the Ruby
side, so the Python port should faithfully reproduce the same not-yet-fixed
state.

---

## What's new vs 01_struct_skeleton

| Component | Status |
|-----------|--------|
| `Config`, `Tasks::Base`, `Tasks::Player` | Unchanged |
| `Tool`, `Message` | Unchanged |
| `Context` | Unchanged — a stray `# This isn'` comment appears above `register_tool` in the Ruby source; do **not** port it, it's an editing artifact with no meaning |
| `Registry` | NEW — stores tools and dispatches calls |
| `UnknownToolError` | NEW — raised on dispatch to unregistered tool name |
| `boukensha.rb` (top-level exports) | Updated — adds errors + registry requires |
| `examples/example.rb` | Replaced — uses Registry instead of direct Context registration |
| `README.md` | Replaced with step 2 content |

No new dependencies — `Gemfile` unchanged (just `dotenv`).

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/errors.rb` | → | `boukensha/errors.py` | **Create** |
| `lib/boukensha/registry.rb` | → | `boukensha/registry.py` | **Create** |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** — add Registry, UnknownToolError exports + `__all__` |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |

All other files (`config.py`, `context.py`, `tool.py`, `message.py`, `tasks/`,
`agent.py`, `prompts/system.md`, `requirements.txt`) remain unchanged from the
01_struct_skeleton copy.

---

## Mapping: Ruby → Python (new files only)

### UnknownToolError (`errors.rb` → `errors.py`)

```ruby
class UnknownToolError < StandardError; end
```

Python:

```python
class UnknownToolError(Exception):
    """Raised when dispatch is called with an unregistered tool name."""
```

Trivial — a single custom exception. `Exception` is the direct equivalent of
Ruby's `StandardError`. No custom base error class exists on the Ruby side to
mirror.

### Registry (`registry.rb` → `registry.py`)

Ruby:

```ruby
class Registry
  def initialize(context)
    @context = context
  end

  def tool(name, description:, parameters: {}, &block)
    tool = Tool.new(name.to_s, description, parameters, block)
    @context.register_tool(tool)
    tool
  end

  def dispatch(name, args = {})
    tool = @context.tools[name.to_s]
    raise UnknownToolError, "No tool registered as '#{name}'" unless tool
    tool.block.call(**args.transform_keys(&:to_sym))
  end
end
```

Python target — **decorator approach** for `tool()`:

```python
from .errors import UnknownToolError
from .tool import Tool


class Registry:
    def __init__(self, context):
        self.context = context

    def tool(self, name, description, parameters=None):
        """Register a tool on the context. Returns a decorator."""
        def decorator(block):
            registered = Tool(str(name), description, parameters or {}, block)
            self.context.register_tool(registered)
            return block
        return decorator

    def dispatch(self, name, args=None):
        tool = self.context.tools.get(str(name))
        if tool is None:
            raise UnknownToolError(f"No tool registered as '{name}'")
        return tool.block(**(args or {}))
```

> **Why a decorator?** Ruby's trailing-block call syntax
> (`registry.tool("move", description: ...) do |direction:| ... end`) has no
> direct Python equivalent. The closest Pythonic match is a decorator factory:
> `@registry.tool("move", description="...", parameters={...})` followed by a
> function definition. The decorator builds the `Tool`, registers it on the
> context, and returns the function unchanged (so it stays usable/testable on
> its own).

> **No symbol/string key translation in `dispatch`.** Ruby's `dispatch` does
> `args.transform_keys(&:to_sym)` because JSON/API args arrive as strings but
> Ruby blocks with keyword args (`|direction:|`) require symbol keys. Python
> has no such duality — `tool.block(**args)` works directly against a
> string-keyed dict. Add a one-line comment noting why the conversion step is
> unnecessary in Python.

| Ruby | Python |
|------|--------|
| `def initialize(context)` | `def __init__(self, context)` |
| `tool(name, description:, parameters: {}, &block)` | `tool(self, name, description, parameters=None)` → returns decorator |
| `Tool.new(name.to_s, description, parameters, block)` | `Tool(str(name), description, parameters or {}, block)` inside decorator |
| `dispatch(name, args = {})` | `dispatch(self, name, args=None)` |
| `@context.tools[name.to_s]` | `self.context.tools.get(str(name))` |
| `raise UnknownToolError unless tool` | `if tool is None: raise UnknownToolError(...)` |
| `tool.block.call(**args.transform_keys(&:to_sym))` | `tool.block(**(args or {}))` |

### `__init__.py` update

Add exports for `Registry` and `UnknownToolError`, plus an explicit `__all__`
list to match the public surface:

```python
from .config import Config
from .context import Context
from .errors import UnknownToolError
from .message import Message
from .registry import Registry
from .tasks.player import Player
from .tool import Tool

__all__ = [
    "Config",
    "Context",
    "Message",
    "Player",
    "Registry",
    "Tool",
    "UnknownToolError",
]
```

---

## Dependencies

Unchanged:

| Python Package |
|---------------|
| `python-dotenv` |
| `pyyaml` |

No new packages needed.

---

## Project Structure (target)

```
week1_baseline/python/02_the_registry/
├── requirements.txt            # unchanged
├── README.md                   # replaced with step 2 content
├── boukensha/
│   ├── __init__.py             # updated — adds Registry, UnknownToolError, __all__
│   ├── config.py               # unchanged
│   ├── agent.py                # unchanged
│   ├── context.py              # unchanged (stray comment NOT ported)
│   ├── errors.py               # NEW — UnknownToolError
│   ├── message.py              # unchanged
│   ├── registry.py             # NEW — Registry with decorator-based tool()
│   ├── tool.py                 # unchanged
│   └── tasks/
│       ├── __init__.py         # unchanged
│       ├── base.py             # unchanged
│       └── player.py           # unchanged
├── examples/
│   └── example.py              # replaced — uses @registry.tool() decorator
└── prompts/
    └── system.md               # unchanged
```

---

## Behavior Parity Checklist

- [ ] `UnknownToolError` inherits from `Exception`
- [ ] `Registry.__init__` stores `context`
- [ ] `Registry.tool(name, description, parameters)` returns a decorator
- [ ] Decorator builds a `Tool`, registers it on `context`, returns the function unchanged
- [ ] `Registry.dispatch(name, args)` looks up tool by name in `context.tools`
- [ ] `Registry.dispatch` raises `UnknownToolError` when tool name not found
- [ ] `Registry.dispatch` calls `tool.block(**args)` with unpacked keyword arguments
- [ ] `Registry.dispatch` accepts `args=None` (defaults to empty dict)
- [ ] `boukensha/__init__.py` has explicit `__all__` with all 7 exports
- [ ] Example registers tools via `@registry.tool(...)` decorator
- [ ] `parameters` dicts match Ruby step 2 exactly — step 2 drops the inner `description` key that step 1 had (e.g. `{"direction": {"type": "string"}}`, not `{"direction": {"type": "string", "description": "The direction to move"}}`)
- [ ] Example dispatches `"shout"` and `"move"` with string-keyed args
- [ ] Example catches `UnknownToolError` for unregistered tool `"flee"` — does **not** crash
- [ ] Output matches expected format (real context output, not aspirational)

---

## Expected Output

```
=== BOUKENSHA Step 2: Tool Registry ===

Config:  #<Boukensha::Config dir=.../.boukensha tasks=player>
Context: #<Context task=player turns=0 tools=2>
Tools:
  #<Tool name=move description=Move the player in a direction (north, s params=['direction']>
  #<Tool name=shout description=Shout a message so everyone in the zone  params=['message']>

Dispatching 'shout' with message='dragon spotted'...
Result: DRAGON SPOTTED

Dispatching 'move' with direction='north'...
Result: You move north into a torch-lit corridor.

UnknownToolError caught: No tool registered as 'flee'
```

> **Note:** The Ruby README's "Expected Output" section shows an aspirational
> `#<Context turns=0 tools=2 budget=8192>` that does **not** match what
> `context.rb`'s actual `to_s` produces (no `budget` field, missing `task=`).
> The Python port outputs the **real** string (`#<Context task=player turns=0
> tools=2>`), matching the actual code, not the Ruby README's out-of-sync
> example. The Python README should show the real output as well.

---

## Note: bin/ structure

```
week1_baseline/bin/
├── ruby/02_the_registry        ← existing
└── python/02_the_registry      ← NEW
```

Launcher follows the same explicit-venv convention:

```bash
#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/../../.."

cd "$SCRIPT_DIR/../../python/02_the_registry"
"$REPO_ROOT/.venv/bin/python" examples/example.py
```

---

## Implementation Steps

1. Confirm `week1_baseline/python/02_the_registry/` exists as a copy of `01_struct_skeleton` (README/example still say "Step 1")
2. Create `boukensha/errors.py` — `UnknownToolError(Exception)`
3. Create `boukensha/registry.py` — `Registry` with decorator-based `tool()` and `dispatch()`
4. Update `boukensha/__init__.py` — add `Registry` and `UnknownToolError` exports + `__all__`
5. Replace `examples/example.py` with step 2 smoke test using `@registry.tool()` decorator
6. Replace `README.md` with step 2 content (fix Ruby README bugs: real Context output, correct run command path, keep both `## Considerations` sections)
7. Create `bin/python/02_the_registry` launcher, make executable
8. Run smoke test through launcher — verify exit 0 and expected output

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | `Registry.tool()` API style? | **Decorator factory** | `@registry.tool(name, description=..., parameters=...)` — closest Pythonic match to Ruby's trailing-block syntax. Returns the function unchanged so it stays callable/testable |
| 2 | `args` key conversion (string → symbol)? | **Not needed in Python** | Python `**` unpacking works directly with string keys. Add a comment noting why this Ruby step is skipped |
| 3 | `args` / `parameters` default values? | **`None`** (converted to `{}` internally) | Matches Python convention for mutable defaults |
| 4 | New dependencies? | **No** | `requirements.txt` unchanged |
| 5 | `__all__` in `__init__.py`? | **Yes** | Explicit list of all 7 public exports |
| 6 | Stray comment `# This isn'` in `context.rb`? | **Do not port** | Editing artifact with no meaning |
| 7 | README: reproduce Ruby doc bugs? | **Fix them** | Use real Context output (no `budget`), correct run command path |
| 8 | `parameters` drift from step 1? | **Port exactly** | Step 2 drops the inner `description` key; don't restore it |
| 9 | `Context`/`Registry` data overlap? | **Leave as-is** | Ruby README flags this for a future fix; replicate the same imperfect state |

---

## Open Questions

1. **Decorator convention confirmed?** This plan adopts the decorator approach
   for `Registry.tool()`. Since it sets the convention for tool registration in
   all later steps, it should be confirmed before execution.
2. **README: duplicate `## Considerations` headings?** The Ruby README has two
   separate `## Considerations` sections (one about symbol/string key
   translation in `dispatch`, one about the Context/Registry ownership
   gotcha). The Python README should preserve both as separate sections
   (faithful port) rather than merging them, even though it reads as an
   editing artifact.

---

## Out of Scope (future steps)

- The agent loop that decides *when* to call `registry.dispatch()`
- API client / LLM provider integration
- Token budget enforcement
- Multi-turn conversations with the actual model
- Context/Registry data-ownership rework (deferred on Ruby side too)
