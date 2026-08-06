import json
import os

data_dir = "/home/ubunt22jose/dev/proyectos/claude-code-camp-2026-Q2/week0_explore/preview/data/world/wld/"

for filename in os.listdir(data_dir):
    if filename.endswith(".json"):
        with open(os.path.join(data_dir, filename), 'r') as f:
            try:
                content = f.read()
                if "Minotaur" in content:
                    print(f"Found in {filename}")
            except Exception:
                continue
