#!/usr/bin/env python3
"""Smoke test for the Boukensha REPL loop step."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import boukensha

os.environ.setdefault(
    "BOUKENSHA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent / ".boukensha"),
)

base_dir = str(Path(__file__).resolve().parent.parent)

print("=== BOUKENSHA Step 8: The REPL Loop ===")
print()


def register_tools(dsl):
    @dsl.tool(
        "read_file",
        description="Read the contents of a file from disk",
        parameters={"path": {"type": "string", "description": "File path (relative to the working directory)"}},
    )
    def read_file(path):
        return Path(base_dir, path).read_text()

    @dsl.tool(
        "list_directory",
        description="List the files in a directory",
        parameters={"path": {"type": "string", "description": "Directory path (relative to the working directory, or '.' for root)"}},
    )
    def list_directory(path):
        entries = sorted(
            f for f in os.listdir(Path(base_dir, path)) if not f.startswith(".")
        )
        return ", ".join(entries)


boukensha.repl(tools=register_tools)
