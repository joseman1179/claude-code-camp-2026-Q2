# mud_manager_mcp

The `mud-manager` daemon: a thin MCP server over the `mud_manager` domain gem.

`mud_manager` owns the hard part — a **stateful, long-lived telnet session**
(`MudManager::Session`) and a table of **stateless command primitives**
(`MudManager::Primitives`). This package turns that into **tools** that an
agent in any language can call over stdio, so a Rust/Go/Java/Python bootcamper
never has to touch Ruby or telnet.

## Why a daemon, not a library

A MUD session is a persistent TCP socket. A one-shot "CLI" process can't hold
it open; the login dance and async chatter would be lost between calls. The
answer is a **long-lived process** that owns the socket, with a clean protocol
in front of it. This package implements two such protocols:

- **MCP** (JSON-RPC 2.0 over stdio) — the primary, blessed interface. Any
  MCP-capable agent SDK can `tools/list` and `tools/call` it.
- **raw JSON-line** (`--stdio-json`) — a bespoke escape hatch and teaching
  artifact.

## Usage

```sh
# MCP server (default)
mud-manager --mcp

# raw JSON-line protocol
mud-manager --stdio-json

# inspect the tool surface
mud-manager --list-tools
mud-manager --dump-spec > primitives.json
```

Credentials travel by environment (the stdio transport's standard channel):

```sh
MUD_HOST=localhost MUD_PORT=4000 MUD_NAME=Gandalf MUD_PASSWORD=secret mud-manager --mcp
```

The session is opened **lazily** on the first tool call; connect + login happen
behind the boundary and are invisible to the caller.

## Tool surface

26 tools, generated from `MudManager::Primitives` (see
`lib/mud_manager_mcp/spec.rb`): `look`, `examine`, `check`, `move`, `flee`,
`set_position`, `track`, `attack`, `skill_strike`, `consider`, `say`, `tell`,
`channel_say`, `get_item`, `drop_item`, `put_item`, `equip_item`,
`consume_item`, `cast_spell`, `use_magic_item`, `shop`, `practice`,
`save_character`, `send_raw`, plus two daemon additions: `poll` and
`mud_status`.

## Development

```sh
# run the suite (uses an in-process FakeMud — no live MUD needed)
rake test

# smoke test against the FakeMud through a real subprocess
ruby examples/boukensha_mcp_demo.rb
```

Build/install (depends on `mud_manager`):

```sh
gem build mud_manager_mcp.gemspec
gem install ./mud_manager_mcp-0.1.0.gem
```

## Layout

- `lib/mud_manager_mcp/session_pool.rb` — owns the single `MudManager::Session`
- `lib/mud_manager_mcp/spec.rb` — the 26-tool spec, generated from Primitives
- `lib/mud_manager_mcp/dispatcher.rb` — (tool, args) → (text, is_error)
- `lib/mud_manager_mcp/mcp_server.rb` — JSON-RPC 2.0 stdio server
- `lib/mud_manager_mcp/json_line_server.rb` — raw JSON-line server
- `lib/mud_manager_mcp/fake_mud.rb` — in-memory MUD for tests
- `lib/mud_manager_mcp/mcp_client.rb` — test-scoped MCP client (daemon-only)
