#!/usr/bin/env python3
"""Smoke test for the Boukensha configuration port."""

import os
import sys
from pathlib import Path

# Ensure the package is importable when run from this directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from boukensha import Config, Player

# Override the config directory so the example works from the repo root.
# In real usage a user's ~/.boukensha is picked up automatically.
os.environ.setdefault(
    "BOUKENSHA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent / ".boukensha"),
)

config = Config()
player_settings = config.tasks("player")

print("=== Boukensha Step 0: Configuration ===")
print()
print(f"Config dir:     {config.dir}")
print(f"Tasks:          {','.join(config.tasks().keys())}")
print()
print("-- player task --")
print(f"Provider:       {Player.provider(player_settings)}")
print(f"Model:          {Player.model(player_settings)}")
print(f"Prompt override?{Player.prompt_override(player_settings, 'system')}")
sys_prompt = Player.system_prompt(
    player_settings,
    user_prompts_dir=config.user_prompts_dir,
    default_prompts_dir=str(Config.PROMPTS_DIR),
)
print(f"System prompt:  {sys_prompt[:60] if sys_prompt else 'None'}...")
print()
print(f"MUD host:       {config.mud_host}:{config.mud_port}")
print(f"MUD user:       {config.mud_username}")
print()
print(f"API key set?    {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
print()
print(config)
