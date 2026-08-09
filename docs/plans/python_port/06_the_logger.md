# Plan: Port 06_the_logger from Ruby → Python

## Overview

Port `week1_baseline/ruby/06_the_logger` to Python as
`week1_baseline/python/06_the_logger/`.

The Python snapshot is a copy of `05_agent_loop`. This is a small step — one
new class (`Logger`) wired into the Agent loop. The Logger writes structured
JSON Lines (`.jsonl`) files recording every phase of an agent run: iterations,
tool calls, tool results, responses (with token usage and cost), and optional
raw API payloads.

---

## What's new vs 05_agent_loop

| Component | Status |
|-----------|--------|
| `Logger` | NEW — JSONL file logger |
| `Agent` | Updated — `logger:` parameter, log calls at every lifecycle event, `try/except` on tool dispatch |
| `boukensha.rb` | Updated — module-level `debug!`/`quiet!`/`config`, logger require |
| `boukensha/__init__.py` | Updated — add `Logger` export, module-level `config`/`debug` |
| `examples/example.rb` | Updated — creates `Logger`, passes to `Agent`, adds `deepseek` case |
| `README.md` | Replaced |
| All backends, PromptBuilder, Client, Config, Context, Registry, Tasks | Unchanged |

No new dependencies — `json`, `os`, `time`, `secrets` are stdlib.

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/logger.rb` | → | `boukensha/logger.py` | **Create** |
| `lib/boukensha/agent.rb` | → | `boukensha/agent.py` | **Update** — add logger calls, try/except on dispatch |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** — add Logger, module-level `config`/`debug` |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |
| — | → | `bin/python/06_the_logger` | **Create** launcher |

---

## Mapping: Ruby → Python

### Logger (`logger.rb` → `logger.py`)

| Ruby | Python |
|------|--------|
| `require "json"` | `import json` (stdlib) |
| `require "fileutils"` | `from pathlib import Path` + `Path.mkdir(parents=True)` |
| `require "securerandom"` | `import secrets` (stdlib) |
| `require "time"` | `from datetime import datetime, timezone` |
| `DEFAULT_SESSION_DIR = "sessions"` | Class constant |
| `initialize(session_id:, dir:, log:, snapshot:)` | `__init__` with same kwargs + defaults |
| `FileUtils.mkdir_p(...)` | `Path(path).parent.mkdir(parents=True, exist_ok=True)` |
| `File.open(path, "a")` | `open(path, "a")` |
| `write_log(event)` — `@log_io.puts JSON.generate(...)` | `self._log_io.write(json.dumps(event) + "\n")` |
| `@log_io.flush` | `self._log_io.flush()` |
| `generate_session_id` | `f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"` |
| `Time.now.iso8601` | `datetime.now(timezone.utc).isoformat()` |
| `Boukensha.config.dir` | `_config.dir` — passed via module-level config |
| `Boukensha.debug?` | `_debug` — module-level flag |
| `execution_metadata(...)` → `metadata.compact` | Dict comprehension filtering `None` values |
| `usage_tokens(usage)` — `first_integer` helper | Same logic, iterate keys, `int(value)` |
| `provider_name(backend)` — regex on class name | `type(backend).__name__` — simpler in Python |
| `close` | `self._log_io.close()` |

Key design decisions:

**1. Module-level config/debug:**

Ruby uses `Boukensha.config.dir` and `Boukensha.debug?` as module-level
singletons. In Python, add these to `boukensha/__init__.py`:

```python
# boukensha/__init__.py additions
_config = None
_debug = False

def set_config(config):
    global _config
    _config = config

def get_config():
    return _config

def debug_mode():
    global _debug
    _debug = True

def is_debug():
    return _debug
```

The Logger reads `get_config().dir` for the sessions directory.

**2. Logger methods map 1:1:**

| Ruby method | Python method | Logs |
|---|---|---|
| `iteration(n:, max:)` | `iteration(n, max)` | `{"phase": "iteration", "n": N, "max": M}` |
| `limit_reached(kind:, n:, max:)` | `limit_reached(kind, n, max)` | `{"phase": "limit_reached", ...}` |
| `turn_end(reason:, iterations:, tokens:)` | `turn_end(reason, iterations, tokens=None)` | `{"phase": "turn_end", ...}` |
| `prompt(messages:, tools:)` | `prompt(messages, tools)` | `{"phase": "prompt", ...}` |
| `tool_call(name:, args:)` | `tool_call(name, args)` | `{"phase": "tool_call", ...}` |
| `tool_result(name:, result:, ok:, error:)` | `tool_result(name, result, ok=True, error=None)` | `{"phase": "tool_result", ...}` |
| `response(text:, usage:, stop_reason:, task:, backend:)` | `response(text, usage=None, stop_reason=None, task=None, backend=None)` | `{"phase": "response", ...}` |
| `raw(data:)` | `raw(data)` | `{"phase": "raw", ...}` (only if `is_debug()`) |
| `close` | `close()` | — |

**3. `execution_metadata`:**

Normalizes usage tokens from different provider formats:

```python
def _usage_tokens(self, usage):
    if not usage:
        usage = {}
    return {
        "input": self._first_integer(usage, "input_tokens", "prompt_tokens",
                                      "promptTokenCount", "prompt_eval_count"),
        "output": self._first_integer(usage, "output_tokens", "completion_tokens",
                                       "candidatesTokenCount", "eval_count"),
    }

def _first_integer(self, d, *keys):
    for key in keys:
        value = d.get(key)
        if value is not None:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
    return None
```

**4. `provider_name`:**

