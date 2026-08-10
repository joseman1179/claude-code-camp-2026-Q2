# Plan: Port 08_the_repl_loop from Ruby → Python

## Overview

Port `week1_baseline/ruby/08_the_repl_loop` to Python as
`week1_baseline/python/08_the_repl_loop/`.

The Python snapshot is a copy of `07_the_run_dsl`. This step adds the
interactive **REPL loop** — a persistent session that accumulates conversation
history across multiple turns, with built-in commands (`/clear`, `/quiet`,
`/loud`, `/help`, `/exit`).

---

## What's new vs 07_the_run_dsl

| Component | Status |
|-----------|--------|
| `Repl` | NEW — interactive session loop |
| `VERSION` | NEW — `"0.8.0"` constant |
| `boukensha.repl()` | NEW — same signature as `run()` minus `task`, drops into REPL |
| `Context#clear_messages!` | NEW — wipes `@messages`, keeps tools |
| `Agent#run` | Updated — adds final reply as `assistant` message to context |
| `Agent#_wrap_up` | Updated — adds wrap-up reply as `assistant` message to context |
| `Logger#turn` | NEW — logs `{"phase": "turn", "n": N}` |
| `__init__.py` | Updated — adds `Repl`, `VERSION`, `repl()` function |
| `examples/example.rb` | Replaced — uses `Boukensha.repl` |
| `README.md` | Replaced |

No new dependencies. All backends, Client, PromptBuilder, Registry, Config
unchanged.

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/repl.rb` | → | `boukensha/repl.py` | **Create** |
| `lib/boukensha/version.rb` | → | `boukensha/version.py` | **Create** |
| `lib/boukensha/context.rb` | → | `boukensha/context.py` | **Update** — add `clear_messages()` |
| `lib/boukensha/agent.rb` | → | `boukensha/agent.py` | **Update** — add final reply to context |
| `lib/boukensha/logger.rb` | → | `boukensha/logger.py` | **Update** — add `turn()` method |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** — add `Repl`, `VERSION`, `repl()` |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |
| — | → | `bin/python/08_the_repl_loop` | **Create** launcher |

---

## Mapping: Ruby → Python

### Repl (`repl.rb` → `repl.py`)

| Ruby | Python |
|------|--------|
| `PROMPT = "boukensha> "` | Class constant |
| `HELP = <<~HELP ... HELP` | Multiline string constant |
| `initialize(context:, registry:, ...)` | `__init__` with same kwargs |
| `start` — loop: print prompt, read stdin, dispatch commands | Same — `input()`, `print()`, `sys.stdin.read()` |
| `$stdin.gets` → break on nil (EOF) | `input()` raises `EOFError` on Ctrl-D |
| `case input when "/exit"` | `if/elif` chain |
| `Boukensha.quiet!` / `Boukensha.loud!` | `boukensha.set_quiet(True/False)` — need to add module-level `_quiet` |
| `@context.clear_messages!` | `self.context.clear_messages()` |
| `run_turn(input)` | `self._run_turn(input)` |
| `banner` method | Same — ASCII art with version, config dir, provider |
| Creates new `Agent.new(...)` each turn | Same |
| `rescue LoopError` | `except ...` (need to add `LoopError` to errors or catch generic) |

> **Note on REPL input:** Python's `input()` raises `EOFError` on Ctrl-D
> (unlike Ruby's `$stdin.gets` returning nil). Catch `EOFError` to exit
> gracefully. Ctrl-C raises `KeyboardInterrupt`.

### Context (`context.rb` → `context.py`)

Add one method:

```python
def clear_messages(self) -> None:
    """Drop all conversation history, keeping tools and system prompt intact."""
    self.messages = []
```

### Agent (`agent.rb` → `agent.py`)

Two changes:

**1. In `run()` — add final reply to context before returning:**

```python
# Before (step 7):
text = self._extract_text(parsed["content"])
self._log_response(text=text, response=response)
self.logger.turn_end(reason="completed", iterations=self.iteration)
return text

