# Single Gem — merge `mud_manager_mcp` into `mud_manager` (Plan)

## Goal

One gem — **`mud_manager`** — ships both the domain (a stateful telnet
`Session` + stateless `Primitives`) **and** the MCP daemon, exposing **one
binary**: `mud-manager`. The two-gem split disappears: `gem install
mud_manager` puts `mud-manager` on PATH, end of story.

## Why (the problem this solves)

1. **Deployment trap (floating artifact incident #2).** Today `mud-manager` is
   only on PATH if `mud_manager_mcp` is installed, but the daemon gem was never
   installed, so `boukensha` boots with *"optional MCP server 'mud' failed to
   start: No such file or directory - mud-manager"*. A single gem collapses the
   two install steps into one and removes the "forgot to install the second
   gem" failure mode.
2. **The split was always labeled intermediate.** `mud_manager_mcp.gemspec`
   says *"the eventual target is a single gem; this split is the intermediate
   state."* This plan is that eventual target.
3. **Redundant packaging.** `mud_manager_mcp` is ~11 thin files that exist only
   to wrap `MudManager::Session` + `MudManager::Primitives` behind MCP. They
   belong in the same package as the thing they wrap.

## Current state

| Package | Location | Gem | Ships |
|---|---|---|---|
| Domain | `week0_explore/mud_manager/` | `mud_manager` 0.1.0 | lib only (`Session`, `Primitives`). **No bin, no Rakefile, no tests.** |
| Daemon | `week1_baseline/mud_manager_mcp/` | `mud_manager_mcp` 0.1.0 (depends on `mud_manager`) | `bin/mud-manager`, 11 `MudManagerMcp::*` files, `primitives.json`, 5 test files, `Rakefile` |

Coupling (`mud_manager_mcp` → `mud_manager`), all resolved via `require
"mud_manager"` / `MudManager::`:

- `lib/mud_manager_mcp.rb`, `session_pool.rb`, `spec.rb` — `require "mud_manager"`
- `config.rb` — `MudManager::Session::DEFAULT_HOST` / `DEFAULT_PORT`
- `session_pool.rb` — `MudManager::Session` (new/open/login/drain/send_command/read_until_prompt/close)
- `spec.rb` — `P = MudManager::Primitives` (all enums + builders)
- `dispatcher.rb`, `json_line_server.rb` — `MudManager::Session::{ConnectionError,LoginError,Timeout}`
- `bin/mud-manager` — `require "mud_manager"` with a hardcoded `week0_explore` fallback
- `test/helper.rb` — `MUD_MANAGER_LIB` hardcoded to `week0_explore/mud_manager/lib`

## Target architecture (after)

```
week0_explore/mud_manager/                 gem: mud_manager 0.2.0 — one gem, one binary
├── bin/
│   └── mud-manager                        (moved from mud_manager_mcp; load path simplified)
├── lib/
│   ├── mud_manager.rb                     (domain entry — unchanged)
│   ├── mud_manager/
│   │   ├── primitives.rb                  (unchanged)
│   │   └── session.rb                     (unchanged)
│   ├── mud_manager_mcp.rb                 (compat entry — kept so `require "mud_manager_mcp"` still works)
│   └── mud_manager_mcp/
│       ├── config.rb  session_pool.rb  spec.rb  dispatcher.rb  tool_spec.rb
│       ├── mcp_server.rb  json_line_server.rb  mcp_client.rb  fake_mud.rb
│       ├── errors.rb  version.rb
├── primitives.json                        (moved)
├── Rakefile                               (moved; :spec task re-pointed)
├── test/                                  (moved: 5 files, 22 tests)
├── examples/                              (live_session_test.rb, simple.rb, + boukensha_mcp_demo.rb)
└── mud_manager.gemspec                    (gains bindir/executables + files)

week1_baseline/mud_manager_mcp/            (deleted after verification)
```

## Decisions

- **D1 — namespace: keep `MudManagerMcp::`** (recommended). Zero churn inside
  the daemon files and in step 10's `MudManagerMcp::FakeMud` / `require
  "mud_manager_mcp/fake_mud"` references. The merged gem simply ships *both*
  entry points (`mud_manager.rb` and `mud_manager_mcp.rb`); Ruby's require
  dedupes the internal `require "mud_manager"`. Renaming to `MudManager::Mcp::`
  would be cleaner but is pure churn with no behavioral gain — defer it.
- **D2 — gem name: keep `mud_manager`.** The daemon is bundled *into* the
  domain gem, per the goal ("bundle the MCP server into the actual mud
  manager").
- **D3 — version: bump to `0.2.0`.** The installed `mud_manager` 0.1.0 has no
  binary; 0.2.0 makes "the build that ships `mud-manager`" unmistakable. Bump
  `lib/mud_manager_mcp/version.rb` and regenerate `primitives.json` (it embeds
  `"version": "0.1.0"`). Note: this leaves two version literals (gemspec +
  version.rb) — see Open items.
- **D4 — retire the separate gem: delete `week1_baseline/mud_manager_mcp/`**
  after the merge is verified. Git history preserves it. (Alternative: leave a
  one-line README stub pointing at `week0_explore/mud_manager` — not
  recommended; two sources of truth invite drift.)
- **D5 — compatibility entry point: ship `lib/mud_manager_mcp.rb`** so existing
  `require "mud_manager_mcp"` and `require "mud_manager_mcp/fake_mud"` keep
  working from the single gem.

## Implementation steps (plan — not executed)

### Phase A — merge files into the domain gem

1. Copy the daemon's lib tree into the domain gem:
   `week1_baseline/mud_manager_mcp/lib/*` → `week0_explore/mud_manager/lib/`
   (this lands `lib/mud_manager_mcp.rb` + `lib/mud_manager_mcp/*.rb`).
2. Move `week1_baseline/mud_manager_mcp/bin/mud-manager` →
   `week0_explore/mud_manager/bin/mud-manager`.
3. Move `primitives.json`, `Rakefile`, and `test/` (5 files) →
   `week0_explore/mud_manager/`.
4. Move `examples/boukensha_mcp_demo.rb` → `week0_explore/mud_manager/examples/`
   (joins the existing `live_session_test.rb` / `simple.rb`).

### Phase B — fix self-references inside the merged gem

5. **`bin/mud-manager`** — drop the `week0_explore` fallback; the daemon is now
   in the same gem:
   ```ruby
   $LOAD_PATH.unshift(File.expand_path("../lib", __dir__))
   require "mud_manager_mcp"   # internally requires "mud_manager"
   ```
6. **`test/helper.rb`** — `MUD_MANAGER_MCP_ROOT = File.expand_path("..", __dir__)`
   already resolves correctly after the move. Replace the hardcoded
   `MUD_MANAGER_LIB = File.expand_path("../../../week0_explore/mud_manager/lib", __dir__)`
   with `MUD_MANAGER_LIB = MUD_MANAGER_MCP_LIB` (same gem now).
7. **`Rakefile`** — the `:spec` task already runs `bin/mud-manager --dump-spec`
   relative to the gem root; no change needed beyond what the move gives it.
8. **`mud_manager.gemspec`** — add the daemon surface + bump version:
   ```ruby
   spec.version     = "0.2.0"
   spec.files       = Dir["lib/**/*.rb"] + ["bin/mud-manager", "primitives.json", "README.md"]
   spec.bindir      = "bin"
   spec.executables = ["mud-manager"]
   ```
9. **`lib/mud_manager_mcp/version.rb`** — `VERSION = "0.2.0"`; regenerate
   `primitives.json` (`rake spec`).

### Phase C — update consumers (step 10)

10. **`week1_baseline/ruby/10_standard_tool_library/test/helper.rb`** — repoint
    the three constants from `../../../mud_manager_mcp` to
    `../../../../week0_explore/mud_manager`:
    ```ruby
    MUD_MANAGER_ROOT = File.expand_path("../../../../week0_explore/mud_manager", __dir__)
    MUD_MANAGER_BIN  = File.join(MUD_MANAGER_ROOT, "bin", "mud-manager")
    MUD_MANAGER_LIB  = File.join(MUD_MANAGER_ROOT, "lib")
    ```
    (`require "mud_manager_mcp/fake_mud"` and `MudManagerMcp::FakeMud` stay
    unchanged — the file still exists at `<lib>/mud_manager_mcp/fake_mud.rb`.)
11. **`week1_baseline/ruby/10_standard_tool_library/examples/mcp_mud_demo.rb`** —
    repoint the load path and daemon path the same way:
    `"../../../mud_manager_mcp/lib"` → `"../../../../week0_explore/mud_manager/lib"`,
    `"../../../mud_manager_mcp/bin/mud-manager"` → `"../../../../week0_explore/mud_manager/bin/mud-manager"`.
12. **`week1_baseline/ruby/10_standard_tool_library/README.md`** — update the
    "What went away" table note (`mud_manager` is no longer a separate
    dependency; the daemon ships in it) and the technical-considerations bullet
    that mentions the split.
13. **`.boukensha/settings.yaml`** — correct the stale `mud:` comment (it
    claims `required` defaults loud, but the entry sets `required: false`), and
    the `mud-manager` comment now becomes true once `mud_manager` 0.2.0 is
    installed.

### Phase D — retire the separate gem

14. Delete `week1_baseline/mud_manager_mcp/` (after Phase F passes).

### Phase E — docs

15. `docs/plans/mud_manager/generic_mcp_client.md` — flip plan-3 status from
    "⏸ deferred" to "✅ done (see `single_gem.md`)".
16. `docs/plans/floating_artifacts/boukensharc.md` — update incident #2's fix:
    `gem install mud_manager` (0.2.0) now ships `mud-manager`, replacing the
    `gem install mud_manager_mcp` instruction.
17. `week0_explore/mud_manager/README.md` — add the daemon usage section
    (`mud-manager --mcp` / `--list-tools` / `--dump-spec`, credentials by
    environment) and the "one gem, one binary" note.

## Verification

```sh
# 1. Build + install the single gem (from week0_explore/mud_manager)
cd week0_explore/mud_manager
gem build mud_manager.gemspec
gem install ./mud_manager-0.2.0.gem
which mud-manager                       # => .../bin/mud-manager  (the fix)

# 2. The binary works standalone
mud-manager --list-tools                # => 26 names
mud-manager --dump-spec                 # => primitives.json, version 0.2.0

# 3. Merged suite green
rake test                               # => 22 runs, 0 failures/errors

# 4. Smoke test through a real subprocess
ruby examples/boukensha_mcp_demo.rb     # => "[dry run OK — daemon + FakeMud working]"

# 5. Step 10 still green against the merged gem
cd week1_baseline/ruby/10_standard_tool_library
rake test                               # => 22 runs, 65 assertions, 0 failures

# 6. Step 10 dry run still green
ruby examples/mcp_mud_demo.rb --dry     # => 26 tbamud__ tools, "[dry run OK]"

# 7. The original symptom is gone (global boukensha now finds mud-manager)
boukensha                               # => Servers: mud, filesystem (no "failed to start" for mud)

# 8. Cleanup
gem uninstall mud_manager_mcp -a        # (was never installed, but sweep it)
```

## Open items / risks

- **Two version literals** (`gemspec` + `version.rb`) can drift. Acceptable for
  now; a single `MudManager::VERSION` constant is a possible follow-up.
- **Location: the merged gem lands in `week0_explore/`**, while the daemon
  lived in `week1_baseline/`. That is intentional (the domain gem is the "real"
  home), but flag it so future steps know the daemon is now a week-0 artifact
  that week-1 steps consume — not a week-1 artifact.
- **Installed `mud_manager` 0.1.0 has no binary.** The 0.2.0 install must
  happen (or `gem uninstall mud_manager` + reinstall) or `mud-manager` stays
  off PATH. The old 0.1.0 `.gem` file in `week0_explore/mud_manager/` should be
  removed or replaced by the 0.2.0 build.
- **`mcp_client.rb` stays test-scoped.** It is the daemon's self-contained
  test client (mirrors `Boukensha::Mcp::Client`); the merge doesn't change
  that, but two copies now live in two gems — keep them intentionally separate
  (boukensha's is canonical for boukensha; the daemon must not depend on
  boukensha).
