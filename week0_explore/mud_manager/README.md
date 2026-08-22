# MudManager

The MudManager is a single gem that ships both the domain and the MCP daemon:

- manages long-lived telnet sessions (`MudManager::Session`)
- manages the multi-step process of logging back in
- provides generic primitives for MUD commands (`MudManager::Primitives`)
- exposes those primitives as MCP tools over stdio via the `mud-manager` binary

One gem, one binary.

## Build the Gem

From this directory:

```sh
gem build mud_manager.gemspec
gem install ./mud_manager-0.2.0.gem
```

This installs the `mud_manager` library **and** the `mud-manager` executable on
your PATH.

## The daemon

```sh
mud-manager --mcp          # MCP (JSON-RPC 2.0) server over stdio — the default
mud-manager --stdio-json   # raw JSON-line protocol (escape hatch)
mud-manager --list-tools   # print the 26 advertised tools
mud-manager --dump-spec    # print the primitives.json spec
```

Credentials travel by environment (the stdio transport's standard channel):

```sh
MUD_HOST=localhost MUD_PORT=4000 MUD_NAME=Gandalf MUD_PASSWORD=secret mud-manager --mcp
```

The session opens lazily on the first tool call; connect + login happen behind
the boundary.

## Uninstall

```sh
gem uninstall mud_manager
```

## Tests

```sh
rake test   # 22 runs — uses an in-process FakeMud, no live MUD needed
```

## Examples

Test the live session:

```sh
MUD_NAME=YourCharacterName MUD_PASSWORD=yourpassword ruby examples/live_session_test.rb
```

Smoke-test the daemon end-to-end (spawns a FakeMud + the daemon subprocess):

```sh
ruby examples/boukensha_mcp_demo.rb
```
