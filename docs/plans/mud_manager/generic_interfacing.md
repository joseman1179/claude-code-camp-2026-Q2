# Generic Interfacing — Technical Exploration

## The Problem

Our MUD manager is written in Ruby. It owns two things:

1. **`MudManager::Session`** — a long-lived telnet connection to CircleMUD
   (tabMUD on `localhost:4000`). It spawns a background reader thread, strips
   telnet IAC negotiation bytes, buffers incoming text, performs the multi-step
   login dance, and exposes `read_until_quiet` / `read_until` / `send_command`.
2. **`MudManager::Primitives`** — a stateless library of ~55 typed command
   builders (`look`, `move north`, `attack orc`, `say`, `get`, `drop`, …).

In our Bootcamp, bootcampers want to use their preferred programming language —
Java, Python, Rust, PHP, Go, and so on. They must all drive the **same** MUD
through the **same** session management, without us re-writing the MUD manager
per language.

### The constraint that drives everything

> **The MUD manager is managing the sessions for the MUD.**

A MUD session is *stateful and long-lived*. The telnet TCP socket stays open
for the life of the player character. A one-shot process that connects, sends a
command, reads the reply, and exits cannot hold that state — it would redo the
login dance on every command, lose async chatter (combat, tells, room events),
and pay a full TCP + login round-trip per call.

This was already proven in the pre-week exploration
(`week0_explore/0_PREWEEK.md` and
`week0_explore/explore_architecture/01_plain_agent/*`):

- A coding harness's shell tool is **atomic and non-interactive** — it runs a
  command, waits for termination, reads static output, and closes. A live TCP
  loop (`nc`, `telnet`) never terminates, so the tool times out or freezes.
- **Conclusion:** raw terminal access is a point of failure. A **middleware
  layer** that owns the persistent connection is mandatory. The pre-week
  document names the two viable shapes: *a dedicated SDK/wrapper*, or *an MCP
  server*.

Any generic-interfacing decision must therefore be evaluated against one test:

> Does the interface keep the **stateful session alive in one long-lived
> process**, and let every language talk to it over a **clean, language-agnostic
> channel**?

---

## The Four Candidate Solutions

### Option 1 — A wrapper (binding) per language

Write native bindings for Ruby in every language: Java (JRuby/FFI), Python
(Ruby FFI / subprocess), Rust (FFI), PHP, Go, …

**Why it fails the test**

- The wrapper would have to **re-implement the stateful session** in each
  language. `Session` is not a pure function you can bind to — it is a thread +
  socket + buffer + login state machine. FFI can call functions, but binding a
  Ruby `Thread` + `Mutex` + `ConditionVariable` lifecycle across an FFI boundary
  is fragile and effectively means re-writing the session per language.
- Requires a **Ruby runtime installed on every bootcamper's machine** just to
  use the library.
- **N × M maintenance:** every primitive and every session change must be
  propagated to N language bindings.
- It couples everyone to Ruby's object model and version (`>= 3.0`).

**Verdict:** highest cost, most coupling, and it does not solve the stateful
session problem — each language would carry its own copy of the hard part.

---

### Option 2 — Make MudManager a CLI and shell out to it

Bootcampers run `mud-manager look`, `mud-manager move --direction north`, etc.
from their own language.

**Why it fails the test (as stated)**

- A one-shot CLI is **atomic**: each invocation is a fresh process. To keep the
  session alive it must either:
  - reconnect + re-login on every command (slow, and it breaks state), or
  - become a **long-lived daemon** that accepts commands — at which point it is
    no longer "shell commands", it is a protocol server in disguise.
- Still requires **Ruby installed everywhere** (you shell out to a Ruby CLI).
- Every language must **parse human-readable text output**, which is fragile and
  duplicates logic N times.