# After (step 8):
text = self._extract_text(parsed["content"])
self._log_response(text=text, response=response)
self.logger.turn_end(reason="completed", iterations=self.iteration)
self.context.add_message("assistant", text)
return text
```

**2. In `_wrap_up()` — add reply to context:**

```python
# After build_message, before return:
self.context.add_message("assistant", text)  # or msg for fallback
```

### Logger (`logger.rb` → `logger.py`)

Add one method:

```python
def turn(self, n: int) -> None:
    self._write_log({"phase": "turn", "n": n})
```

### `__init__.py` — `boukensha.repl()` function

Same structure as `boukensha.run()` but:
- No `task` parameter
- Creates `Repl` instead of calling `agent.run()` directly
- Passes `config_dir`, `provider`, `model`, `version`, `api_key`
- Needs module-level `_quiet` flag + `set_quiet()`/`is_quiet()` functions
- Needs `LoopError` in errors (or use generic Exception)

### `version.py`

```python
VERSION = "0.8.0"
```

---

## Dependencies

Unchanged. No new packages.

---

## Project Structure (target)

```
week1_baseline/python/08_the_repl_loop/
├── requirements.txt              # unchanged
├── README.md                     # replaced
├── boukensha/
│   ├── __init__.py               # updated — Repl, VERSION, repl(), quiet/loud
│   ├── version.py                # NEW
│   ├── repl.py                   # NEW
│   ├── context.py                # updated — clear_messages()
│   ├── agent.py                  # updated — final reply to context
│   ├── logger.py                 # updated — turn()
│   ├── errors.py                 # updated — LoopError (optional)
│   ├── ...                       # all other files unchanged
├── examples/
│   └── example.py                # replaced
```

---

## Behavior Parity Checklist

- [ ] `Repl.start()` prints banner, then loops reading stdin
- [ ] `/exit` and `/quit` exit gracefully
- [ ] `/help` prints command list
- [ ] `/clear` calls `context.clear_messages()`, resets turn counter
- [ ] `/quiet` / `/loud` toggle module-level `_quiet` flag
- [ ] Ctrl-D (EOFError) exits gracefully
- [ ] Ctrl-C (KeyboardInterrupt) exits gracefully
- [ ] Each turn creates a new `Agent`, runs it, prints result
- [ ] `Agent.run()` adds final text as `assistant` message to context
- [ ] `Agent._wrap_up()` adds wrap-up text as `assistant` message to context
- [ ] `Context.clear_messages()` wipes messages, keeps tools
- [ ] `Logger.turn(n)` logs `{"phase": "turn", "n": N}`
- [ ] Conversation history accumulates across turns

---

## Expected Output

```
╔══════════════════════════════════════╗
║  BOUKENSHA MUD Assistant (v0.8.0)    ║
╚══════════════════════════════════════╝
  config:    .../.boukensha
  provider:  deepseek (deepseek-v4-pro)  ✓ API key set

  /quiet or /loud   toggle logging
  /clear           reset conversation history
  /exit or /quit    leave the REPL

boukensha> list the files in .
... (agent response) ...
boukensha> /exit
Goodbye.
```

---

## Implementation Steps

1. Copy `python/07_the_run_dsl` → `python/08_the_repl_loop`
2. Create `boukensha/version.py`
3. Create `boukensha/repl.py`
4. Update `boukensha/context.py` — add `clear_messages()`
5. Update `boukensha/agent.py` — add `context.add_message("assistant", text)` in `run()` and `_wrap_up()`
6. Update `boukensha/logger.py` — add `turn(n)` method
7. Update `boukensha/__init__.py` — add `VERSION`, `Repl`, `repl()`, `_quiet`/`set_quiet`/`is_quiet`
8. Replace `examples/example.py`
9. Create `bin/python/08_the_repl_loop`, make executable
10. Test with piped input

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | `instance_eval` for tools in REPL? | **Same callback pattern as step 7** | `boukensha.repl(tools=register_tools)` |
| 2 | New Agent per turn or reuse? | **New Agent per turn** (match Ruby) | Agent is stateless; context is shared for history |
| 3 | `LoopError`? | **Skip for now** | Ruby raises it but there's no matching error in the codebase; catch generic `Exception` |
| 4 | `_quiet` module flag? | **Yes** | `/quiet` suppresses logger output via `is_quiet()` check |
| 5 | New dependencies? | **No** | |

---

## Out of Scope

- All future steps (this is the final step)
