# Plan: Port 00_config from Ruby → Python

## Overview

Port `week1_baseline/ruby/00_config` to Python, preserving the same behavior,
configuration schema, and directory resolution logic. The Python port will live
at `week1_baseline/python/00_config/`.

---

## Files to Port

| Ruby Source | → | Python Target |
|-------------|---|---------------|
| `lib/boukensha.rb` | → | `boukensha/__init__.py` |
| `lib/boukensha/config.rb` | → | `boukensha/config.py` |
| `lib/boukensha/tasks/base.rb` | → | `boukensha/tasks/base.py` |
| `lib/boukensha/tasks/player.rb` | → | `boukensha/tasks/player.py` |
| `lib/boukensha/agent.rb` | → | `boukensha/agent.py` |
| `examples/example.rb` | → | `examples/example.py` |
| `prompts/system.md` | → | `prompts/system.md` (copy, no changes) |
| `README.md` | → | `README.md` (ported from Ruby, Python-flavored) |
| `Gemfile` | → | `requirements.txt` |
| `bin/ruby/00_config` | → | `bin/python/00_config` (new, calls python) |

---

## Mapping: Ruby → Python

### Config class (`config.rb` → `config.py`)

| Ruby | Python |
|------|--------|
| `require "yaml"` | `import yaml` (PyYAML) |
| `require "dotenv"` | `from dotenv import load_dotenv` (python-dotenv) |
| `require "pathname"` | `from pathlib import Path` |
| `File.join(...)` | `Path(...) / "..."` |
| `Dir.home` | `Path.home()` |
| `File.exist?` | `Path.exists()` |
| `File.read(...)` | `Path(...).read_text()` |
| `ENV.fetch("X", nil)` | `os.environ.get("X")` |
| `YAML.safe_load(...)` | `yaml.safe_load(...)` |
| `attr_reader :dir, :settings` | `self.dir`, `self.settings` properties (or plain attributes in `__init__`) |
| `#to_s` / `#inspect` | `__str__` / `__repr__` |
| `private` methods | prefix with `_` (convention) |

### Tasks::Base (`tasks/base.rb` → `tasks/base.py`)

| Ruby | Python |
|------|--------|
| `module Boukensha::Tasks` | `boukensha.tasks` package |
| `class << self; private` | `@staticmethod` or module-level private functions |
| `raise NotImplementedError` | `raise NotImplementedError` (same) |
| `raise ArgumentError` | `raise ValueError` (Python equivalent) |
| `node.is_a?(Hash)` | `isinstance(node, dict)` |

### Tasks::Player (`tasks/player.rb` → `tasks/player.py`)

| Ruby | Python |
|------|--------|
| `class Player < Base` | `class Player(Base)` |
| `def self.task_name = "player"` | `task_name: ClassVar[str] = "player"` |

### Agent (`agent.rb` → `agent.py`)

The Agent performs BFS pathfinding from a start room to the bakery (room 3009)
using room exit data. Straightforward port — Ruby `Hash` → Python `dict`, etc.

---

## Dependencies

| Ruby Gem | Python Package |
|----------|---------------|
| `dotenv` | `python-dotenv` |
| `yaml` (stdlib) | `pyyaml` |
| `pathname` (stdlib) | `pathlib` (stdlib) |

---

## Project Structure (target)

```
week1_baseline/python/00_config/
├── requirements.txt            # python-dotenv, pyyaml
├── README.md                   # ported from Ruby README, Python-flavoured
├── boukensha/
│   ├── __init__.py             # top-level package exports
│   ├── config.py
│   ├── agent.py
│   └── tasks/
│       ├── __init__.py
│       ├── base.py
│       └── player.py
├── examples/
│   └── example.py
└── prompts/
    └── system.md
```

---

## Behavior Parity Checklist

- [ ] `BOUKENSHA_DIR` env var → custom config dir
- [ ] `~/.boukensha` → default config dir
- [ ] Load `.env` from config dir
- [ ] Load `settings.yaml` from config dir
- [ ] `config.tasks()` → full tasks hash
- [ ] `config.tasks("player")` → player task hash
- [ ] `config.tasks(:player)` → player task hash (symbol-style — Python equivalent with string)
- [ ] `config.user_prompts_dir` → `{config_dir}/prompts`
- [ ] `config.mud_host`, `mud_port`, `mud_username`, `mud_password` → with defaults
- [ ] `config.dig(:mud, :host)` → nested dict access
- [ ] `Tasks::Base.provider(settings)` → raises if missing
- [ ] `Tasks::Base.model(settings)` → raises if missing
- [ ] `Tasks::Base.prompt_override?(settings)` → checks `prompt_override.system == true`
- [ ] `Tasks::Base.system_prompt(settings, ...)` → user override → default fallback
- [ ] `Tasks::Player.task_name` → `"player"`
- [ ] `Agent#cognize` → BFS pathfinding to bakery
- [ ] Smoke test (`examples/example.py`) produces equivalent output

---

## Note: bin/ structure

The repo already separates bin scripts by language:

```
week1_baseline/bin/
├── ruby/00_config     ← existing
└── python/00_config   ← NEW (we create this)
```

The Python launcher goes in `bin/python/00_config`, mirroring `bin/ruby/00_config`.
It will `cd` to `week1_baseline/python/00_config` and run
`python examples/example.py`, assuming a shared virtualenv has already been
activated at the repo root (see [Virtualenv Convention](#virtualenv-convention)
below).

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Python version? | **3.10** | `str \| None` available (PEP 604), `match`/`case` available (3.10+), `from __future__ import annotations` not needed |
| 2 | Deps format? | **`requirements.txt`** only | `requirements.txt` for `python-dotenv` + `pyyaml`. No `pyproject.toml` or editable install — each step is a self-contained snapshot |
| 3 | Type hints? | **Yes** | All public methods typed. Use `dict[str, Any]`, `str \| None`, `Path`, etc. |
| 4 | Install mode? | **virtualenv + `pip install -r requirements.txt`** | One shared venv at repo root, created once per Virtualenv Convention. The launcher assumes it's already activated |
| 5 | Port Agent now? | **Yes** | Agent (BFS pathfinding) included in this step |
| 6 | Tests? | **No** | Smoke test only via `examples/example.py` |
| 7 | Virtualenv? | **One shared venv at repo root** | `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` done once. All future steps reuse the same venv |

---

## Virtualenv Convention

One shared virtualenv at the **repo root** is used across all Python steps:

```bash
# Create once at the project root:
python -m venv .venv
source .venv/bin/activate
pip install -r week1_baseline/python/00_config/requirements.txt
```

The README ported to Python will document this at the top. All future steps
(`01_...`, `02_...`) reuse this same `.venv` — when a new step adds
dependencies, the user runs `pip install -r` for that step's `requirements.txt`
from within the already-activated venv.

---

## Out of Scope (future steps)

- `max_iterations`, `max_turn_tokens`, `max_output_tokens`, `compaction_threshold` (not read yet per README)
- Multi-task support (only `player` for now)