**Verdict:** the "command-line tool" idea only works if it silently mutates into
a persistent server. That mutation *is* the right answer — but then the real
question becomes "which protocol does the daemon speak?", which lands on
Option 3/4. So Option 2 is not a solution, it is a half-formed version of the
solution.

---

### Option 3 — Implement a custom communication protocol

Define our own RPC: JSON-RPC or a bespoke wire format over TCP/stdio, with
hand-rolled message framing, versioning, error model, and tool discovery.

**Why it is close but expensive**

- A protocol is the *correct architecture*: a long-lived server owns the
  session, clients in any language speak the protocol.
- But "implement a communication protocol" means we must:
  1. design and version the protocol,
  2. document it,
  3. **write a client library in every language** (Java, Python, Rust, PHP,
     Go, …) — which is exactly the N×M maintenance burden we were trying to
     escape.

**Verdict:** right architecture, but we'd be paying for the protocol *and* all
the client SDKs ourselves.

---

### Option 4 — Implement MCP as the layer ✅

Expose the Ruby MUD manager as a **Model Context Protocol (MCP) server**, and
let every bootcamper connect using their language's **existing MCP client SDK**.

MCP *is* a communication protocol — specifically **JSON-RPC 2.0 over stdio**
(newline-delimited JSON) — but it is a *standardized* one with:

- a fixed lifecycle (`initialize` → `notifications/initialized` →
  `tools/list` → `tools/call`),
- a JSON Schema tool/parameter model,
- **official client SDKs already shipping** for Python, TypeScript/Node, Java,
  Kotlin, C#; mature community SDKs for Go, Rust, PHP, and more.

**Why it passes the test**

- The Ruby process **stays alive and owns the telnet socket**; clients send
  short JSON-RPC tool calls and receive text back. State never leaves the
  server.
- **Language-neutral by construction:** a bootcamper in Go imports a Go MCP
  client, points it at `mud-manager --mcp`, and gets `look`, `move`, `attack`,
  … as typed tools. No Ruby runtime on their machine, no FFI, no text parsing.
- **One implementation to maintain:** the Ruby server is the single source of
  truth. New primitives appear automatically via `tools/list` discovery.
- **The work is already half done in this repo** (see "Current state" below):
  the Ruby `boukensha` agent already speaks MCP as a *client*, and its config
  already models `mcp_servers:` entries.

**Verdict:** MCP is Option 3 (a communication protocol) with the protocol
design, versioning, and all the client SDKs done for us. It is the only option
that satisfies the stateful-session constraint *and* removes the per-language
maintenance burden.

---

## Recommendation

> **Implement MCP as the layer.**

The MudManager keeps doing exactly what it does today — managing sessions and
building commands — but instead of only being consumable as a Ruby library, it
gains a thin `bin/mud-manager --mcp` entry point that serves its `Session` +
`Primitives` surface as MCP tools over stdio.

Bootcampers then interact with the MUD from their language of choice via the
standard MCP SDK for that language, and their agent loop (the `boukensha`
pattern, re-implemented in their own language) registers those tools exactly the
way `Boukensha::Tools::Mcp` does in Ruby.

### Why not the others, in one line each

| Option | Fails because |
|--------|---------------|
| 1. Wrapper per language | Re-implements the stateful session N times; needs Ruby + FFI everywhere; N×M maintenance |
| 2. CLI + shell out | Atomic calls can't hold the session; still needs Ruby; fragile text parsing; mutates into a daemon anyway |
| 3. Custom protocol | Right architecture, but we pay for protocol *and* N client SDKs ourselves |
| **4. MCP** | **Standardized protocol + existing SDKs + session stays in one long-lived Ruby process** |

---

## Concrete Design

### Transport

- **stdio** (JSON-RPC 2.0, one JSON object per line). This matches the client
  already implemented in `week1_baseline/ruby/10_standard_tool_library/lib/boukensha/mcp/client.rb`
  and is the simplest transport to script.
