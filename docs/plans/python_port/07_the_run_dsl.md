# Plan: Port 07_the_run_dsl from Ruby → Python

## Overview

Port `week1_baseline/ruby/07_the_run_dsl` to Python as
`week1_baseline/python/07_the_run_dsl/`.

The Python snapshot is a copy of `06_the_logger`. This step adds
`Boukensha.run()` — a high-level entry point that hides all manual wiring
(Context, Registry, Backend, PromptBuilder, Client, Logger, Agent) behind a
single function call with a tool-registration block.

---

## What's new vs 06_the_logger

| Component | Status |
|-----------|--------|
| `RunDSL` | NEW — host object for the `tool` block, wraps `Registry` |
| `boukensha.run()` | NEW — top-level function in `__init__.py` that wires everything internally |
| `__init__.py` | Updated — adds `RunDSL` import + `run()` function |
| `examples/example.rb` | Replaced — uses `Boukensha.run(task: ...)` |
| `README.md` | Replaced |
| All backends, Agent, Logger, Client, PromptBuilder, Registry, Context, Config, Tasks | Unchanged |

No new dependencies.

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/run_dsl.rb` | → | `boukensha/run_dsl.py` | **Create** |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** — add `RunDSL` + `run()` function |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |
| — | → | `bin/python/07_the_run_dsl` | **Create** launcher |

---

## Mapping: Ruby → Python

### RunDSL (`run_dsl.rb` → `run_dsl.py`)

| Ruby | Python |
|------|--------|
| `class RunDSL` — `instance_eval(&block)` host | Plain class — `tool` method delegates to registry |
| `def initialize(registry)` | `def __init__(self, registry)` |
| `@registry = registry` | `self._registry = registry` |
| `tool(name, description:, parameters: {}, &block)` | `tool(self, name, description, parameters=None, block=None)` → calls `self._registry.tool(name, description, parameters)(block)` |

> **Key difference:** Ruby uses `instance_eval(&block)` so `self` inside the
> block is the `RunDSL` instance, making `tool "name", ... do ... end` work
> naturally. Python doesn't have `instance_eval`. Instead, `Boukensha.run()`
> passes the `RunDSL` instance as an argument to the user's callback:
>
> ```python
> Boukensha.run(task="...", tools=lambda dsl: [
>     dsl.tool("read_file", description="...", parameters={...})(read_file),
> ])
> ```
>
> Or more Pythonically, use the decorator style we already have:
>
> ```python
> def run(task, ...):
>     ...
>     dsl = RunDSL(registry)
>     if tools_callback:
>         tools_callback(dsl)
>     ...
> ```
>
> The user writes:
>
> ```python
> def register_tools(dsl):
>     @dsl.tool("read_file", description="...", parameters={...})
>     def read_file(path):
>         return Path(path).read_text()
>
> Boukensha.run(task="...", tools=register_tools)
> ```

### `Boukensha.run()` function (in `__init__.py`)

Ruby's `Boukensha.run` is a class method that:

1. Loads config (`.env` + `settings.yaml`)
2. Resolves defaults: `system`, `model`, `backend`, `api_key`
3. Creates `Context`, `Registry`
4. `instance_eval`'s the block against `RunDSL` to register tools
5. Creates backend (dispatch on `:anthropic`, `:deepseek`, `:openai`, `:gemini`, `:ollama`, `:ollama_cloud`)
6. Creates `PromptBuilder`, `Client`, `Logger`, `Agent`
7. Adds user message, calls `agent.run()`
8. Ensures `logger.close()`

Python translation — `boukensha.run()` function in `__init__.py`:

```python
def run(
    task,
    *,
    system=None,
    model=None,
    backend=None,
    api_key=None,
    ollama_host="http://localhost:11434",
    log=None,
    max_output_tokens=None,
    tools=None,
):
    import os
    from boukensha.config import Config
    from boukensha.context import Context
    from boukensha.registry import Registry
    from boukensha.run_dsl import RunDSL
    from boukensha.prompt_builder import PromptBuilder
    from boukensha.client import Client
    from boukensha.logger import Logger
    from boukensha.agent import Agent
    from boukensha.tasks.player import Player

    cfg = Config()
    set_config(cfg)

    task_class = Player
    task_settings = cfg.tasks(task_class.task_name())

    if system is None:
        system = task_class.system_prompt(
            task_settings,
            user_prompts_dir=cfg.user_prompts_dir,
            default_prompts_dir=str(Config.PROMPTS_DIR),
        )
    if model is None:
        model = task_class.model(task_settings)
    if backend is None:
        backend = task_class.provider(task_settings)

    # Resolve api_key
    if api_key is None:
        key_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "ollama_cloud": "OLLAMA_API_KEY",
        }
        api_key = os.environ.get(key_map.get(backend, ""))

    ctx = Context(task=task_class, system=system)
    registry = Registry(ctx)

    if tools:
        dsl = RunDSL(registry)
        tools(dsl)

    # Build backend
    from boukensha.backends.anthropic import Anthropic
    from boukensha.backends.deepseek import DeepSeek
    from boukensha.backends.openai import OpenAI
    from boukensha.backends.gemini import Gemini
    from boukensha.backends.ollama import Ollama
    from boukensha.backends.ollama_cloud import OllamaCloud

    backend_map = {
        "anthropic": lambda: Anthropic(api_key=api_key, model=model),
        "deepseek": lambda: DeepSeek(api_key=api_key, model=model),
        "openai": lambda: OpenAI(api_key=api_key, model=model),
        "gemini": lambda: Gemini(api_key=api_key, model=model),
        "ollama": lambda: Ollama(host=ollama_host, model=model),
        "ollama_cloud": lambda: OllamaCloud(api_key=api_key, model=model),
    }
    if backend not in backend_map:
        raise ValueError(
            f"Unknown backend {backend!r}. "
            f"Use: {', '.join(backend_map.keys())}"
        )
    be = backend_map[backend]()

    builder = PromptBuilder(ctx, be)
    client = Client(builder)
    logger = Logger(log=log, snapshot={
        "task": task_class.task_name(),
        "max_iterations": task_class.max_iterations(task_settings),
        "max_output_tokens": max_output_tokens or task_class.max_output_tokens(task_settings),
        "model": model,
        "provider": backend,
    })
    agent = Agent(
        context=ctx, registry=registry, builder=builder, client=client,
        logger=logger, task_settings=task_settings,
        max_iterations=task_class.max_iterations(task_settings),
        max_output_tokens=max_output_tokens or task_class.max_output_tokens(task_settings),
    )

    ctx.add_message("user", task)
    try:
        return agent.run()
    finally:
        logger.close()
