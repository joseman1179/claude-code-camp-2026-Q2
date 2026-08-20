# Generic MCP Client — Boukensha as an MCP Host (Plan)

## Goal

Move boukensha from a "built-in tools" agent to a **generic MCP client/host**:

> The agent ships **zero tools of its own**. Every tool it can call is
> discovered at runtime from an MCP server declared in `settings.yaml`. The
> agent knows what a *server* is — never what a *MUD* (or filesystem, or shell)
> is.

This is the **client-side counterpart** to `generic_interfacing.md`, which built
the *server* side (`mud_manager_mcp`). Together they complete the two-halves
split:

```
┌─────────────────────────────┐        ┌──────────────────────────────┐
│  boukensha (agent)          │  stdio │  mud_manager_mcp (server)    │
│  = generic MCP *host*       │◄──────►│  = MUD-specific MCP server   │
│  knows NOTHING about MUD    │JSON-RPC│  owns the telnet session     │
└─────────────────────────────┘        └──────────────────────────────┘
```

## Relationship to the other plans

This is plan **2** of a three-part series (the instructor's series, applied to
our repo):

| # | Plan | Concern | Status in our repo |
|---|------|---------|--------------------|
| 1 | `generic_interfacing.md` | Build the daemon (`mud_manager_mcp`) — the *server* side | ✅ done |
| 2 | **`generic_mcp_client.md`** (this) | boukensha consumes *any* MCP server — the *client* side | ✅ **already the end state of step 10** |
| 3 | `single_gem.md` | Merge the daemon into the domain gem | ⏸ deferred ("leave as-is") |

---

## Target architecture

Four pieces, none of which knows what a MUD is:

### 1. `Boukensha::Mcp::Client` — minimal MCP-over-stdio client

Location: `lib/boukensha/mcp/client.rb`

- `Client.spawn(command:, args: [], env: {})` — spawns the server subprocess
  with `Open3.popen3`.
- `initialize` — performs the handshake:
  1. `initialize` request (pins `protocolVersion: "2025-06-18"`, sends
     `clientInfo`, reads `serverInfo`),
  2. `notifications/initialized`,
  3. `tools/list` → caches `@tools`.
- `call_tool(name, arguments)` → `{ text:, error: }`. It extracts **text**
  blocks and joins them; `isError: true` is surfaced as `error: true`, never
  raised.
- `close` — closes stdin, reaps the subprocess.

The client is server-agnostic: `command` / `args` / `env` is the standard stdio
transport config, the same triple every MCP host uses.

### 2. `Boukensha::Tools::Mcp` — the generic host layer

Location: `lib/boukensha/tools/mcp.rb`

- `Tools::Mcp.register(registry, command:, args: [], env: {}, prefix: nil)` —
  spawns a client and registers its tools into any object exposing the
  `#tool` surface (a `Registry` or the `RunDSL`).
- **Prefix scoping:** `look` → `tbamud__look`. The prefix is a property of the
  server *entry* (from config), applied **agent-side** — the server still sees
  its bare name on the wire.
- **Collision detection:** two servers claiming one local name raises
  `Tools::Mcp::CollisionError` (always fatal — a config contradiction, not a
  server being unreachable).
- **Schema translation:** `to_boukensha_params` converts an MCP `inputSchema`
  into boukensha's `parameters` shape (`{ name => { type:, description: } }`),
  folding `enum` lists into the description text.
- Registers a closure per tool that calls the client and maps
  `error` → `"error: #{text}"`.

### 3. `Config#mcp_servers` — config-driven tool sourcing

Location: `lib/boukensha/config.rb`

`settings.yaml`'s `mcp_servers:` block is the **only** source of tools:

```yaml
mcp_servers:
  mud:
    command: mud-manager
    args:    [--mcp]
    prefix:  tbamud
    env:                     # stdio credentials travel by environment
      MUD_HOST:     localhost
      MUD_PORT:     4000

  filesystem:
    command:  npx
    args:     [-y, "@modelcontextprotocol/server-filesystem", /tmp]
    prefix:   fs
    required: false          # can't start? warn and carry on
```

