While working through the steps there are some major changes we need to carry
forward for future steps.

Artifacts:
 - boukensharc.md — the `~/.boukensharc` global-executable mechanism (step 9)
   and its carry-forward rules. Records two incidents: (1) step 10's loader
   rewrite silently broke step-9 rc parsing; (2) step 10's MCP `command:` is
   resolved by the OS PATH (not `boukensha_dir`), so `mud-manager` must be
   installed via `gem install mud_manager` (the single merged gem).
