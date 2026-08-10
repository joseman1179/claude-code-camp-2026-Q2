#!/usr/bin/env python3
"""Smoke test for the Boukensha.run DSL step."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import boukensha
from boukensha import Config

os.environ.setdefault(
    "BOUKENSHA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent / ".boukensha"),
)

base_dir = str(Path(__file__).resolve().parent.parent)

print("=== BOUKENSHA Step 7: The Boukensha.run DSL ===")
print()
print(f"Config: {Config()}")
print()


def register_tools(dsl):
    @dsl.tool(
        "read_file",
        description="Read the contents of a file from disk",
        parameters={"path": {"type": "string", "description": "The file path to read"}},
    )
    def read_file(path):
        return Path(base_dir, path).read_text()

    @dsl.tool(
        "list_directory",
        description="List the files in a directory",
        parameters={"path": {"type": "string", "description": "The directory path to list"}},
    )
    def list_directory(path):
        entries = [f for f in os.listdir(Path(base_dir, path)) if not f.startswith(".")]
        return ", ".join(entries)


result = boukensha.run(
    task="Read the README.md file and summarise what this MUD player assistant framework can do.",
    tools=register_tools,
)

print()
print("=== FINAL RESPONSE ===")
print(result)