```

### Example (`example.rb` → `example.py`)

Before (step 6 — ~80 lines):

```python
config = Config()
ctx = Context(task=Player, ...)
registry = Registry(ctx)
backend = DeepSeek(...)
builder = PromptBuilder(ctx, backend)
client = Client(builder)
logger = Logger()
agent = Agent(context=ctx, registry=registry, ...)
# ... tool registration, etc.
result = agent.run()
```

After (step 7 — ~20 lines):

```python
import boukensha
boukensha.set_config(Config())

def register_tools(dsl):
    @dsl.tool("read_file", description="...", parameters={...})
    def read_file(path):
        return Path(base_dir, path).read_text()

    @dsl.tool("list_directory", description="...", parameters={...})
    def list_directory(path):
        ...

result = boukensha.run(
    task="Read the README.md file and summarise...",
    tools=register_tools,
)
```

---

## Dependencies

Unchanged. No new packages.

---

## Project Structure (target)

```
week1_baseline/python/07_the_run_dsl/
├── requirements.txt              # unchanged
├── README.md                     # replaced
├── boukensha/
│   ├── __init__.py               # updated — run_dsl + run() function
│   ├── run_dsl.py                # NEW
│   ├── ...                       # all other files unchanged
├── examples/
│   └── example.py                # replaced — uses boukensha.run()
```

---

## Behavior Parity Checklist

- [ ] `RunDSL.__init__` stores registry
- [ ] `RunDSL.tool(name, description, parameters, block)` calls `registry.tool(name, description, parameters)(block)`
- [ ] `boukensha.run()` accepts `task`, `system`, `model`, `backend`, `api_key`, `ollama_host`, `log`, `max_output_tokens`, `tools`
- [ ] `run()` resolves defaults from `Config`/`settings.yaml` when kwargs are `None`
- [ ] `run()` auto-resolves `api_key` from env vars based on backend
- [ ] `run()` supports all 6 backends: anthropic, deepseek, openai, gemini, ollama, ollama_cloud
- [ ] `run()` creates and wires all plumbing internally
- [ ] `run()` passes `RunDSL` to `tools` callback for registration
- [ ] `run()` closes logger in `finally` block
- [ ] Example is ~20 lines vs ~80 lines in step 6
- [ ] Smoke test produces same agent behavior as step 6

---

## Expected Output

```
=== BOUKENSHA Step 7: The Boukensha.run DSL ===

Config: #<Boukensha::Config dir=.../.boukensha tasks=player>

... (agent run output) ...

=== FINAL RESPONSE ===
... (model's text response)
```

---

## Implementation Steps

1. Copy `python/06_the_logger` → `python/07_the_run_dsl`
2. Create `boukensha/run_dsl.py`
3. Update `boukensha/__init__.py` — add `RunDSL` import + `run()` function
4. Replace `examples/example.py`
5. Create `bin/python/07_the_run_dsl`, make executable
6. Run smoke test

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | `instance_eval` equivalent? | **Callback with `dsl` argument** | User passes `tools=lambda dsl: ...` instead of Ruby's magic `self` swap |
| 2 | `RunDSL.tool()` API? | **Decorator factory** | `@dsl.tool(name, description=..., parameters=...)` — consistent with Registry pattern |
| 3 | Backend dispatch? | **Dict of lambdas** | Cleaner than if/elif chain, matches Ruby's `case/when` intent |
| 4 | New dependencies? | **No** | |
| 5 | DeepSeek? | **Included** | Full first-class backend in `run()` |

---

## Out of Scope

- All future steps (this is the final baseline step)