Python: `type(backend).__name__` gives `"DeepSeek"`. Convert CamelCase to
snake_case via regex or just lower it.

---

### Agent updates (`agent.py`)

Changes from step 5:

1. **`__init__` — add `logger` parameter:**
   ```python
   def __init__(self, ..., logger=None):
       self.logger = logger if logger is not None else Logger()
   ```

2. **`run` — add log calls:**
   - Before iteration: `self.logger.iteration(n=..., max=...)`
   - Before API call: `self.logger.prompt(messages=..., tools=...)`
   - After API call: `self.logger.raw(data=response)`
   - On limit reached: `self.logger.limit_reached(kind="max_iterations", n=..., max=...)`
   - On turn end: `self.logger.turn_end(reason=..., iterations=...)`

3. **`_handle_tool_calls` — wrap dispatch in try/except:**
   ```python
   self.logger.tool_call(name=name, args=args)
   try:
       result = self.registry.dispatch(name, args)
       self.logger.tool_result(name=name, result=result, ok=True)
   except Exception as e:
       result = f"ERROR: {type(e).__name__}: {e}"
       self.logger.tool_result(name=name, result=result, ok=False, error=str(e))
   ```

4. **New helper `_log_response`:**
   ```python
   def _log_response(self, text, response):
       self.logger.response(
           text=text,
           usage=self._normalized_usage(response),
           stop_reason=response.get("stop_reason"),
           task=self.context.task,
           backend=self.builder.backend,
       )
   ```

5. **New helper `_normalized_usage`:**
   ```python
   def _normalized_usage(self, response):
       for key in ("usage", "usageMetadata"):
           if key in response:
               return response[key]
       usage = {}
       for key in ("prompt_eval_count", "eval_count"):
           if key in response:
               usage[key] = response[key]
       return usage or None
   ```

### `__init__.py` additions

```python
# Module-level state (used by Logger)
_config = None
_debug = False

def set_config(config):
    global _config
    _config = config

def get_config():
    global _config
    return _config

def debug_mode():
    global _debug
    _debug = True

def is_debug():
    return _debug
```

And add `Logger` to imports + `__all__`.

---

## Dependencies

Unchanged. No new packages — `json`, `pathlib`, `secrets`, `datetime` are all stdlib.

---

## Project Structure (target)

```
week1_baseline/python/06_the_logger/
├── requirements.txt              # unchanged
├── README.md                     # replaced
├── boukensha/
│   ├── __init__.py               # updated — Logger export + module-level config/debug
│   ├── logger.py                 # NEW
│   ├── agent.py                  # updated — logger calls + error handling
│   ├── ...                       # all other files unchanged
├── examples/
│   └── example.py                # replaced
```

---

## Behavior Parity Checklist

- [ ] Logger writes to `.boukensha/sessions/<session-id>.jsonl`
- [ ] Session ID format: `YYYYMMDDTHHMMSSZ-<8 hex chars>`
- [ ] Every line is valid JSON with `session_id`, `at`, `phase`
- [ ] `iteration` phase logs `n` and `max`
- [ ] `prompt` phase logs message count, serialized messages, tool count, tool names
- [ ] `tool_call` phase logs name and args
- [ ] `tool_result` phase logs name, result, ok, error
- [ ] `response` phase logs text, usage tokens, stop_reason, task, provider, model, cost
- [ ] `raw` phase only logged when `debug_mode()` has been called
- [ ] `limit_reached` phase logged before wrap-up
- [ ] `turn_end` phase logged after completion or wrap-up
- [ ] Agent calls logger at every lifecycle event
- [ ] Agent wraps tool dispatch in try/except, logs errors
- [ ] `execution_metadata` normalizes tokens from Anthropic/OpenAI/Gemini/Ollama formats
- [ ] `estimate_cost` returns float or None
- [ ] `close()` closes the file handle

---

## Expected Output

```
=== BOUKENSHA Step 6: The Logger ===

Config: #<Boukensha::Config ...>
Provider: deepseek
Model: deepseek-v4-pro
Max iterations: 25
Max output tokens: 1024

[iteration 1/25]
  tool call → read_file({'path': 'README.md'})
  tool result → ...
[iteration 2/25]

=== FINAL RESPONSE ===
... (model's text response)
```

Plus a `.jsonl` file in `.boukensha/sessions/` with the logged phases.

---

## Implementation Steps

1. Copy `python/05_agent_loop` → `python/06_the_logger`
2. Create `boukensha/logger.py`
3. Update `boukensha/agent.py` — add logger calls, try/except dispatch, `_log_response`, `_normalized_usage`
4. Update `boukensha/__init__.py` — add Logger export, module-level `config`/`debug`
5. Replace `examples/example.py` — add Logger creation, pass to Agent
6. Create `bin/python/06_the_logger`, make executable
7. Run smoke test — verify output + `.jsonl` file created

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Module-level `config`/`debug`? | **Yes, in `__init__.py`** | Logger reads `get_config().dir` and `is_debug()`. Set via `set_config()` and `debug_mode()` |
| 2 | `logger:` default value? | **`None` → creates `Logger()` internally** | Agent works without explicit logger; Ruby defaults to `Logger.new` |
| 3 | `provider_name` format? | **`type(backend).__name__`** | Gives `"DeepSeek"`, `"Anthropic"`, etc. Simpler than Ruby's regex |
| 4 | New dependencies? | **No** | `json`, `pathlib`, `secrets`, `datetime` are stdlib |
| 5 | DeepSeek backend? | **Already present** | Carried from step 5 copy |

---

## Out of Scope

- Compaction (trimming conversation history)
- Streaming responses
- Multi-task agent loops
