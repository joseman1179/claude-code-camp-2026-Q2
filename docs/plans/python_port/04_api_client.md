# Plan: Port 04_api_client from Ruby → Python

## Overview

Port `week1_baseline/ruby/04_api_client` to Python as
`week1_baseline/python/04_api_client/`.

The Python snapshot is a copy of `03_prompt_builder`. This plan covers only the
**step 4 delta**: compare Ruby `03_prompt_builder` to Ruby `04_api_client`,
then apply those changes.

This step adds the **API Client** — an HTTP layer that POSTs the
`PromptBuilder` payload to the LLM provider and returns the parsed JSON
response. It includes retry logic for transient network errors and retryable
HTTP status codes (408, 409, 429, 5xx).

---

## What's new vs 03_prompt_builder

| Component | Status |
|-----------|--------|
| All backends, PromptBuilder, Registry, Config, Tasks | Unchanged |
| `ApiError` | NEW — raised when all retries are exhausted |
| `Client` | NEW — HTTP client with retry logic |
| `boukensha.rb` (top-level exports) | Updated — adds client require |
| `examples/example.rb` | Replaced — calls real API via Client |
| `README.md` | Replaced with step 4 content |

No new dependencies — `Gemfile` unchanged (just `dotenv`).

---

## Files to touch (delta only)

| Ruby Source | → | Python Target | Action |
|-------------|---|---------------|--------|
| `lib/boukensha/errors.rb` | → | `boukensha/errors.py` | **Update** — add `ApiError` |
| `lib/boukensha/client.rb` | → | `boukensha/client.py` | **Create** |
| `lib/boukensha.rb` | → | `boukensha/__init__.py` | **Update** — add `Client`, `ApiError` |
| `examples/example.rb` | → | `examples/example.py` | **Replace** |
| `README.md` | → | `README.md` | **Replace** |
| — | → | `bin/python/04_api_client` | **Create** launcher |

All other files unchanged.

---

## Mapping: Ruby → Python

### ApiError (`errors.rb` → `errors.py` update)

```python
class ApiError(Exception):
    """Raised when an API request fails after all retries."""
    pass
```

### Client (`client.rb` → `client.py`)

Ruby uses `Net::HTTP`. Python uses stdlib `urllib` (no `requests` dependency).

| Ruby | Python |
|------|--------|
| `require "net/http"` | `import urllib.request` |
| `require "json"` | `import json` (stdlib) |
| `require "openssl"` | `import ssl` (stdlib) |
| `Net::HTTP.new(uri.host, uri.port)` | `urllib.request.Request(url, data, headers, method="POST")` |
| `http.use_ssl = true` | HTTPS handled automatically by `urllib` for `https://` URLs |
| `Net::HTTP::Post.new(uri, headers)` | `urllib.request.Request(method="POST")` |
| `request.body = payload.to_json` | `data=json.dumps(payload).encode("utf-8")` |
| `http.request(request)` | `urllib.request.urlopen(request, timeout=30)` |
| `retryable_response?(response)` — checks `code.to_i` | `response.getcode() in RETRYABLE_STATUS_CODES` |
| `rescue *TRANSIENT_ERRORS` | `except (URLError, socket.timeout, TimeoutError, ConnectionResetError, ...)` |
| `sleep retry_delay(attempts)` | `time.sleep(self._retry_delay(attempts))` |
| `JSON.parse(response.body)` | `json.loads(response.read().decode("utf-8"))` |
| `MAX_RETRIES = 3` | Same |
| `BASE_RETRY_DELAY = 0.5` | Same |
| `retry_delay = BASE_RETRY_DELAY * (2**(attempt-1))` | Same — exponential backoff |

Transient errors mapped:

| Ruby | Python |
|------|--------|
| `EOFError` | (covered by `URLError`) |
| `Errno::ECONNRESET` | `ConnectionResetError` |
| `Errno::ECONNREFUSED` | `ConnectionRefusedError` |
| `Net::OpenTimeout` | `urllib.error.URLError` |
| `Net::ReadTimeout` | `socket.timeout` / `TimeoutError` |
| `OpenSSL::SSL::SSLError` | `ssl.SSLError` |
| `SocketError` | `OSError` |
| `Timeout::Error` | `TimeoutError` |

---

## Dependencies

Unchanged:

| Python Package |
|---------------|
| `python-dotenv` |
| `pyyaml` |

`urllib`, `json`, `ssl`, `socket`, `time` are all stdlib.

---

## Project Structure (target)

```
week1_baseline/python/04_api_client/
├── requirements.txt            # unchanged
├── README.md                   # replaced with step 4 content
├── boukensha/
│   ├── __init__.py             # updated — adds Client, ApiError
│   ├── client.py               # NEW
│   ├── errors.py               # updated — adds ApiError
│   ├── ...                     # all other files unchanged
│   └── backends/
│       └── ...                 # unchanged
├── examples/
│   └── example.py              # replaced
└── prompts/
    └── system.md               # unchanged
```

---

## Behavior Parity Checklist

- [ ] `ApiError` added to `errors.py`
- [ ] `Client.__init__` stores `builder`
- [ ] `Client.call(max_output_tokens)` POSTs payload to `builder.url()`
- [ ] Retry logic: 3 attempts, exponential backoff (0.5s, 1s, 2s)
- [ ] Retryable status codes: {408, 409, 429, 500, 502, 503, 504}
- [ ] Transient network errors caught and retried
- [ ] `ApiError` raised after exhausting retries
- [ ] `ApiError` raised on non-2xx response after retries
- [ ] Successful response parsed as JSON and returned as dict
- [ ] `__init__.py` exports `Client` and `ApiError`
- [ ] Example calls real API and prints response

---

## Implementation Steps

1. Copy `python/03_prompt_builder` → `python/04_api_client`
2. Add `ApiError` to `boukensha/errors.py`
3. Create `boukensha/client.py`
4. Update `boukensha/__init__.py`
5. Replace `examples/example.py`
6. Replace `README.md`
7. Create `bin/python/04_api_client`, make executable
8. Run smoke test — verify real API response

---

## Resolved Decisions

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | HTTP library? | **`urllib` (stdlib)** | No new dependency. Matches Ruby's choice of stdlib `net/http` over a third-party gem |
| 2 | New dependencies? | **No** | `urllib`, `json`, `ssl`, `time` are stdlib |
| 3 | DeepSeek backend? | **Already present** | Carried from step 3 copy; no action needed |

---

## Out of Scope (future steps)

- Parsing tool calls from the API response
- The agent loop that iterates: call API → parse response → dispatch tool → repeat
- Token budget tracking during runtime