- Pin `protocolVersion: "2025-06-18"` (the version the existing client sends).
- Credentials travel by **environment variables** (`MUD_HOST`, `MUD_PORT`,
  `MUD_NAME`, `MUD_PASSWORD`) — the stdio transport's standard credential
  channel, already documented in `config.rb` as `env:` on an `mcp_servers`
  entry.

### Lifecycle

```
client spawns:  mud-manager --mcp            (server process starts, socket not yet open)
  → initialize (handshake, reports serverInfo)
  → notifications/initialized
  → tools/list  (discovers N tools + JSON schemas)
  → tools/call  (each call executes against the persistent session)
  → … repeat tools/call …
client closes stdin → server closes the telnet session and exits
```

### Tool mapping — Primitives → MCP tools

Each public `MudManager::Primitives` method becomes one MCP tool:

- `move` → tool `move`, parameter `direction` (JSON Schema `enum: [north, south, east, west, up, down]`)
- `attack` → tool `attack`, parameters `style` (enum) + `target` (string)
- `look` → tool `look`, parameters `mode` (enum), `target`, `preposition`
- … and so on for `say`, `get`, `drop`, `equip`, `cast`, `info_self`, `info_world`, …

The `Primitives` module already carries the enum tables (`DIRECTIONS`,
`POSITIONS`, `ATTACK_STYLES`, `CHANNELS`, …) and the required-vs-optional shape
of every argument, so generating a faithful JSON Schema is mechanical:

```json
{
  "name": "move",
  "description": "Move one room in a compass direction.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "direction": {
        "type": "string",
        "enum": ["north", "south", "east", "west", "up", "down"],
        "description": "Compass direction to travel."
      }
    },
    "required": ["direction"]
  }
}
```

> Note: the step-10 test suite (`test_mcp_servers_config.rb`) currently asserts a
> `mud` server exposes **26 tools**. `Primitives` defines ~55 public methods, so
> the daemon may ship a curated subset (the 26 most agent-relevant commands) or
> expose all of them — this is an open decision (see Open Questions).

### Session ownership

- The server process owns **one `MudManager::Session` per player character**
  (credentials from env). The telnet socket is opened lazily and kept open for
  the server's whole lifetime.
- On the first `tools/call`, the server performs `open` + `login` transparently
  (or exposes an explicit `connect` tool — open question).
- Each tool call: `send_command(primitive)` → `read_until_prompt` (with
  `read_until_quiet` fallback) → return the MUD's text as `content`.
- Async chatter (combat, tells, room events) that arrives between calls is
  buffered and returned with the next response — exactly the semantics
  `Session#read_until_quiet` already provides.

### Error model

- **Argument errors** (bad enum, missing required string) → tool result with
  `isError: true` and text `argument_error: …`. These are *data*, not
  exceptions, so an agent loop can keep going — this is already the contract
  asserted by `test_mcp_client.rb`.
- **Connection / login failures** → tool result with `isError: true` (or a
  JSON-RPC error result for the `connect` step), never a server crash.
- **Protocol-level failures** (malformed JSON, unknown method) → standard
  JSON-RPC `error` object.

---

## Current State (what exists vs. what is missing)

### Already implemented (in this repo)