| Key | Default | Meaning |
|-----|---------|---------|
| `command` | — | Executable to spawn (OS-resolved; nothing hunts for the binary) |
| `args` | `[]` | Its argv |
| `env` | `{}` | Extra environment (servers inherit boukensha's; these override) |
| `prefix` | none | Scopes discovered names (`fs` → `fs__read_file`) |
| `required` | `true` | `false` downgrades a spawn failure to a warning |

### 4. `Boukensha.register_mcp_servers` — the wiring

Location: `lib/boukensha.rb`

- Iterates `cfg.mcp_servers`, calling `Tools::Mcp.register` for each.
- `CollisionError` re-raises (never excused).
- Any other spawn failure: **raise** if `required`, **warn** if `required:
  false` ("optional MCP server 'X' failed to start — continuing without its
  tools").
- Returns `{ server_name => tool_count }` for the servers that came up.
- Called once from `Boukensha.run` (and `.repl`) right after the `Registry` is
  built — the agent has no tool-selection mode and no MUD argument, because it
  has no concept of a MUD.

---

## The "before → after" (what the move replaces)

The instructor's plan 2 frames this as replacing step-9's built-in tools. Our
step 10 already performed that deletion; the README documents the mapping:

| Gone | Replaced by |
|------|-------------|
| `Tools::FileSystem` (`pwd`, `read_file`, `write_file`, `search_files`, …) | a filesystem MCP server |
| `Tools::Shell` (`run_command`) | a shell MCP server of your choosing |
| `Tools::Mud` (embedded `MudManager::Session`) | the `mud-manager --mcp` daemon |
| `Tools::McpMud`, `mud:` / `working_dir:` / `allowed_commands:` / `shell_timeout:` args, `BOUKENSHA_MUD_MODE`, `mud:` in settings.yaml | one `mcp_servers:` entry |

The gemspec drops its tool dependencies (`mud_manager` went with `Tools::Mud`);
servers are separate processes that bring their own.

---

## Implementation steps (plan — not executed)

Each step maps to a concrete file, in dependency order:

1. **`lib/boukensha/mcp/client.rb`** — `Mcp::Client` (spawn → handshake →
   `tools/list` → `tools/call` → close). Status: ✅ present in step 10.
2. **`lib/boukensha/tools/mcp.rb`** — `Tools::Mcp` (register, prefix,
   collision, schema translation). Status: ✅ present.
3. **`lib/boukensha/config.rb`** — add `Config#mcp_servers` (parse
   `command`/`args`/`env`/`prefix`/`required`, apply defaults). Status: ✅ present.
4. **`lib/boukensha.rb`** — add `register_mcp_servers` and call it from
   `run`/`repl`; the agent's tool surface becomes "whatever `mcp_servers:` says".
   Status: ✅ present.
5. **Delete the built-in tools** (`tools/filesystem.rb`, `tools/shell.rb`,
   `tools/mud.rb`, `tools/mcp_mud.rb`) and their settings keys
   (`mud:`, `working_dir:`, `allowed_commands:`, `shell_timeout:`). Status: ✅
   done (only `tools/mcp.rb` remains).
6. **`boukensha.gemspec`** — drop tool dependencies. Status: ✅ done.
7. **Tests** — `test_mcp_client.rb`, `test_tools_mcp.rb`,
   `test_mcp_servers_config.rb` encode the contract (isError-as-data, prefixing,
   collision, optional-server warning, required-server raise). Status: ✅
   present (suite green at 22 runs / 65 assertions).
8. **Demo** — `examples/mcp_mud_demo.rb` (`--dry` offline path) and
   `examples/example.rb` (full run). Status: ✅ present.

**Net:** in our repo this plan is already the end state of step 10 — nothing
needs to be executed. The remaining work lives in the "Open items" below.

---

## Alignment with the instructor's plan (differences to note)

Reconstructed from the instructor's plan shared in an earlier interaction and
from `generic_interfacing.md`:

1. **The "before" state differs.** The instructor's plan 2 assumes the move
   starts from step-9's built-in tools (`Tools::FileSystem`, `Tools::Shell`,
   `Tools::Mud`, `Tools::McpMud`). Our step 10 already deleted those — so the
   "move" the instructor describes is *already complete* here.
2. **`tools/mud.rb` does not exist in our tree.** The instructor's plan maps
   the MUD surface to `tools/mud.rb`; our step 10 replaced *all* built-in tools
   with the generic `tools/mcp.rb`. There is no MUD-specific tool file in
   boukensha.
3. **Plan 3 is deferred.** The instructor's series ends with `single_gem.md`
   (merge the daemon into the domain gem). We deliberately left
   `mud_manager_mcp` as a separate gem ("leave as-is").
4. **One divergence from the instructor's tree:** we added
   `lib/boukensha/backends/deepseek.rb` (7 backends vs. the instructor's 6).
   Unrelated to MCP, but it is the only file-level difference in
   `lib/boukensha/`.

---

## Verification

```sh
# Offline, no API key, no live MUD — daemon's built-in fake MUD:
ruby week1_baseline/ruby/10_standard_tool_library/examples/mcp_mud_demo.rb --dry

# Contract tests (client, host layer, config wiring):
cd week1_baseline/ruby/10_standard_tool_library && rake test
```

Expected: `--dry` prints `26 tbamud__ tools` and dispatches `look` / `attack` /
`bad cast` through the generic layer; `rake test` is green.

---

## Open items (technical considerations, not to fix now)

Carried from the step-10 README's "Technical Considerations" — preserved here
as the plan's known-limitations ledger:

- **Session-in-use prompt unhandled:** if the MUD already has an active session
  for a character, tabMUD asks Yes/No to kill it; neither the agent nor the
  daemon handles that case yet.
- **Tool coverage:** the primitives→tools mapping may be thin for real tasks
  (mostly 1:1 with primitives).
- **Eager spawn:** every `mcp_servers:` entry costs a subprocess + handshake at
  boot, even if the LLM never calls it. Fine at two servers; revisit past that.
- **Non-text content dropped:** non-text MCP blocks (images, embedded
  resources) are discarded, yielding an empty string rather than an exception.
  No MUD tool can hit this.
- **Required-params bug:** backends advertise every listed parameter as
  required, which is wrong for third-party servers with genuinely optional
  params. Fixing means plumbing `inputSchema["required"]` through
  `Boukensha::Tool`.
- **`.boukensharc` YAML support:** step 9's `boukensha_path:` / `boukensha_dir:`
  keys must not regress when `boukensha_loader.rb` is touched in later steps
  (see `docs/plans/floating_artifacts/bounkensharc.md`).

---

## Decision summary

| Question | Decision |
|----------|----------|
| Does the agent special-case MUD? | No — it registers any server's tools via the identical path. |
| Where does MUD-specificity live? | Server side (`mud_manager_mcp`) + the agent's prompt/task (semantic), never the agent's code. |
| Prefix semantics | Applied agent-side; the server sees its bare name on the wire. |
| Collision policy | Always fatal (`CollisionError`) — never silently drop a tool. |
| Optional server policy | `required: false` → warn and continue; `required` → raise. |
| Credentials | Environment variables on the stdio transport. |
| Session | Owned entirely by the daemon; invisible to the agent behind `tools/call`. |
