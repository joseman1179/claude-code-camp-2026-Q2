# The Tool Registry

The Tool Registry is how BOUKENSHA manages what capabilities the agent can use.

It has two jobs:
  1. storing tools
  2. dispatching tools when asked

## Setup (shared virtualenv)

A single virtualenv at the **repo root** is shared across all Python steps:

```bash
# From the project root:
python3 -m venv .venv
source .venv/bin/activate
pip install -r week1_baseline/python/02_the_registry/requirements.txt
```

All future steps reuse this same `.venv`.

## New Files

| File | Description |
|---|---|
| `boukensha/registry.py` | The Registry class — registers tools and dispatches calls |
| `boukensha/errors.py` | BOUKENSHA-specific error classes |

## How It Works

The agent NEVER calls a tool directly.
It emits a structured request (name and args) and the Registry looks up the tool and runs it.

```
Agent:  "Hey registry call move with direction='north'"
Registry: "looking up 'move' in the tool table"
Registry: "Found it now calling the block with the provided args"
Registry: "Here's the result"
Agent: "Thanks buddy"
Registry: "Thats why you pay me the big tokens"
```

## `Registry`

| Method | Description |
|---|---|
| `tool(name, description, parameters)` | Decorator that registers a new tool on the context |
| `dispatch(name, args)` | Looks up a tool by name and calls it with the provided args |

## `UnknownToolError`

Raised when `dispatch` is called with a name that has no registered tool.
A harness needs explicit error boundaries — an unrecognised tool name should never silently fail.

**Example:**
```
UnknownToolError: No tool registered as 'flee'
```

## Expected Output

```
=== BOUKENSHA Step 2: Tool Registry ===

Config:  #<Boukensha::Config ...>
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

## Considerations

`dispatch` converts string keys to keyword arguments when calling the block.
In Ruby, the API returns arguments as string-keyed JSON but Ruby blocks expect symbols,
so `transform_keys(&:to_sym)` is needed. In Python, `**` unpacking works directly with
string keys — no conversion is necessary. This difference is noted in `registry.py`.

## Considerations

We now register tools with the Registry but our code still has direct registration and tools in context. This likely should have been reworked.

Checking the final baseline example, we did correct the issue.
The context should have reference to tools[] its currently using, and the full table of tools registered should live on the Registry.

We'll correct this manually in a future step and we will leave things in place.

## Run Example

```bash
./week1_baseline/bin/python/02_the_registry
```