| Piece | Location | Status |
|-------|----------|--------|
| Ruby `Session` (telnet + IAC strip + login + buffering) | `week0_explore/mud_manager/lib/mud_manager/session.rb` | ✅ done |
| Ruby `Primitives` (~55 typed command builders + enum tables) | `week0_explore/mud_manager/lib/mud_manager/primitives.rb` | ✅ done |
| Generic **MCP client** (initialize / tools/list / tools/call over stdio) | `week1_baseline/ruby/10_standard_tool_library/lib/boukensha/mcp/client.rb` | ✅ done |
| Generic **MCP host layer** (registers any server's tools + prefixing + collisions) | `week1_baseline/ruby/10_standard_tool_library/lib/boukensha/tools/mcp.rb` | ✅ done |
| `mcp_servers:` config (`command`/`args`/`env`/`prefix`/`required`) | `week1_baseline/ruby/10_standard_tool_library/lib/boukensha/config.rb` | ✅ done |
| End-to-end demo that treats the daemon as "just another server" | `week1_baseline/ruby/10_standard_tool_library/examples/mcp_mud_demo.rb` | ✅ done (references the missing daemon) |

### Missing — the actual gap

The MCP **server** side of the MudManager does not exist yet:

1. **`week0_explore/mud_manager/bin/mud-manager`** — the executable that, given
   `--mcp`, speaks JSON-RPC 2.0 over stdio, advertises the primitives as tools,
   and owns the live session. Referenced by step-10 tests and examples, but not
   present.
2. **`week0_explore/mud_manager/lib/mud_manager/fake_mud.rb`** — an in-memory
   fake MUD (binds a local port, speaks enough of the login + prompt protocol)
   so tests run offline. Also referenced by step-10 tests, also missing.
3. **`mud_manager.gemspec`** — currently declares *no* executable and no
   dependencies; needs `spec.executables = ["mud-manager"]` and (if we don't
   hand-roll the server) an MCP server dependency.

This is exactly what "generic interfacing" requires us to build next: turn the
MudManager library into a *server* so any language can consume it.

---

## Decision Matrix

| Criterion | 1. Wrappers | 2. CLI | 3. Custom protocol | 4. MCP |
|-----------|:-----------:|:------:|:------------------:|:------:|
| Keeps stateful session in one long-lived process | ✗ (per language) | ✗ (unless it becomes a daemon) | ✓ | ✓ |
| Language-neutral (no Ruby runtime on client) | ✗ | ✗ | ✓ | ✓ |
| Per-language effort for us | High (N bindings) | High (N parsers) | High (N SDKs) | **~Zero (existing SDKs)** |
| Typed/structured tool discovery | ✗ | ✗ | Build it | **Built-in** |
| Standardized / future-proof | ✗ | ✗ | ✗ (ours to own) | **✓ (industry standard)** |
| Amount of work already done in this repo | ✗ | ✗ | ✗ | **✓ (client + config + demo)** |

---

## Open Questions

1. **Tool set:** expose all ~55 primitives, or the curated 26 the step-10 test
   expects? (Leaning: ship all — discovery lets the agent see them, and the
   schemas come for free from the enum tables.)
2. **Session bootstrap:** implicit `open`+`login` on first call, or an explicit
   `connect`/`login` tool? (Leaning: explicit tool for observability, with env
   credentials as the default source.)
3. **Server implementation:** hand-roll the JSON-RPC loop (zero deps, matches
   the minimal client already written) vs. adopt a Ruby MCP server gem.
   (Leaning: hand-roll — the surface is small and it keeps the gem dependency-free
   like the rest of `mud_manager`.)
4. **Transport:** stdio only, or also streamable HTTP for remote/cloud MUDs?
   (Leaning: stdio now; HTTP is a later, additive concern.)
5. **Multi-session:** one character per server process (simplest, isolated) vs.
   one server managing many sessions by `session_id` parameter. (Leaning: one
   per process — matches the stdio "credentials by env" convention already in
   `config.rb`.)

---

## Recommended Next Steps

1. Write `bin/mud-manager` — a stdio JSON-RPC 2.0 MCP server that advertises
   the primitives as tools and drives a real `MudManager::Session`.
2. Write `lib/mud_manager/fake_mud.rb` — offline fake MUD for tests.
3. Update `mud_manager.gemspec` (`executables`, description).
4. Make the existing step-10 tests green
   (`test_mcp_client.rb`, `test_tools_mcp.rb`, `test_mcp_servers_config.rb`) —
   they already encode the desired contract.
5. Smoke-test from a **second language** (e.g. Python with the official MCP SDK)
   against the Ruby daemon — this is the proof that generic interfacing works.
