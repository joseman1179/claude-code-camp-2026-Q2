# The Prompt Builder

Because LLM access, cost and quality are constantly changing, we want to be able to switch between multiple LLMs that will drive the agent loop.

There are several SDKs that provide access to many LLMs but in practice we only really need to focus on top-tier models:
- anthropic family
- deepseek family
- openai family
- gemini family
- ollama cloud eg. kimi, minimax, llama

The Prompt Builder serializes `Context` for the exact format each API expects.
The `PromptBuilder` delegates to whichever backend you pass in.

PromptBuilder does not call the API, we are simply preparing the format for API calls.

Configuration is task-based here, carried forward from the registry step. The
`player` task owns its provider, model, and prompt override settings, and the
context records the task that the prompt is being built for.

## Setup (shared virtualenv)

```bash
source .venv/bin/activate
pip install -r week1_baseline/python/03_prompt_builder/requirements.txt
```

## New Files

| File | Description |
|---|---|
| `boukensha/prompt_builder.py` | Delegates serialization to the active backend |
| `boukensha/backends/base.py` | Shared backend contract for model validation and model metadata |
| `boukensha/backends/_openai_compatible.py` | Shared serialization for OpenAI/DeepSeek/Ollama/OllamaCloud |
| `boukensha/backends/anthropic.py` | Serializes context into the Anthropic API format |
| `boukensha/backends/deepseek.py` | Serializes context into the DeepSeek API format |
| `boukensha/backends/ollama.py` | Serializes context into the Ollama API format |
| `boukensha/backends/ollama_cloud.py` | Serializes context into the Ollama Cloud API format |
| `boukensha/backends/openai.py` | Serializes context into the OpenAI Chat Completions format |
| `boukensha/backends/gemini.py` | Serializes context into the Gemini generateContent format |

## How It Works

```
Context (Python objects)
        ↓
PromptBuilder
        ↓
Backend (Anthropic, DeepSeek, Gemini, Ollama, or OpenAI)
        ↓
API Payload (plain dicts and lists)
        ↓
POST to API
```

## `PromptBuilder`

| Method | Description |
|---|---|
| `to_messages()` | Delegates message serialization to the backend |
| `to_tools()` | Delegates tool serialization to the backend |
| `to_api_payload()` | Assembles the complete payload ready to POST |
| `headers()` | Returns the correct headers for the backend |
| `url()` | Returns the correct endpoint URL for the backend |

## Backends

Each API has its own conventions for how data is expected. Anthropic and Gemini are the most alike (system prompt as a top-level field), while OpenAI, DeepSeek, and Ollama share the same `function`-wrapped tool schema.

Backends also own their supported model table. A backend refuses to initialize
with an unknown model, so `settings.yaml` cannot silently select an unsupported
or misspelled model. Each model entry carries:

| Key | Meaning |
|---|---|
| `context_window` | The model's known token context window |
| `cost_per_million.input` | USD input token price per million tokens, when known |
| `cost_per_million.output` | USD output token price per million tokens, when known |
| `usage_unit` | `tokens`, `local_compute`, or `ollama_cloud_usage` |
| `usage_level` | Ollama Cloud usage tier, when applicable |

### `Anthropic`

Talks to `https://api.anthropic.com/v1/messages`.
Requires an `ANTHROPIC_API_KEY`.

### `DeepSeek`

Talks to `https://api.deepseek.com/v1/chat/completions`.
Requires a `DEEPSEEK_API_KEY`. OpenAI-compatible format.

### `Ollama`

Talks to `http://localhost:11434/api/chat`.
Requires `ollama serve` running locally. No API key needed.

### `OllamaCloud`

Talks to `https://ollama.com/api/chat`. Requires an `OLLAMA_API_KEY`.

### `OpenAI`

Talks to `https://api.openai.com/v1/chat/completions`.
Requires an `OPENAI_API_KEY`.

### `Gemini`

Talks to `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`.
Requires a `GEMINI_API_KEY`.

## Run Example

```bash
./week1_baseline/bin/python/03_prompt_builder
```
