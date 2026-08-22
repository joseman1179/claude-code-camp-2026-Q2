# Floating artifact — `~/.boukensharc` (global executable resolution)

Origin: **step 9 (`09_global_executable`)**. Introduced when boukensha was
packaged as a gem so the `boukensha` command works from anywhere. This
mechanism carries forward into every later step — any step that rewrites
`boukensha_loader.rb` or changes how tools/servers are launched must preserve
these semantics.

## What it does

`~/.boukensharc` is a YAML file with two **independent** settings:

```yaml
boukensha_path: ~/path/to/step_folder   # which implementation's lib/boukensha.rb to load
boukensha_dir:  ~/path/to/.boukensha    # where .env, settings.yaml, prompts/ live
```

Resolution priority (per setting, independently):

| Setting         | 1st priority        | 2nd priority                  | Default                          |
|-----------------|---------------------|-------------------------------|----------------------------------|
| Implementation  | `BOUKENSHA_PATH`    | `boukensha_path` in rc file   | bundled lib (the gem's own copy) |
| Runtime config  | `BOUKENSHA_DIR`     | `boukensha_dir` in rc file    | `~/.boukensha`                   |

Rules that must hold:

- YAML is parsed with `YAML.safe_load` (no aliases, no arbitrary classes).
- Legacy single-line format (a bare path string) is treated as `boukensha_path`.
- rc paths are expanded **relative to the rc file's directory**
  (`File.expand_path(path, File.dirname(rc_file))`).
- `BOUKENSHA_DIR` is exported into `ENV` *before* the selected step's code is
  required, so `Config` picks it up when it resolves its settings dir.
- The gem is a wrapper + default: it never copies or symlinks step code; it
  only knows where to look.

## Carry-forward obligations

Any later step that touches `boukensha_loader.rb` must keep: YAML Hash +
legacy String rc support, env-over-rc precedence, independent resolution of
path/dir, and the `BOUKENSHA_DIR` export before `require`. The loader is
**shared infrastructure**, not per-step teaching material — do not "simplify"
it while porting a step.

## Incidents (record of breakages)

### 1. Step 10 loader rewrite dropped step-9 rc support

Step 10's initial rewrite silently mis-parsed step-9-era rc files: it dropped
the `boukensha_dir:` key and the legacy single-line-path backward compat, so a
step-9 `~/.boukensharc` stopped pointing at the right config dir. Restored by
copying step-9's loader behavior verbatim.

### 2. Step 10 MCP `command:` is resolved by the OS PATH, not by boukensharc

Step 10 pivoted boukensha to a generic MCP host: it ships **zero tools** and
discovers every tool at runtime from `settings.yaml`'s `mcp_servers:` block:

```yaml
mcp_servers:
  mud:
    command: mud-manager      # resolved by the OS against PATH (or cwd if it contains a slash)
    args:    [--mcp]
    prefix:  tbamud
    required: false
```

**Critical semantic gap:** the loader's path-expansion (`expand_rc_path`)
applies to `boukensha_path` / `boukensha_dir` **only**. It does **not** touch
`mcp_servers.*.command`. The MCP client spawns the command via
`Open3.popen3(env, command, *args)` — OS `execvp` semantics:

- a bare name (`mud-manager`) → looked up on `$PATH`
- a path containing `/` → resolved against the shell's cwd

So a bare `command: mud-manager` only works if the daemon is **installed** on
PATH. Building the gem is not enough; installing it (which places
`bin/mud-manager` in the gem bin dir) is required — and since the single-gem
merge (see `docs/plans/mud_manager/single_gem.md`), that gem is `mud_manager`.

**What actually happened:** the daemon was built at
`week1_baseline/mud_manager_mcp/bin/mud-manager` but its gem was never
`gem install`ed, so `mud-manager` was not on PATH. Result at boot:

```
optional MCP server 'mud' failed to start: No such file or directory - mud-manager — continuing without its tools
```

Because the entry is `required: false`, this is a **warning, not a fatal
error** — boukensha continues but registers **zero MUD tools**. The agent runs
but cannot play the MUD.

**Why every earlier "works" check missed it:** all green checks ran
`examples/mcp_mud_demo.rb --dry`, which hardcodes the daemon path and spawns it
directly (`command: RbConfig.ruby, args: [daemon, "--mcp"]`) — bypassing PATH
resolution entirely. A demo that hardcodes a path proves the *code* works, not
that the *deployment* (executable on PATH) is done.

**Fix (for reference):**

```bash
# The daemon now ships inside the mud_manager gem (single_gem.md):
cd week0_explore/mud_manager
gem build mud_manager.gemspec
gem install mud_manager-0.2.0.gem   # installs the domain lib AND the mud-manager binary
```

## Guidance for future steps

- Treat `boukensha_loader.rb` as shared infrastructure. Preserve its rc
  semantics across steps; if a step changes them, record it here.
- When a step changes how tools/servers are launched, explicitly answer: is
  `command:` resolved against PATH, cwd, or `boukensha_dir`? Then verify the
  deployment requirement (installed vs. relative path).
- "Built" ≠ "installed": a gem whose `bin/` executable is referenced by bare
  name must be `gem install`ed.
- `required: false` makes a missing server a *silent* degradation. "The command
  runs" is not proof that tools registered — verify via the `Servers:` /
  `Config:` output or a tool listing, not just a clean exit.
- The `--dry` demo (`mcp_mud_demo.rb`) intentionally hardcodes the daemon path;
  do not treat its green output as proof that PATH resolution works.
